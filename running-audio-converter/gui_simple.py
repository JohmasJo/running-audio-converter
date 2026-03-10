#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏃 Running Audio Converter - Simple GUI (English Only)
Minimal GUI to avoid encoding issues
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
from pathlib import Path

# Force UTF-8 encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Import converters
try:
    from converter import AudioConverter
    from converter_variable import VariableBPMConverter
    from converter_variable_fast import convert_fast
    from converter_variable_gpu import convert_gpu
    HAS_CONVERTERS = True
except ImportError as e:
    HAS_CONVERTERS = False
    print(f"Warning: Converter import failed: {e}")


class SimpleGUI:
    """Simple GUI for Running Audio Converter"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Running Audio Converter - 180 BPM")
        self.root.geometry("850x650")
        
        self.files = []
        self.is_processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI"""
        main = ttk.Frame(self.root, padding="15")
        main.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        ttk.Label(main, text="Running Audio Converter", 
                 font=("Helvetica", 18, "bold")).grid(row=0, column=0, pady=(0, 15))
        ttk.Label(main, text="Convert any audio to 180 BPM for running",
                 font=("Helvetica", 10)).grid(row=1, column=0, pady=(0, 15))
        
        # Converter selection
        conv_frame = ttk.LabelFrame(main, text="Converter", padding="10")
        conv_frame.grid(row=2, column=0, sticky="ew", pady=10)
        
        self.converter_var = tk.StringVar(value="standard")
        
        converters = [
            ("standard", "Standard - Fixed BPM (Fast)"),
            ("variable_fast", "Variable - Fast (Recommended)"),
            ("variable", "Variable - High Quality (Slow)"),
            ("variable_gpu", "Variable - GPU (Need NVIDIA)"),
        ]
        
        for i, (val, txt) in enumerate(converters):
            ttk.Radiobutton(conv_frame, text=txt, variable=self.converter_var, 
                          value=val).grid(row=i, column=0, sticky="w")
        
        # File selection
        file_frame = ttk.LabelFrame(main, text="Files", padding="10")
        file_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        self.file_list = tk.Listbox(file_frame, height=4)
        self.file_list.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        btn_frame = ttk.Frame(file_frame)
        btn_frame.grid(row=1, column=0)
        ttk.Button(btn_frame, text="Add Files", command=self.add_files).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Remove", command=self.remove_selected).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Clear", command=self.clear_files).pack(side="left", padx=2)
        
        # Parameters
        param_frame = ttk.LabelFrame(main, text="Parameters", padding="10")
        param_frame.grid(row=4, column=0, sticky="ew", pady=10)
        
        ttk.Label(param_frame, text="Target BPM:").grid(row=0, column=0)
        self.bpm_var = tk.StringVar(value="180")
        ttk.Spinbox(param_frame, from_=60, to=220, textvariable=self.bpm_var, 
                   width=8).grid(row=0, column=1, padx=5)
        
        self.metronome_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(param_frame, text="Add Metronome", 
                       variable=self.metronome_var).grid(row=0, column=2, padx=20)
        
        ttk.Label(param_frame, text="Volume:").grid(row=0, column=3)
        self.volume_var = tk.DoubleVar(value=0.3)
        ttk.Scale(param_frame, from_=0.0, to=1.0, variable=self.volume_var, 
                 length=100).grid(row=0, column=4, padx=5)
        
        # Output dir
        ttk.Label(param_frame, text="Output:").grid(row=1, column=0, pady=10)
        self.output_var = tk.StringVar(value="")
        ttk.Entry(param_frame, textvariable=self.output_var, width=40).grid(row=1, column=1, columnspan=3, padx=5)
        ttk.Button(param_frame, text="Browse", command=self.browse_output).grid(row=1, column=4)
        
        # Progress
        prog_frame = ttk.LabelFrame(main, text="Progress", padding="10")
        prog_frame.grid(row=5, column=0, sticky="ew", pady=10)
        
        self.progress_var = tk.DoubleVar()
        ttk.Progressbar(prog_frame, variable=self.progress_var, maximum=100).grid(row=0, column=0, sticky="ew")
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(prog_frame, textvariable=self.status_var).grid(row=1, column=0)
        
        # Start button
        self.start_btn = ttk.Button(main, text="START CONVERSION", command=self.start, 
                                   style="Accent.TButton")
        self.start_btn.grid(row=6, column=0, pady=15)
        
        # Log
        log_frame = ttk.LabelFrame(main, text="Log", padding="10")
        log_frame.grid(row=7, column=0, sticky="nsew", pady=10)
        main.rowconfigure(7, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, state="disabled")
        self.log_text.pack(fill="both", expand=True)
        
        # Check converters
        if not HAS_CONVERTERS:
            messagebox.showwarning("Warning", 
                "Converter modules not found!\n\nInstall: pip install -r requirements.txt")
    
    def add_files(self):
        """Add files"""
        types = [("Audio", "*.mp3 *.wav *.flac *.m4a *.ogg *.wma"), ("All", "*.*")]
        files = filedialog.askopenfilenames(title="Select audio files", filetypes=types)
        
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.file_list.insert("end", os.path.basename(f))
        
        self.log(f"Added {len(files)} file(s)")
    
    def remove_selected(self):
        """Remove selected"""
        sel = self.file_list.curselection()
        for i in reversed(sel):
            del self.files[i]
            self.file_list.delete(i)
    
    def clear_files(self):
        """Clear files"""
        self.files = []
        self.file_list.delete(0, "end")
        self.log("Cleared")
    
    def browse_output(self):
        """Browse output dir"""
        d = filedialog.askdirectory(title="Output directory")
        if d:
            self.output_var.set(d)
    
    def log(self, msg):
        """Add log"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
    
    def start(self):
        """Start conversion"""
        if not self.files:
            messagebox.showwarning("Warning", "Please add files first!")
            return
        
        if self.is_processing:
            messagebox.showwarning("Warning", "Processing...")
            return
        
        self.is_processing = True
        self.start_btn.configure(state="disabled")
        
        thread = threading.Thread(target=self.process, daemon=True)
        thread.start()
    
    def process(self):
        """Process files"""
        try:
            conv_type = self.converter_var.get()
            target_bpm = int(self.bpm_var.get())
            out_dir = self.output_var.get() or None
            
            total = len(self.files)
            
            for i, fpath in enumerate(self.files):
                self.status_var.set(f"Processing: {os.path.basename(fpath)}")
                self.progress_var.set((i / total) * 100)
                self.log(f"\n[{i+1}/{total}] {fpath}")
                
                try:
                    if conv_type == "standard":
                        conv = AudioConverter(target_bpm)
                        out = conv.convert(fpath, add_metronome=self.metronome_var.get(),
                                         metronome_volume=self.volume_var.get(),
                                         output_dir=out_dir)
                    elif conv_type == "variable":
                        conv = VariableBPMConverter(target_bpm)
                        out = conv.convert(fpath, output_dir=out_dir)
                    elif conv_type == "variable_fast":
                        out = convert_fast(fpath, target_bpm, output_dir=out_dir)
                    elif conv_type == "variable_gpu":
                        out = convert_gpu(fpath, target_bpm, output_dir=out_dir)
                    
                    self.log(f"OK: {os.path.basename(out)}")
                
                except Exception as e:
                    self.log(f"ERROR: {e}")
            
            self.status_var.set("Completed!")
            self.progress_var.set(100)
            self.log("\n=== All done! ===")
            messagebox.showinfo("Complete", f"Converted {total} file(s)!")
        
        except Exception as e:
            self.log(f"FATAL: {e}")
            messagebox.showerror("Error", str(e))
        
        finally:
            self.is_processing = False
            self.start_btn.configure(state="normal")
            self.status_var.set("Ready")


def main():
    import signal
    
    root = tk.Tk()
    
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Accent.TButton', background='#0078D7', foreground='white')
    
    app = SimpleGUI(root)
    
    def handler(sig, frame):
        print("\nInterrupted")
        root.quit()
        root.destroy()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handler)
    
    def check():
        root.after(100, check)
    
    root.after(100, check)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.destroy()
        sys.exit(0)


if __name__ == '__main__':
    main()
