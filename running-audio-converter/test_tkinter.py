#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 tkinter 中文显示
"""

import tkinter as tk
from tkinter import ttk
import sys
import locale

print(f"Python 版本：{sys.version}")
print(f"默认编码：{sys.getdefaultencoding()}")
print(f"文件系统编码：{sys.getfilesystemencoding()}")

try:
    print(f"Locale: {locale.getdefaultlocale()}")
except Exception as e:
    print(f"Locale 错误：{e}")

root = tk.Tk()
root.title("Tkinter 中文测试")
root.geometry("400x300")

frame = ttk.Frame(root, padding="20")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# 测试文本
test_texts = [
    "英文测试 - English Test",
    "中文测试 - 跑步音频转换器",
    "数字测试 - 180 BPM",
    "符号测试 - 🏃♂️🎵⚡",
]

for i, text in enumerate(test_texts):
    label = ttk.Label(frame, text=f"{i+1}. {text}", font=("Helvetica", 12))
    label.grid(row=i, column=0, sticky=tk.W, pady=5)

# 测试输入
entry_label = ttk.Label(frame, text="输入测试:")
entry_label.grid(row=len(test_texts), column=0, sticky=tk.W, pady=(20, 5))

entry = ttk.Entry(frame, width=40)
entry.insert(0, "请输入中文测试")
entry.grid(row=len(test_texts)+1, column=0, sticky=tk.W)

root.mainloop()
