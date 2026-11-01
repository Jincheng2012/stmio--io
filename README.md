## 📖 完整用户手册（v6.0）

### 1. 概述
本固件将 STM32F103C8/C6 变成一个通过 USB 虚拟串口控制的 I/O 扩展器，支持 27 个可用引脚（PB2 已禁用），每个引脚可动态配置为数字输入/输出、ADC 或硬件 PWM。板载 PC13 LED 可通过 `SET_LED` 命令开关。

### 2. 硬件说明
- **芯片**：STM32F103C8T6（64KB Flash）或 C6T6（32KB Flash），两者引脚兼容。
- **保留引脚（不可用）**：`PA11`(USB_DM), `PA12`(USB_DP), `PA13`(SWDIO), `PA14`(SWCLK), `PD0/PD1`(HSE晶振), `PC14/PC15`(LSE晶振), `NRST`(复位), 电源引脚。
- **禁用引脚**：`PB2`（BOOT1，多数开发板有上下拉，误操作可能影响启动或损坏芯片）。
- **可用引脚（27个）**：`PA0~PA10`, `PB0~PB1`, `PB3~PB15`, `PC13`。
- **PC13 LED**：低电平点亮，高电平熄灭，已串联限流电阻（开发板默认）。

### 3. USB 虚拟串口配置
- **驱动**：Windows 10/11 自动识别；Win7 需安装 ST 虚拟串口驱动；Linux/macOS 免驱。
- **连接**：设备插 USB 后，在设备管理器或 `/dev/` 下看到 COM 口。
- **串口参数（必须严格匹配）**：
  - **波特率**：`115200`
  - **数据位**：`8`
  - **停止位**：`1`
  - **校验位**：`无`
  - **流控**：`无`
- **说明**：固件固定使用 115200，使用其他波特率将无法通信。

### 4. 命令集（不区分大小写，以 `\n` 或 `\r\n` 结尾）
| 命令 | 参数 | 功能 | 示例 |
|------|------|------|------|
| `SET_DO` | `<引脚> <0/1>` | 设置引脚输出电平 | `SET_DO PA0 1` |
| `GET_DI` | `<引脚>` | 读取引脚数字输入（0/1） | `GET_DI PB10` |
| `GET_ADC` | `<引脚>` | 读取 ADC 值（0~4095，仅支持 ADC 引脚） | `GET_ADC PA1` |
| `SET_PWM` | `<引脚> <0-255>` | 设置 PWM 占空比（仅支持硬件 PWM 引脚） | `SET_PWM PA8 128` |
| `SET_LED` | `<0/1>` | 控制 PC13 LED（1=亮，0=灭） | `SET_LED 1` |
| `SET_MODE` | `<引脚> <模式>` | 切换引脚模式（见下文） | `SET_MODE PB0 OUTPUT` |
| `HELP` | 无 | 显示帮助 | `HELP` |

**支持的模式**：`INPUT`, `INPUT_PULLUP`, `INPUT_PULLDOWN`, `OUTPUT`, `PWM`, `ADC`

**错误返回**：`ERR: ...` 或 `NOT SUPPORT FOR ... ON ...`

### 5. 每个引脚的功能详细描述（按引脚分组）

#### 5.1 PA0 ~ PA7
- **PA0**：支持数字输入/输出，支持12位ADC（通道0），支持硬件PWM（TIM2_CH1）。
- **PA1**：支持数字输入/输出，支持12位ADC（通道1），支持硬件PWM（TIM2_CH2）。
- **PA2**：支持数字输入/输出，支持12位ADC（通道2），支持硬件PWM（TIM2_CH3）。
- **PA3**：支持数字输入/输出，支持12位ADC（通道3），支持硬件PWM（TIM2_CH4）。
- **PA4**：支持数字输入/输出，支持12位ADC（通道4），不支持硬件PWM。
- **PA5**：支持数字输入/输出，支持12位ADC（通道5），不支持硬件PWM。
- **PA6**：支持数字输入/输出，支持12位ADC（通道6），支持硬件PWM（TIM3_CH1）。
- **PA7**：支持数字输入/输出，支持12位ADC（通道7），支持硬件PWM（TIM3_CH2）。

#### 5.2 PA8 ~ PA10
- **PA8**：支持数字输入/输出，不支持ADC，支持硬件PWM（TIM1_CH1）。
- **PA9**：支持数字输入/输出，不支持ADC，支持硬件PWM（TIM1_CH2）。
- **PA10**：支持数字输入/输出，不支持ADC，支持硬件PWM（TIM1_CH3）。

#### 5.3 PB0 ~ PB1
- **PB0**：支持数字输入/输出，支持12位ADC（通道8），支持硬件PWM（TIM3_CH3）。
- **PB1**：支持数字输入/输出，支持12位ADC（通道9），支持硬件PWM（TIM3_CH4）。

#### 5.4 PB3 ~ PB15（不含PB2）
- **PB3**：支持数字输入/输出，不支持ADC，不支持硬件PWM（注：此引脚同时为JTDO/SPI，但可作为GPIO）。
- **PB4**：支持数字输入/输出，不支持ADC，不支持硬件PWM。
- **PB5**：支持数字输入/输出，不支持ADC，不支持硬件PWM。
- **PB6**：支持数字输入/输出，不支持ADC，不支持硬件PWM。
- **PB7**：支持数字输入/输出，不支持ADC，不支持硬件PWM。
- **PB8**：支持数字输入/输出，不支持ADC，不支持硬件PWM。
- **PB9**：支持数字输入/输出，不支持ADC，不支持硬件PWM。
- **PB10**：支持数字输入/输出，不支持ADC，不支持硬件PWM。
- **PB11**：支持数字输入/输出，不支持ADC，不支持硬件PWM。
- **PB12**：支持数字输入/输出，不支持ADC，不支持硬件PWM。
- **PB13**：支持数字输入/输出，不支持ADC，不支持硬件PWM。
- **PB14**：支持数字输入/输出，不支持ADC，不支持硬件PWM。
- **PB15**：支持数字输入/输出，不支持ADC，不支持硬件PWM。

#### 5.5 PC13（板载LED）
- **PC13**：支持数字输入/输出，不支持ADC，不支持硬件PWM。此引脚专门用于板载LED，通过 `SET_LED` 命令控制亮灭（输出低电平点亮）。

### 6. 引脚动态模式切换示例
- **将 PA0 设为 ADC 模式并读取**：
  ```
  SET_MODE PA0 ADC
  OK: PA0 mode = ADC
  GET_ADC PA0
  OK: PA0 = 2048
  ```
- **将 PB0 设为输出并置高**：
  ```
  SET_MODE PB0 OUTPUT
  OK: PB0 mode = OUTPUT
  SET_DO PB0 1
  OK: PB0 = HIGH
  ```
- **将 PA8 设为 PWM 输出 50% 占空比**：
  ```
  SET_MODE PA8 PWM
  OK: PA8 mode = PWM (use SET_PWM to set duty)
  SET_PWM PA8 128
  OK: PA8 PWM = 128
  ```

### 7. Python 控制库示例
```python
import serial, time, re

class STM32IO:
    def __init__(self, port):
        self.ser = serial.Serial(port, 115200, timeout=1)
    def _cmd(self, cmd):
        self.ser.write((cmd+'\r\n').encode())
        lines=[]
        for _ in range(5):
            line=self.ser.readline().decode().strip()
            if line: lines.append(line)
            if line.startswith(('OK:','ERR:')): break
        return '\n'.join(lines)
    def set_mode(self, pin, mode):
        return self._cmd(f'SET_MODE {pin} {mode}')
    def set_do(self, pin, val):
        return self._cmd(f'SET_DO {pin} {val}')
    def get_di(self, pin):
        resp=self._cmd(f'GET_DI {pin}')
        m=re.search(r'=\s*(\d+)', resp)
        return int(m.group(1)) if m else None
    def get_adc(self, pin):
        resp=self._cmd(f'GET_ADC {pin}')
        m=re.search(r'=\s*(\d+)', resp)
        return int(m.group(1)) if m else None
    def set_pwm(self, pin, duty):
        return self._cmd(f'SET_PWM {pin} {duty}')
    def set_led(self, state):
        return self._cmd(f'SET_LED {state}')
    def close(self):
        self.ser.close()

# 使用示例
io = STM32IO('COM3')
io.set_mode('PB0','OUTPUT')
io.set_do('PB0',1)
print(io.get_adc('PA0'))
io.set_pwm('PA8',200)
io.set_led(1)
io.close()
```

### 8. 常见问题
**Q：为什么 PB2 不可用？**  
A：PB2 同时也是 BOOT1 引脚，多数开发板通过电阻拉高/拉低以决定启动模式。若将其作为普通 I/O 误操作，可能导致芯片无法启动或损坏，故禁用。

**Q：必须使用 115200 吗？**  
A：是的，固件固定为 115200 8N1，使用其他波特率将导致乱码或无响应。

**Q：PC13 LED 不亮？**  
A：检查限流电阻（通常板载），发送 `SET_LED 1` 后测量 PC13 电压，应为低电平（0V）。若一直高电平，检查焊接。

**Q：能否增加更多引脚？**  
A：可以，但需释放保留引脚（如使用内部 HSI 释放 PD0/PD1），修改源码中的 `availablePins` 数组，并自行承担风险。

### 9. 版本记录
- v6.0 (2026-07-02): 移除 PB2，固定波特率 115200，优化引脚功能描述。

---

**手册完毕**。如有疑问，请查阅源码注释或咨询开发者。





### 附录

 **ADC**和**PWM**功能的引脚列表及其**5V耐受**能力。

### 📊 引脚功能与5V耐受性对照表

| 引脚 | ADC支持 | PWM支持 | 5V耐受 | 关键说明 |
| :--- | :---: | :---: | :---: | :--- |
| **PA0** | ✔ | ✔ | ❌ | 支持ADC、PWM，但**非5V耐受** |
| **PA1** | ✔ | ✔ | ❌ | 支持ADC、PWM，但**非5V耐受** |
| **PA2** | ✔ | ✔ | ❌ | 支持ADC、PWM，但**非5V耐受** |
| **PA3** | ✔ | ✔ | ❌ | 支持ADC、PWM，但**非5V耐受** |
| **PA4** | ✔ | ❌ | ❌ | 仅支持ADC，**非5V耐受** |
| **PA5** | ✔ | ❌ | ❌ | 仅支持ADC，**非5V耐受** |
| **PA6** | ✔ | ✔ | ❌ | 支持ADC、PWM，但**非5V耐受** |
| **PA7** | ✔ | ✔ | ❌ | 支持ADC、PWM，但**非5V耐受** |
| **PA8** | ❌ | ✔ | ✔ | 仅支持PWM，**5V耐受** |
| **PA9** | ❌ | ✔ | ✔ | 仅支持PWM，**5V耐受** |
| **PA10**| ❌ | ✔ | ✔ | 仅支持PWM，**5V耐受** |
| **PB0** | ✔ | ✔ | ❌ | 支持ADC、PWM，但**非5V耐受** |
| **PB1** | ✔ | ❌ | ❌ | 仅支持ADC，**非5V耐受** |
| **PB6** | ❌ | ✔ | ✔ | 仅支持PWM，**5V耐受** |
| **PB7** | ❌ | ✔ | ✔ | 仅支持PWM，**5V耐受** |
| **PB8** | ❌ | ✔ | ✔ | 仅支持PWM，**5V耐受** |
| **PB9** | ❌ | ✔ | ✔ | 仅支持PWM，**5V耐受** |

### ⚠️ 重要说明

*   **5V耐受 (FT) 的含义**：标注为“5V耐受”的引脚，可以在输入电压为5V时安全工作。但需注意，**ADC引脚（如PA0-PA7, PB0-PB1）均非5V耐受**，严禁直接接入5V信号，否则可能损坏芯片。
*   **PWM引脚说明**：上表所列的PWM引脚是基于通用定时器（如TIM2, TIM3, TIM4）的输出通道。部分引脚（如PA6, PA7）的PWM功能可能需要进行重映射（Remap）才能使用。
*   **官方信息来源**：最准确的信息应参考ST官方发布的**STM32F103x8/B数据手册**中的“Pin definitions”表格。表格中标注“FT”的引脚即为5V耐受引脚。


在 **v6.0 固件** 中，上电后所有可用引脚默认配置如下：

- **除 PC13 外**：全部设置为 **浮空输入（`INPUT`）**，引脚电平由外部电路决定。
- **PC13（板载 LED）**：设置为 **输出（`OUTPUT`）**，默认输出 **高电平**（LED 熄灭）。

**没有任何引脚默认处于 ADC 或 PWM 模式**，这些功能需要通过 `SET_MODE` 命令动态切换。

---

### 📊 引脚默认模式与可切换能力表

| 引脚 | 程序默认模式 | 可切换为 ADC 模式？ | 可切换为 PWM 模式？ |
| :--- | :--- | :---: | :---: |
| **PA0** | `INPUT` | ✔ | ✔ |
| **PA1** | `INPUT` | ✔ | ✔ |
| **PA2** | `INPUT` | ✔ | ✔ |
| **PA3** | `INPUT` | ✔ | ✔ |
| **PA4** | `INPUT` | ✔ | ❌ |
| **PA5** | `INPUT` | ✔ | ❌ |
| **PA6** | `INPUT` | ✔ | ✔ |
| **PA7** | `INPUT` | ✔ | ✔ |
| **PA8** | `INPUT` | ❌ | ✔ |
| **PA9** | `INPUT` | ❌ | ✔ |
| **PA10**| `INPUT` | ❌ | ✔ |
| **PB0** | `INPUT` | ✔ | ✔ |
| **PB1** | `INPUT` | ✔ | ❌ |
| **PB3** | `INPUT` | ❌ | ❌ |
| **PB4** | `INPUT` | ❌ | ❌ |
| **PB5** | `INPUT` | ❌ | ❌ |
| **PB6** | `INPUT` | ❌ | ❌ |
| **PB7** | `INPUT` | ❌ | ❌ |
| **PB8** | `INPUT` | ❌ | ❌ |
| **PB9** | `INPUT` | ❌ | ❌ |
| **PB10**| `INPUT` | ❌ | ❌ |
| **PB11**| `INPUT` | ❌ | ❌ |
| **PB12**| `INPUT` | ❌ | ❌ |
| **PB13**| `INPUT` | ❌ | ❌ |
| **PB14**| `INPUT` | ❌ | ❌ |
| **PB15**| `INPUT` | ❌ | ❌ |
| **PC13**| `OUTPUT`（高电平） | ❌ | ❌ |

---

### 📌 补充说明

- **PB2** 已被程序**禁用**（因 BOOT1 风险），不会出现在任何操作中。
- **未列出引脚**（如 PA11, PA12, PA13, PA14, PD0, PD1, PC14, PC15）**不被程序控制**，保持硬件默认状态（通常为复用功能或浮空）。
- 所有可用引脚的 ADC/PWM 支持情况如上表所示，切换时若引脚不支持对应功能，会返回 `NOT SUPPORT FOR ...` 错误。
