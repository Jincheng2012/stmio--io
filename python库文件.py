#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
STM32 I/O 扩展器控制库 (函数式风格)
版本: 2.0
兼容固件: STM32 I/O Expander v6.0 (115200 8N1)

用法:
    import stmio
    stmio.init('COM3')               # 连接串口
    stmio.SET_DO('PA0', 1)           # 设置输出高
    val = stmio.GET_DI('PB10')       # 读取数字输入
    adc = stmio.GET_ADC('PA0')       # 读取ADC
    stmio.SET_PWM('PA8', 128)        # PWM 50%
    stmio.SET_MODE('PB0', 'OUTPUT')  # 模式切换
    stmio.SET_LED(1)                 # 点亮LED
    stmio.close()                    # 关闭连接
"""

import serial
import time
import re
import threading
from typing import Optional, Union

# ==================== 全局状态 ====================
_io = None
_is_connected = False
_lock = threading.Lock()  # 线程安全

# ==================== 内部类 ====================
class _StmioInternal:
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.is_open = False
        self._connect()

    def _connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.is_open = True
        except Exception as e:
            raise RuntimeError(f"无法连接串口 {self.port}: {e}")

    def _send_cmd(self, cmd: str) -> str:
        if not self.is_open:
            raise RuntimeError("串口未打开")
        with _lock:
            self.ser.write((cmd + '\r\n').encode())
            lines = []
            for _ in range(10):
                line = self.ser.readline().decode().strip()
                if line:
                    lines.append(line)
                    if line.startswith(('OK:', 'ERR:', 'NOT SUPPORT')):
                        break
            return '\n'.join(lines) if lines else ''

    def _parse_response(self, resp: str, expected_prefix: str = 'OK:') -> str:
        if not resp:
            raise RuntimeError("无响应（设备可能未连接或超时）")
        if resp.startswith('ERR:') or resp.startswith('NOT SUPPORT'):
            raise RuntimeError(resp)
        if resp.startswith(expected_prefix):
            parts = resp.split(':', 1)
            return parts[1].strip() if len(parts) > 1 else ''
        return resp

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.is_open = False

# ==================== 公开函数 ====================

def init(port: str, baudrate: int = 115200, timeout: float = 1.0) -> None:
    """
    初始化串口连接（必须首先调用）

    :param port: 串口号，如 'COM3' 或 '/dev/ttyACM0'
    :param baudrate: 波特率，必须与固件一致（默认115200）
    :param timeout: 读取超时秒数
    """
    global _io, _is_connected
    if _io is not None:
        close()
    _io = _StmioInternal(port, baudrate, timeout)
    _is_connected = True

def close() -> None:
    """关闭串口连接，释放资源"""
    global _io, _is_connected
    if _io:
        _io.close()
        _io = None
        _is_connected = False

def _ensure_connected():
    if not _is_connected or _io is None:
        raise RuntimeError("未连接，请先调用 stmio.init(port)")

def _send_cmd(cmd: str) -> str:
    _ensure_connected()
    return _io._send_cmd(cmd)

def _parse(resp: str) -> str:
    return _io._parse_response(resp)

# ==================== 命令API（与固件命令完全对应） ====================

def SET_DO(pin: str, value: int) -> bool:
    """
    设置数字输出

    :param pin: 引脚名，如 'PA0', 'PB13'
    :param value: 0 或 1
    :return: True 表示成功
    """
    if value not in (0, 1):
        raise ValueError("值必须为 0 或 1")
    resp = _send_cmd(f"SET_DO {pin} {value}")
    _parse(resp)
    return True

def GET_DI(pin: str) -> int:
    """
    读取数字输入

    :param pin: 引脚名
    :return: 0 或 1
    """
    resp = _send_cmd(f"GET_DI {pin}")
    result = _parse(resp)
    match = re.search(r'=\s*(\d+)', result)
    if match:
        return int(match.group(1))
    raise RuntimeError(f"无法解析返回: {result}")

def GET_ADC(pin: str) -> int:
    """
    读取ADC值（12位，0~4095）

    :param pin: 支持ADC的引脚
    :return: ADC值
    """
    resp = _send_cmd(f"GET_ADC {pin}")
    result = _parse(resp)
    match = re.search(r'=\s*(\d+)', result)
    if match:
        return int(match.group(1))
    raise RuntimeError(f"无法解析返回: {result}")

def SET_PWM(pin: str, duty: int) -> bool:
    """
    设置硬件PWM占空比

    :param pin: 支持PWM的引脚
    :param duty: 0~255
    :return: True
    """
    if not (0 <= duty <= 255):
        raise ValueError("占空比必须在 0~255 之间")
    resp = _send_cmd(f"SET_PWM {pin} {duty}")
    _parse(resp)
    return True

def SET_MODE(pin: str, mode: str) -> bool:
    """
    更改引脚工作模式

    :param pin: 引脚名
    :param mode: 字符串，支持 'INPUT', 'INPUT_PULLUP', 'INPUT_PULLDOWN', 'OUTPUT', 'PWM', 'ADC'
    :return: True
    """
    valid = ['INPUT', 'INPUT_PULLUP', 'INPUT_PULLDOWN', 'OUTPUT', 'PWM', 'ADC']
    mode_upper = mode.upper()
    if mode_upper not in valid:
        raise ValueError(f"模式必须是 {', '.join(valid)}")
    resp = _send_cmd(f"SET_MODE {pin} {mode_upper}")
    _parse(resp)
    return True

def SET_LED(value: int, pin: Optional[str] = None) -> bool:
    """
    控制板载LED (PC13)

    :param value: 0 熄灭，1 点亮
    :param pin: 可选，为了兼容旧代码可传入任意引脚，但会被忽略
    :return: True
    """
    if value not in (0, 1):
        raise ValueError("值必须为 0 或 1")
    resp = _send_cmd(f"SET_LED {value}")
    _parse(resp)
    return True

def send_raw(cmd: str) -> str:
    """
    发送任意原始命令，直接返回响应文本（不解析）

    :param cmd: 命令字符串（不含换行）
    :return: 原始响应字符串
    """
    return _send_cmd(cmd)

# ==================== 状态查询（可选） ====================

def is_connected() -> bool:
    """返回当前连接状态"""
    return _is_connected

def get_port() -> str:
    """返回当前连接的串口号，若未连接则返回空字符串"""
    if _io:
        return _io.port
    return ""

# ==================== 便捷的上下文管理器 ====================
# 虽然函数式风格不需要，但提供 with 支持也很方便

class StmioContext:
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

    def __enter__(self):
        init(self.port, self.baudrate, self.timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        close()

# 使用示例:
# with stmio.StmioContext('COM3') as ctx:
#     stmio.SET_LED(1)
