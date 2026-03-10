#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏃 跑步音频转换器 - GUI 版本
图形界面版本，让操作更简单！
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path

from converter import AudioConverter


class RunningAudioConverterGUI:
    """跑步音频转换器 GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🏃 跑步音频转换器 - 180 BPM Edition")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 文件列表
        self.files = []
        self.is_processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="🏃 跑步音频转换器", 
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        subtitle_label = ttk.Label(
            main_frame,
            text="将任意音频转换为 180 BPM 跑步版本",
            font=("Helvetica", 10)
        )
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # 文件选择区域
        file_frame = ttk.LabelFrame(main_frame, text="📁 文件选择", padding="10")
        file_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(0, weight=1)
        
        # 文件列表
        self.file_listbox = tk.Listbox(file_frame, height=6, selectmode=tk.EXTENDED)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # 文件操作按钮
        btn_frame = ttk.Frame(file_frame)
        btn_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        add_btn = ttk.Button(btn_frame, text="添加文件", command=self.add_files)
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_btn = ttk.Button(btn_frame, text="移除选中", command=self.remove_selected)
        remove_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = ttk.Button(btn_frame, text="清空列表", command=self.clear_files)
        clear_btn.pack(side=tk.LEFT)
        
        # 设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ 设置", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # 目标 BPM
        ttk.Label(settings_frame, text="目标 BPM:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.bpm_var = tk.StringVar(value="180")
        bpm_spinbox = ttk.Spinbox(settings_frame, from_=60, to=220, textvariable=self.bpm_var, width=10)
        bpm_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 节拍器选项
        self.metronome_var = tk.BooleanVar(value=False)
        metronome_check = ttk.Checkbutton(
            settings_frame, 
            text="🎛️ 添加节拍器", 
            variable=self.metronome_var
        )
        metronome_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # 节拍器音量
        ttk.Label(settings_frame, text="节拍器音量:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.metro_volume_var = tk.DoubleVar(value=0.3)
        volume_scale = ttk.Scale(
            settings_frame, 
            from_=0.0, 
            to=1.0, 
            variable=self.metro_volume_var,
            orient=tk.HORIZONTAL,
            length=200
        )
        volume_scale.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 节拍器频率
        ttk.Label(settings_frame, text="节拍器频率 (Hz):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.beat_freq_var = tk.StringVar(value="1000")
        freq_spinbox = ttk.Spinbox(
            settings_frame, 
            from_=400, 
            to=2000, 
            textvariable=self.beat_freq_var, 
            width=10
        )
        freq_spinbox.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # 输出目录
        ttk.Label(settings_frame, text="输出目录:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.output_dir_var = tk.StringVar(value="")
        output_entry = ttk.Entry(settings_frame, textvariable=self.output_dir_var, width=40)
        output_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        browse_btn = ttk.Button(settings_frame, text="浏览...", command=self.browse_output_dir)
        browse_btn.grid(row=4, column=2, padx=(5, 0), pady=5)
        
        # 进度区域
        progress_frame = ttk.LabelFrame(main_frame, text="📊 进度", padding="10")
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
        
        self.status_label = ttk.Label(progress_frame, text="就绪", foreground="gray")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # 转换按钮
        self.convert_btn = ttk.Button(
            main_frame, 
            text="🚀 开始转换", 
            command=self.start_conversion,
            style="Accent.TButton"
        )
        self.convert_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="📝 日志", padding="10")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, width=60, state=tk.DISABLED)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        main_frame.rowconfigure(6, weight=1)
    
    def add_files(self):
        """添加文件"""
        filetypes = [
            ("音频文件", "*.mp3 *.wav *.flac *.m4a *.ogg *.wma"),
            ("所有文件", "*.*")
        ]
        files = filedialog.askopenfilenames(title="选择音频文件", filetypes=filetypes)
        
        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
        
        self.log(f"添加了 {len(files)} 个文件")
    
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
        self.log("已清空文件列表")
    
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
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
            messagebox.showwarning("警告", "请先添加音频文件！")
            return
        
        if self.is_processing:
            messagebox.showwarning("警告", "正在处理中，请稍候...")
            return
        
        self.is_processing = True
        self.convert_btn.configure(state=tk.DISABLED)
        
        # 在新线程中处理
        thread = threading.Thread(target=self.process_files, daemon=True)
        thread.start()
    
    def process_files(self):
        """处理文件"""
        try:
            target_bpm = int(self.bpm_var.get())
            metronome_volume = self.metro_volume_var.get()
            beat_frequency = int(self.beat_freq_var.get())
            output_dir = self.output_dir_var.get() or None
            
            converter = AudioConverter(target_bpm=target_bpm)
            
            total_files = len(self.files)
            
            for i, file_path in enumerate(self.files):
                self.update_status(f"处理中：{os.path.basename(file_path)}", (i / total_files) * 100)
                self.log(f"\n📁 开始处理：{file_path}")
                
                try:
                    output_file = converter.convert(
                        file_path,
                        add_metronome=self.metronome_var.get(),
                        metronome_volume=metronome_volume,
                        beat_frequency=beat_frequency,
                        output_dir=output_dir
                    )
                    self.log(f"✅ 完成：{output_file}")
                except Exception as e:
                    self.log(f"❌ 错误：{e}")
            
            self.update_status("完成！", 100)
            self.log("\n" + "=" * 40)
            self.log("🎉 所有文件处理完成！")
            
            messagebox.showinfo("完成", f"成功转换 {total_files} 个文件！")
            
        except Exception as e:
            self.log(f"❌ 严重错误：{e}")
            messagebox.showerror("错误", f"处理失败：{e}")
        
        finally:
            self.is_processing = False
            self.convert_btn.configure(state=tk.NORMAL)
            self.update_status("就绪")


def main():
    root = tk.Tk()
    app = RunningAudioConverterGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
