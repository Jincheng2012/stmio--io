#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STM32 I/O 扩展器上位机 (Tkinter) v2.0
功能：引脚/值下拉选择+手动输入，动态过滤
通信: 115200 8N1
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
import time
import re

# ==================== 引脚定义 ====================
ALL_PINS = [
    'PA0', 'PA1', 'PA2', 'PA3', 'PA4', 'PA5', 'PA6', 'PA7',
    'PA8', 'PA9', 'PA10',
    'PB0', 'PB1',
    'PB3', 'PB4', 'PB5', 'PB6', 'PB7', 'PB8', 'PB9',
    'PB10', 'PB11', 'PB12', 'PB13', 'PB14', 'PB15',
    'PC13'
]
ADC_PINS = ['PA0', 'PA1', 'PA2', 'PA3', 'PA4', 'PA5', 'PA6', 'PA7', 'PB0', 'PB1']
PWM_PINS = ['PA0', 'PA1', 'PA2', 'PA3', 'PA6', 'PA7', 'PA8', 'PA9', 'PA10', 'PB0', 'PB1']
# 注意：PB1 不支持 PWM，但上表已正确

# 值预设
DO_VALUES = ['0', '1']
PWM_VALUES = ['0', '64', '128', '192', '255']
MODE_VALUES = ['INPUT', 'OUTPUT', 'INPUT_PULLUP', 'INPUT_PULLDOWN', 'PWM', 'ADC']
LED_VALUES = ['0', '1']

# ==================== 核心通信类 ====================
class STM32IO:
    def __init__(self, port, baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.is_connected = False

    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.is_connected = True
            return True, "Connected to " + self.port
        except Exception as e:
            return False, str(e)

    def disconnect(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.is_connected = False
        return True, "Disconnected"

    def send_command(self, cmd):
        if not self.is_connected or not self.ser:
            return "ERR: Not connected"
        try:
            self.ser.write((cmd + '\r\n').encode())
            time.sleep(0.05)
            lines = []
            for _ in range(10):
                line = self.ser.readline().decode().strip()
                if line:
                    lines.append(line)
                    if line.startswith(('OK:', 'ERR:', 'NOT SUPPORT')):
                        break
            return '\n'.join(lines) if lines else 'No response'
        except Exception as e:
            return f"ERR: {str(e)}"

# ==================== GUI 主程序 ====================
class IOExpanderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STM32 I/O 扩展器控制 v2.0")
        self.root.geometry("750x650")
        self.root.resizable(False, False)

        self.baudrate = 115200
        self.io = None

        self.create_widgets()
        self.refresh_ports()
        self.on_op_changed()  # 初始化下拉选项

    def create_widgets(self):
        # ======== 串口连接区域 ========
        frame_top = ttk.LabelFrame(self.root, text="串口连接", padding=5)
        frame_top.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frame_top, text="端口:").grid(row=0, column=0, padx=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(frame_top, textvariable=self.port_var, width=15, state="readonly")
        self.port_combo.grid(row=0, column=1, padx=5)

        ttk.Button(frame_top, text="刷新", command=self.refresh_ports).grid(row=0, column=2, padx=5)
        ttk.Button(frame_top, text="连接", command=self.toggle_connection).grid(row=0, column=3, padx=5)
        self.conn_status = ttk.Label(frame_top, text="未连接", foreground="red")
        self.conn_status.grid(row=0, column=4, padx=10)

        # ======== 操作区域 ========
        frame_cmd = ttk.LabelFrame(self.root, text="命令控制", padding=5)
        frame_cmd.pack(fill=tk.X, padx=10, pady=5)

        # 操作类型
        ttk.Label(frame_cmd, text="操作类型:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.ops = [
            "SET_DO (写数字输出)",
            "GET_DI (读数字输入)",
            "GET_ADC (读ADC)",
            "SET_PWM (写PWM)",
            "SET_MODE (更改引脚模式)",
            "SET_LED (控制LED)"
        ]
        self.op_var = tk.StringVar()
        self.op_combo = ttk.Combobox(frame_cmd, values=self.ops, width=25, state="readonly")
        self.op_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.op_combo.bind("<<ComboboxSelected>>", self.on_op_changed)
        self.op_combo.current(0)

        # 参数区域（动态变化）
        self.param_frame = ttk.Frame(frame_cmd)
        self.param_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)

        # 引脚下拉框
        ttk.Label(self.param_frame, text="引脚:").grid(row=0, column=0, padx=5)
        self.pin_var = tk.StringVar()
        self.pin_combo = ttk.Combobox(self.param_frame, textvariable=self.pin_var, width=10, state="normal")
        self.pin_combo.grid(row=0, column=1, padx=5)
        self.pin_combo.bind("<KeyRelease>", self.on_pin_manual)  # 允许手动输入

        # 值下拉框（可输入）
        ttk.Label(self.param_frame, text="值:").grid(row=0, column=2, padx=5)
        self.val_var = tk.StringVar()
        self.val_combo = ttk.Combobox(self.param_frame, textvariable=self.val_var, width=15, state="normal")
        self.val_combo.grid(row=0, column=3, padx=5)
        self.val_combo.bind("<KeyRelease>", self.on_val_manual)

        # 额外提示
        self.hint_var = tk.StringVar(value="")
        self.hint_label = ttk.Label(frame_cmd, textvariable=self.hint_var, foreground="gray")
        self.hint_label.grid(row=2, column=0, columnspan=2, padx=5, pady=2, sticky=tk.W)

        # 发送按钮
        ttk.Button(frame_cmd, text="发送命令", command=self.send_cmd).grid(row=3, column=0, columnspan=2, pady=10)

        # ======== 反馈显示 ========
        frame_out = ttk.LabelFrame(self.root, text="命令反馈", padding=5)
        frame_out.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.output_text = scrolledtext.ScrolledText(frame_out, wrap=tk.WORD, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        ttk.Button(self.root, text="清空日志", command=self.clear_log).pack(pady=2)

    # ==================== 辅助函数 ====================
    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [p.device for p in ports]
        self.port_combo['values'] = port_list
        if port_list:
            self.port_var.set(port_list[0])

    def toggle_connection(self):
        if self.io and self.io.is_connected:
            self.io.disconnect()
            self.io = None
            self.conn_status.config(text="未连接", foreground="red")
            self.append_log("已断开连接")
        else:
            port = self.port_var.get().strip()
            if not port:
                messagebox.showerror("错误", "请选择串口端口")
                return
            self.io = STM32IO(port, self.baudrate)
            ok, msg = self.io.connect()
            if ok:
                self.conn_status.config(text="已连接", foreground="green")
                self.append_log(f"连接成功: {msg}")
                resp = self.io.send_command("HELP")
                self.append_log(f"HELP 响应:\n{resp}")
            else:
                messagebox.showerror("连接失败", msg)
                self.io = None

    def on_op_changed(self, event=None):
        """根据操作类型更新引脚列表和值列表"""
        op = self.op_combo.get()
        # 选择引脚列表
        if "SET_DO" in op or "GET_DI" in op or "SET_MODE" in op:
            pins = ALL_PINS
        elif "GET_ADC" in op:
            pins = ADC_PINS
        elif "SET_PWM" in op:
            pins = PWM_PINS
        elif "SET_LED" in op:
            pins = []  # 不需要引脚
        else:
            pins = ALL_PINS

        # 更新引脚下拉
        if pins:
            self.pin_combo['values'] = pins
            self.pin_combo.config(state="normal")
            if self.pin_var.get() not in pins:
                self.pin_var.set(pins[0] if pins else "")
        else:
            self.pin_combo['values'] = []
            self.pin_var.set("")
            self.pin_combo.config(state="disabled")

        # 更新值列表
        if "SET_DO" in op:
            vals = DO_VALUES
            self.hint_var.set("值: 0 或 1")
        elif "GET_DI" in op or "GET_ADC" in op:
            vals = []
            self.hint_var.set("只读操作，无需填写值")
            self.val_combo.config(state="disabled")
            self.val_var.set("")
        elif "SET_PWM" in op:
            vals = PWM_VALUES
            self.hint_var.set("值: 0 ~ 255")
        elif "SET_MODE" in op:
            vals = MODE_VALUES
            self.hint_var.set("选择或输入模式")
        elif "SET_LED" in op:
            vals = LED_VALUES
            self.hint_var.set("值: 0 或 1")
        else:
            vals = []
            self.hint_var.set("")

        # 更新值下拉
        if vals:
            self.val_combo['values'] = vals
            self.val_combo.config(state="normal")
            if self.val_var.get() not in vals:
                self.val_var.set(vals[0] if vals else "")
        else:
            self.val_combo['values'] = []
            self.val_var.set("")
            self.val_combo.config(state="disabled")

    # 允许手动输入，同时保留下拉（Combobox默认支持）
    def on_pin_manual(self, event):
        # 可在此添加输入验证，无特殊处理
        pass

    def on_val_manual(self, event):
        pass

    def send_cmd(self):
        if not self.io or not self.io.is_connected:
            messagebox.showerror("错误", "请先连接串口")
            return

        op = self.op_combo.get()
        pin = self.pin_var.get().strip()
        val = self.val_var.get().strip()

        # 构造命令
        cmd = ""
        if "SET_DO" in op:
            if not pin or not val:
                messagebox.showerror("错误", "引脚和值不能为空")
                return
            if val not in DO_VALUES:
                messagebox.showerror("错误", "值必须为 0 或 1")
                return
            cmd = f"SET_DO {pin} {val}"
        elif "GET_DI" in op:
            if not pin:
                messagebox.showerror("错误", "请输入引脚")
                return
            cmd = f"GET_DI {pin}"
        elif "GET_ADC" in op:
            if not pin:
                messagebox.showerror("错误", "请输入引脚")
                return
            if pin not in ADC_PINS:
                messagebox.showerror("错误", f"{pin} 不支持 ADC")
                return
            cmd = f"GET_ADC {pin}"
        elif "SET_PWM" in op:
            if not pin or not val:
                messagebox.showerror("错误", "引脚和值不能为空")
                return
            if pin not in PWM_PINS:
                messagebox.showerror("错误", f"{pin} 不支持硬件 PWM")
                return
            try:
                ival = int(val)
                if ival < 0 or ival > 255:
                    raise ValueError
            except:
                messagebox.showerror("错误", "值必须是 0~255 的整数")
                return
            cmd = f"SET_PWM {pin} {val}"
        elif "SET_MODE" in op:
            if not pin or not val:
                messagebox.showerror("错误", "引脚和模式不能为空")
                return
            valid_modes = ['INPUT', 'OUTPUT', 'INPUT_PULLUP', 'INPUT_PULLDOWN', 'PWM', 'ADC']
            if val.upper() not in valid_modes:
                messagebox.showerror("错误", f"模式必须是: {', '.join(valid_modes)}")
                return
            cmd = f"SET_MODE {pin} {val.upper()}"
        elif "SET_LED" in op:
            if not val:
                messagebox.showerror("错误", "请输入值 (0或1)")
                return
            if val not in LED_VALUES:
                messagebox.showerror("错误", "值必须为 0 或 1")
                return
            cmd = f"SET_LED {val}"
        else:
            return

        # 发送命令
        self.append_log(f">>> {cmd}")
        resp = self.io.send_command(cmd)
        self.append_log(f"<<< {resp}")

    def append_log(self, text):
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)

    def clear_log(self):
        self.output_text.delete(1.0, tk.END)

# ==================== 主程序入口 ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = IOExpanderApp(root)
    root.mainloop()
