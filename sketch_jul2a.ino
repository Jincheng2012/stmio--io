/*
  STM32F103C8T6 I/O 扩展器 (v6.0)
  功能: 开放除保留引脚及PB2外的所有GPIO，支持动态模式切换
  通信: USB 虚拟串口 (CDC)，波特率固定 115200 8N1
  命令: SET_DO, GET_DI, GET_ADC, SET_PWM, SET_LED, SET_MODE, HELP
  注意: PB2 已禁用 (BOOT1 风险)
*/

#include <Arduino.h>

// ==================== 引脚可用性定义 ====================
// 所有可用的 GPIO 引脚（排除保留引脚和 PB2）
const int availablePins[] = {
  PA0, PA1, PA2, PA3, PA4, PA5, PA6, PA7, PA8, PA9, PA10,
  PB0, PB1, // PB2 已移除
  PB3, PB4, PB5, PB6, PB7, PB8, PB9, PB10, PB11, PB12, PB13, PB14, PB15,
  PC13   // 板载 LED
};
const int numPins = sizeof(availablePins) / sizeof(availablePins[0]);

// 硬件PWM支持引脚列表
const int pwmPins[] = {
  PA0, PA1, PA2, PA3, PA6, PA7, PA8, PA9, PA10, PB0, PB1
};
const int numPwmPins = sizeof(pwmPins) / sizeof(pwmPins[0]);

// ADC支持引脚列表
const int adcPins[] = {
  PA0, PA1, PA2, PA3, PA4, PA5, PA6, PA7, PB0, PB1
};
const int numAdcPins = sizeof(adcPins) / sizeof(adcPins[0]);

// ==================== 串口缓冲区 ====================
const byte BUFFER_SIZE = 32;
char serialBuffer[BUFFER_SIZE];
byte bufferIndex = 0;

// ==================== 函数声明 ====================
void processCommand(char* cmd);
void printHelp(void);
void serialPrintln(const String& s);
int parsePin(const String& pinStr);
bool isPwmPin(int pin);
bool isAdcPin(int pin);

// ==================== 初始化 ====================
void setup() {
  // 1. 初始化所有可用引脚为输入模式
  for (int i = 0; i < numPins; i++) {
    pinMode(availablePins[i], INPUT);
  }

  // 2. 初始化 LED 引脚 (PC13) 为输出，默认熄灭
  pinMode(PC13, OUTPUT);
  digitalWrite(PC13, HIGH); // 低电平点亮，高电平熄灭

  // 3. 初始化 USB CDC 串口，波特率固定 115200
  Serial.begin(115200);
  while (!Serial) { ; }

  // 4. 启动信息
  serialPrintln("STM32F103 I/O Expander v6.0 (115200 8N1)");
  serialPrintln("Type 'HELP' for commands.");
}

// ==================== 主循环 ====================
void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (bufferIndex > 0) {
        serialBuffer[bufferIndex] = '\0';
        processCommand(serialBuffer);
        bufferIndex = 0;
        memset(serialBuffer, 0, BUFFER_SIZE);
      }
    } else {
      if (bufferIndex < BUFFER_SIZE - 1) {
        serialBuffer[bufferIndex++] = c;
      } else {
        bufferIndex = 0;
        serialPrintln("ERR: Command too long.");
      }
    }
  }
}

// ==================== 命令处理 ====================
void processCommand(char* cmd) {
  String command = String(cmd);
  command.trim();
  command.toUpperCase();

  if (command.equals("HELP")) {
    printHelp();
    return;
  }

  // --- SET_DO <PIN> <0/1> ---
  if (command.startsWith("SET_DO ")) {
    String rest = command.substring(6);
    rest.trim();
    int firstSpace = rest.indexOf(' ');
    if (firstSpace == -1) {
      serialPrintln("ERR: Missing arguments. Use: SET_DO <PIN> <0/1>");
      return;
    }
    String pinStr = rest.substring(0, firstSpace);
    String valStr = rest.substring(firstSpace + 1);
    valStr.trim();
    int pin = parsePin(pinStr);
    if (pin == -1) {
      serialPrintln("ERR: Invalid pin name. Use format like PA0, PB1, PC13.");
      return;
    }
    pinMode(pin, OUTPUT);
    if (valStr.equals("1")) {
      digitalWrite(pin, HIGH);
      serialPrintln("OK: " + pinStr + " = HIGH");
    } else if (valStr.equals("0")) {
      digitalWrite(pin, LOW);
      serialPrintln("OK: " + pinStr + " = LOW");
    } else {
      serialPrintln("ERR: Value must be 0 or 1.");
    }
    return;
  }

  // --- GET_DI <PIN> ---
  if (command.startsWith("GET_DI ")) {
    String pinStr = command.substring(6);
    pinStr.trim();
    int pin = parsePin(pinStr);
    if (pin == -1) {
      serialPrintln("ERR: Invalid pin name. Use format like PA0, PB1, PC13.");
      return;
    }
    pinMode(pin, INPUT_PULLUP);
    int val = digitalRead(pin);
    serialPrintln("OK: " + pinStr + " = " + String(val));
    return;
  }

  // --- GET_ADC <PIN> ---
  if (command.startsWith("GET_ADC ")) {
    String pinStr = command.substring(7);
    pinStr.trim();
    int pin = parsePin(pinStr);
    if (pin == -1) {
      serialPrintln("ERR: Invalid pin name. Use format like PA0, PB1.");
      return;
    }
    if (!isAdcPin(pin)) {
      serialPrintln("NOT SUPPORT FOR ADC ON " + pinStr);
      return;
    }
    pinMode(pin, INPUT_ANALOG);
    int val = analogRead(pin);
    serialPrintln("OK: " + pinStr + " = " + String(val));
    return;
  }

  // --- SET_PWM <PIN> <0-255> ---
  if (command.startsWith("SET_PWM ")) {
    String rest = command.substring(7);
    rest.trim();
    int firstSpace = rest.indexOf(' ');
    if (firstSpace == -1) {
      serialPrintln("ERR: Missing arguments. Use: SET_PWM <PIN> <0-255>");
      return;
    }
    String pinStr = rest.substring(0, firstSpace);
    String valStr = rest.substring(firstSpace + 1);
    valStr.trim();
    int pin = parsePin(pinStr);
    if (pin == -1) {
      serialPrintln("ERR: Invalid pin name. Use format like PA0, PB1.");
      return;
    }
    if (!isPwmPin(pin)) {
      serialPrintln("NOT SUPPORT FOR PWM ON " + pinStr);
      return;
    }
    int pwmVal = valStr.toInt();
    if (pwmVal < 0 || pwmVal > 255) {
      serialPrintln("ERR: PWM value must be 0-255.");
      return;
    }
    analogWrite(pin, pwmVal);
    serialPrintln("OK: " + pinStr + " PWM = " + String(pwmVal));
    return;
  }

  // --- SET_LED <0/1> ---
  if (command.startsWith("SET_LED ")) {
    String valStr = command.substring(7);
    valStr.trim();
    int val = valStr.toInt();
    if (val != 0 && val != 1) {
      serialPrintln("ERR: LED value must be 0 (off) or 1 (on).");
      return;
    }
    digitalWrite(PC13, val ? LOW : HIGH);
    serialPrintln("OK: LED = " + String(val));
    return;
  }

  // --- SET_MODE <PIN> <MODE> ---
  if (command.startsWith("SET_MODE ")) {
    String rest = command.substring(8);
    rest.trim();
    int firstSpace = rest.indexOf(' ');
    if (firstSpace == -1) {
      serialPrintln("ERR: Missing arguments. Use: SET_MODE <PIN> <MODE>");
      return;
    }
    String pinStr = rest.substring(0, firstSpace);
    String modeStr = rest.substring(firstSpace + 1);
    modeStr.trim();
    int pin = parsePin(pinStr);
    if (pin == -1) {
      serialPrintln("ERR: Invalid pin name. Use format like PA0, PB1.");
      return;
    }

    if (modeStr.equals("ADC")) {
      if (!isAdcPin(pin)) {
        serialPrintln("NOT SUPPORT FOR ADC ON " + pinStr);
        return;
      }
      pinMode(pin, INPUT_ANALOG);
      serialPrintln("OK: " + pinStr + " mode = ADC");
    } else if (modeStr.equals("PWM")) {
      if (!isPwmPin(pin)) {
        serialPrintln("NOT SUPPORT FOR PWM ON " + pinStr);
        return;
      }
      pinMode(pin, OUTPUT);
      serialPrintln("OK: " + pinStr + " mode = PWM (use SET_PWM to set duty)");
    } else if (modeStr.equals("INPUT")) {
      pinMode(pin, INPUT);
      serialPrintln("OK: " + pinStr + " mode = INPUT");
    } else if (modeStr.equals("INPUT_PULLUP")) {
      pinMode(pin, INPUT_PULLUP);
      serialPrintln("OK: " + pinStr + " mode = INPUT_PULLUP");
    } else if (modeStr.equals("INPUT_PULLDOWN")) {
      pinMode(pin, INPUT_PULLDOWN);
      serialPrintln("OK: " + pinStr + " mode = INPUT_PULLDOWN");
    } else if (modeStr.equals("OUTPUT")) {
      pinMode(pin, OUTPUT);
      serialPrintln("OK: " + pinStr + " mode = OUTPUT");
    } else {
      serialPrintln("ERR: Invalid mode. Supported: INPUT, INPUT_PULLUP, INPUT_PULLDOWN, OUTPUT, PWM, ADC");
    }
    return;
  }

  serialPrintln("ERR: Unknown command. Type 'HELP' for list.");
}

// ==================== 引脚解析函数 ====================
int parsePin(const String& pinStr) {
  String s = pinStr;
  s.trim();
  s.toUpperCase();

  int portIdx = -1;
  for (int i = 0; i < s.length(); i++) {
    char ch = s.charAt(i);
    if (ch == 'A' || ch == 'B' || ch == 'C') {
      portIdx = i;
      break;
    }
  }
  if (portIdx == -1) return -1;

  char port = s.charAt(portIdx);
  String numStr = s.substring(portIdx + 1);
  int pinNum = numStr.toInt();
  if (pinNum < 0 || pinNum > 15) return -1;

  switch (port) {
    case 'A': return PA0 + pinNum;
    case 'B': 
      // 排除 PB2
      if (pinNum == 2) return -1;
      return PB0 + pinNum;
    case 'C':
      if (pinNum == 13) return PC13;
      return -1;
    default: return -1;
  }
}

bool isPwmPin(int pin) {
  for (int i = 0; i < numPwmPins; i++) {
    if (pwmPins[i] == pin) return true;
  }
  return false;
}

bool isAdcPin(int pin) {
  for (int i = 0; i < numAdcPins; i++) {
    if (adcPins[i] == pin) return true;
  }
  return false;
}

void printHelp(void) {
  serialPrintln("=== STM32F103 I/O Expander Commands ===");
  serialPrintln("SET_DO <PIN> <0/1>     - Set digital output");
  serialPrintln("GET_DI <PIN>           - Read digital input");
  serialPrintln("GET_ADC <PIN>          - Read analog input (0-4095)");
  serialPrintln("SET_PWM <PIN> <0-255>  - Set hardware PWM duty");
  serialPrintln("SET_LED <0/1>          - Turn PC13 LED ON/OFF");
  serialPrintln("SET_MODE <PIN> <MODE>  - Change pin mode");
  serialPrintln("  MODEs: INPUT, INPUT_PULLUP, INPUT_PULLDOWN, OUTPUT, PWM, ADC");
  serialPrintln("HELP                   - Show this help");
  serialPrintln("");
  serialPrintln("Available pins: PA0-PA10, PB0-PB1, PB3-PB15, PC13");
  serialPrintln("PB2 is DISABLED (BOOT1 risk)");
  serialPrintln("ADC on: PA0-PA7, PB0-PB1");
  serialPrintln("PWM on: PA0-PA3, PA6-PA10, PB0-PB1");
  serialPrintln("Reserved: PA11,PA12(USB), PA13,PA14(SWD), PD0,PD1(HSE), PC14,PC15(LSE)");
  serialPrintln("==========================================");
}

void serialPrintln(const String& s) {
  Serial.println(s);
}