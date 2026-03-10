#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏃 跑步音频转换器 - 统一 GUI 界面
整合所有转换器，提供友好的图形界面

修复：中文编码问题
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
from pathlib import Path
from typing import Optional

# 设置默认编码为 UTF-8
import locale
locale.setlocale(locale.LC_ALL, '')

# 导入转换器
try:
    from converter import AudioConverter, MetronomeGenerator
    from converter_variable import VariableBPMConverter
    from converter_variable_fast import convert_fast
    from converter_variable_gpu import convert_gpu
    HAS_CONVERTERS = True
except ImportError as e:
    HAS_CONVERTERS = False
    print(f"⚠️  导入转换器失败：{e}")


# 尝试设置中文字体
def setup_chinese_font():
    """设置中文字体"""
    import platform
    
    system = platform.system()
    
    if system == "Windows":
        # Windows 常用中文字体
        fonts = ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi"]
    elif system == "Darwin":
        # macOS 常用中文字体
        fonts = ["PingFang SC", "Heiti SC", "STHeiti", "Arial Unicode MS"]
    else:
        # Linux 常用中文字体
        fonts = ["WenQuanYi Micro Hei", "WenQuanYi Zen Hei", "Noto Sans CJK SC", "SimHei"]
    
    for font in fonts:
        try:
            # 测试字体是否可用
            test_font = tk.font.Font(family=font, size=10)
            return font
        except Exception:
            continue
    
    return None  # 使用默认字体


class RunningAudioConverterGUI:
    """跑步音频转换器 - 统一 GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Running Audio Converter - 180 BPM")
        self.root.geometry("900x750")
        self.root.minsize(800, 650)
        
        # 设置中文字体
        self.chinese_font = setup_chinese_font()
        
        # 状态变量
        self.files = []
        self.is_processing = False
        self.current_process = None
        
        # 创建界面
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # ===== 标题区域 =====
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(
            title_frame,
            text="Running Audio Converter (180 BPM)",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = ttk.Label(
            title_frame,
            text="  -  Convert any audio to 180 BPM for running",
            font=("Helvetica", 10)
        )
        subtitle_label.pack(side=tk.LEFT)
        
        # ===== 转换器选择区域 =====
        converter_frame = ttk.LabelFrame(main_frame, text="Converter Type", padding="10")
        converter_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        converter_frame.columnconfigure(1, weight=1)
        
        self.converter_var = tk.StringVar(value="standard")
        
        converters = [
            ("standard", "Standard - Fixed BPM Songs", "Fast processing for songs with fixed BPM"),
            ("variable", "Variable - High Quality", "For songs with BPM changes, quality first"),
            ("variable_fast", "Variable - Fast", "For songs with BPM changes, speed first"),
            ("variable_gpu", "Variable - GPU Accelerated", "Requires NVIDIA GPU, fastest speed"),
        ]
        
        for i, (value, text, desc) in enumerate(converters):
            rb = ttk.Radiobutton(
                converter_frame,
                text=text,
                variable=self.converter_var,
                value=value,
                command=self.on_converter_change
            )
            rb.grid(row=i, column=0, sticky=tk.W, pady=2)
            
            desc_label = ttk.Label(converter_frame, text=desc, foreground="gray")
            desc_label.grid(row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # ===== 文件选择区域 =====
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        
        # 文件列表
        self.file_listbox = tk.Listbox(file_frame, height=5, selectmode=tk.EXTENDED)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 文件操作按钮
        btn_frame = ttk.Frame(file_frame)
        btn_frame.grid(row=1, column=0, sticky=tk.W)
        
        add_btn = ttk.Button(btn_frame, text="Add Files", command=self.add_files)
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_btn = ttk.Button(btn_frame, text="Remove Selected", command=self.remove_selected)
        remove_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = ttk.Button(btn_frame, text="Clear All", command=self.clear_files)
        clear_btn.pack(side=tk.LEFT)
        
        # ===== 参数设置区域 =====
        params_frame = ttk.LabelFrame(main_frame, text="Parameters", padding="10")
        params_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        params_frame.columnconfigure(1, weight=1)
        
        # 目标 BPM
        ttk.Label(params_frame, text="Target BPM:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.bpm_var = tk.StringVar(value="180")
        bpm_spinbox = ttk.Spinbox(params_frame, from_=60, to=220, textvariable=self.bpm_var, width=10)
        bpm_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 变速版专用参数
        self.variable_params_frame = ttk.Frame(params_frame)
        self.variable_params_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(self.variable_params_frame, text="Window Size (s):").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.window_size_var = tk.StringVar(value="30.0")
        ttk.Entry(self.variable_params_frame, textvariable=self.window_size_var, width=10).grid(row=0, column=1, padx=(10, 0), pady=3)
        
        ttk.Label(self.variable_params_frame, text="Hop Size (s):").grid(row=0, column=2, sticky=tk.W, padx=(20, 0), pady=3)
        self.hop_size_var = tk.StringVar(value="15.0")
        ttk.Entry(self.variable_params_frame, textvariable=self.hop_size_var, width=10).grid(row=0, column=3, padx=(10, 0), pady=3)
        
        ttk.Label(self.variable_params_frame, text="BPM Threshold:").grid(row=0, column=4, sticky=tk.W, padx=(20, 0), pady=3)
        self.threshold_var = tk.StringVar(value="15.0")
        ttk.Entry(self.variable_params_frame, textvariable=self.threshold_var, width=10).grid(row=0, column=5, padx=(10, 0), pady=3)
        
        # 节拍器选项
        self.metronome_var = tk.BooleanVar(value=False)
        metronome_check = ttk.Checkbutton(
            params_frame,
            text="Add Metronome",
            variable=self.metronome_var
        )
        metronome_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 节拍器音量
        ttk.Label(params_frame, text="Metronome Volume:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.metro_volume_var = tk.DoubleVar(value=0.3)
        volume_scale = ttk.Scale(
            params_frame,
            from_=0.0,
            to=1.0,
            variable=self.metro_volume_var,
            orient=tk.HORIZONTAL,
            length=200
        )
        volume_scale.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 节拍器频率
        ttk.Label(params_frame, text="Metronome Frequency (Hz):").grid(row=3, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.beat_freq_var = tk.StringVar(value="1000")
        freq_spinbox = ttk.Spinbox(
            params_frame,
            from_=400,
            to=2000,
            textvariable=self.beat_freq_var,
            width=10
        )
        freq_spinbox.grid(row=3, column=3, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 输出目录
        ttk.Label(params_frame, text="Output Directory:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar(value="")
        output_entry = ttk.Entry(params_frame, textvariable=self.output_dir_var, width=40)
        output_entry.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        browse_btn = ttk.Button(params_frame, text="Browse...", command=self.browse_output_dir)
        browse_btn.grid(row=4, column=3, padx=(5, 0), pady=5)
        
        # ===== 进度区域 =====
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame, text="Ready", foreground="gray")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # ===== 转换按钮 =====
        self.convert_btn = ttk.Button(
            main_frame,
            text="Start Conversion",
            command=self.start_conversion,
            style="Accent.TButton"
        )
        self.convert_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # ===== 日志区域 =====
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=10, width=80, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        main_frame.rowconfigure(6, weight=1)
        
        # 检查依赖
        if not HAS_CONVERTERS:
            messagebox.showwarning(
                "Warning",
                "Converter modules import failed!\n\nPlease install dependencies:\npip install -r requirements.txt"
            )
    
    def on_converter_change(self):
        """转换器选择变化"""
        converter = self.converter_var.get()
        is_variable = converter in ["variable", "variable_fast", "variable_gpu"]
        
        # 显示/隐藏变速版参数
        if is_variable:
            self.variable_params_frame.grid()
        else:
            self.variable_params_frame.grid_remove()
    
    def add_files(self):
        """添加文件"""
        filetypes = [
            ("Audio files", "*.mp3 *.wav *.flac *.m4a *.ogg *.wma"),
            ("All files", "*.*")
        ]
        files = filedialog.askopenfilenames(title="Select audio files", filetypes=filetypes)
        
        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
        
        self.log(f"Added {len(files)} file(s)")
    
    def remove_selected(self):
        """移除选中的文件"""
        selection = self.file_listbox.curselection()
        for index in reversed(selection):
            del self.files[index]
            self.file_listbox.delete(index)
    
    def clear_files(self):
        """清空文件列表"""
        self.files = []
        self.file_listbox.delete(0, tk.END)
        self.log("Cleared file list")
    
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.output_dir_var.set(directory)
    
    def log(self, message):
        """添加日志"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
    
    def update_status(self, message, progress=None):
        """更新状态"""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_var.set(progress)
        self.root.update_idletasks()
    
    def start_conversion(self):
        """开始转换"""
        if not self.files:
            messagebox.showwarning("Warning", "Please add audio files first!")
            return
        
        if self.is_processing:
            messagebox.showwarning("Warning", "Processing in progress, please wait...")
            return
        
        self.is_processing = True
        self.convert_btn.configure(state=tk.DISABLED)
        
        # 在新线程中处理
        thread = threading.Thread(target=self.process_files, daemon=True)
        thread.start()
    
    def process_files(self):
        """处理文件"""
        try:
            converter_type = self.converter_var.get()
            target_bpm = int(self.bpm_var.get())
            output_dir = self.output_dir_var.get() or None
            
            total_files = len(self.files)
            
            for i, file_path in enumerate(self.files):
                self.update_status(f"Processing: {os.path.basename(file_path)}", (i / total_files) * 100)
                self.log(f"\n[{i+1}/{total_files}] Starting: {file_path}")
                
                try:
                    if converter_type == "standard":
                        output_file = self.convert_standard(file_path, target_bpm, output_dir)
                    
                    elif converter_type == "variable":
                        output_file = self.convert_variable(file_path, target_bpm, output_dir)
                    
                    elif converter_type == "variable_fast":
                        output_file = self.convert_variable_fast(file_path, target_bpm, output_dir)
                    
                    elif converter_type == "variable_gpu":
                        output_file = self.convert_variable_gpu(file_path, target_bpm, output_dir)
                    
                    self.log(f"Done: {output_file}")
                
                except Exception as e:
                    self.log(f"Error: {e}")
                    import traceback
                    traceback.print_exc()
            
            self.update_status("Completed!", 100)
            self.log("\n" + "=" * 40)
            self.log("All files processed successfully!")
            
            messagebox.showinfo("Complete", f"Successfully converted {total_files} file(s)!")
        
        except Exception as e:
            self.log(f"Fatal error: {e}")
            messagebox.showerror("Error", f"Processing failed: {e}")
        
        finally:
            self.is_processing = False
            self.convert_btn.configure(state=tk.NORMAL)
            self.update_status("Ready")
    
    def convert_standard(self, file_path, target_bpm, output_dir):
        """标准版转换"""
        converter = AudioConverter(target_bpm=target_bpm)
        return converter.convert(
            file_path,
            add_metronome=self.metronome_var.get(),
            metronome_volume=self.metro_volume_var.get(),
            beat_frequency=int(self.beat_freq_var.get()),
            output_dir=output_dir
        )
    
    def convert_variable(self, file_path, target_bpm, output_dir):
        """变速版 - 高质量"""
        converter = VariableBPMConverter(
            target_bpm=target_bpm,
            window_size=float(self.window_size_var.get()),
            hop_size=float(self.hop_size_var.get()),
            bpm_threshold=float(self.threshold_var.get())
        )
        return converter.convert(file_path, output_dir)
    
    def convert_variable_fast(self, file_path, target_bpm, output_dir):
        """变速版 - 快速"""
        return convert_fast(
            file_path,
            target_bpm=target_bpm,
            window_size=float(self.window_size_var.get()),
            hop_size=float(self.hop_size_var.get()),
            bpm_threshold=float(self.threshold_var.get()),
            output_dir=output_dir
        )
    
    def convert_variable_gpu(self, file_path, target_bpm, output_dir):
        """变速版 - GPU 加速"""
        return convert_gpu(
            file_path,
            target_bpm=target_bpm,
            window_size=float(self.window_size_var.get()),
            hop_size=float(self.hop_size_var.get()),
            bpm_threshold=float(self.threshold_var.get()),
            output_dir=output_dir
        )


def main():
    import signal
    
    root = tk.Tk()
    
    # 设置样式
    style = ttk.Style()
    style.theme_use('clam')
    
    # 配置 Accent 按钮样式
    style.configure('Accent.TButton', foreground='white', background='#0078D7')
    
    app = RunningAudioConverterGUI(root)
    
    # 处理 Ctrl+C 信号
    def signal_handler(sig, frame):
        print("\nReceived interrupt signal, exiting...")
        root.quit()
        root.destroy()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # 定期检查信号
    def check_signals():
        root.after(100, check_signals)
    
    root.after(100, check_signals)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nProgram interrupted")
        root.destroy()
        sys.exit(0)


if __name__ == '__main__':
    main()
