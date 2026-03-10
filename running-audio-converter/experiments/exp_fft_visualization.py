#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 FFT 频谱图可视化
分析音频的频域特征，验证 BPM 检测的基础数据
"""

import argparse
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from pathlib import Path
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def plot_fft_spectrum(audio_path: str, output_dir: str = ".", 
                      n_fft: int = 2048, hop_length: int = 512):
    """
    绘制 FFT 频谱图
    
    Args:
        audio_path: 音频文件路径
        output_dir: 输出目录
        n_fft: FFT 窗口大小
        hop_length: 跳跃长度
    """
    print(f"🎵 加载音频：{audio_path}")
    
    # 加载音频
    y, sr = librosa.load(audio_path, sr=None)
    duration = len(y) / sr
    
    print(f"   采样率：{sr} Hz")
    print(f"   时长：{duration:.2f} 秒")
    print(f"   样本数：{len(y)}")
    
    # 创建图形
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    fig.suptitle(f'FFT 频谱分析 - {Path(audio_path).name}', fontsize=16, fontweight='bold')
    
    # 1. 原始波形
    print("📊 绘制波形图...")
    times = np.arange(len(y)) / sr
    axes[0, 0].plot(times, y, linewidth=0.5, color='blue')
    axes[0, 0].set_xlabel('时间 (秒)')
    axes[0, 0].set_ylabel('振幅')
    axes[0, 0].set_title('1. 原始音频波形')
    axes[0, 0].set_xlim([0, duration])
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. 波形局部放大（前 2 秒）
    zoom_duration = min(2.0, duration)
    zoom_samples = int(zoom_duration * sr)
    axes[0, 1].plot(times[:zoom_samples], y[:zoom_samples], linewidth=0.5, color='green')
    axes[0, 1].set_xlabel('时间 (秒)')
    axes[0, 1].set_ylabel('振幅')
    axes[0, 1].set_title(f'2. 波形局部放大 (0-{zoom_duration}秒)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. 频谱图（Spectrogram）
    print("📊 计算频谱图...")
    D = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=n_fft, hop_length=hop_length)), 
                                 ref=np.max)
    
    times_stft = librosa.frames_to_time(D.shape[1], sr=sr, hop_length=hop_length)
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    
    im = librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='hz', 
                                   ax=axes[1, 0], hop_length=hop_length)
    axes[1, 0].set_title('3. 频谱图 (Spectrogram)')
    axes[1, 0].set_ylim([0, 8000])  # 显示 0-8kHz
    fig.colorbar(im, ax=axes[1, 0], format='%+2.0f dB')
    
    # 4. 平均频谱
    print("📊 计算平均频谱...")
    avg_spectrum = np.mean(D, axis=1)
    axes[1, 1].plot(freqs / 1000, avg_spectrum, linewidth=1, color='red')
    axes[1, 1].set_xlabel('频率 (kHz)')
    axes[1, 1].set_ylabel('平均幅度 (dB)')
    axes[1, 1].set_title('4. 平均频谱')
    axes[1, 1].set_xlim([0, sr/2000])  # 显示到 Nyquist 频率的一半
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_xscale('log')
    
    # 5. Onset Envelope（起始包络）
    print("📊 计算 Onset Envelope...")
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    times_onset = librosa.frames_to_time(len(onset_env), sr=sr, hop_length=hop_length)
    
    axes[2, 0].plot(times_onset, onset_env, linewidth=1, color='orange')
    axes[2, 0].set_xlabel('时间 (秒)')
    axes[2, 0].set_ylabel('强度')
    axes[2, 0].set_title('5. Onset Envelope (用于 BPM 检测)')
    axes[2, 0].grid(True, alpha=0.3)
    
    # 6. Onset Envelope 的 FFT（检测周期性）
    print("📊 计算 Onset Envelope 的 FFT...")
    onset_fft = np.fft.fft(onset_env)
    onset_fft_freq = np.fft.fftfreq(len(onset_env), d=hop_length/sr)
    
    # 只显示正频率，且只显示 0.5-4Hz 范围（对应 30-240 BPM）
    positive_mask = onset_fft_freq > 0
    freq_range_mask = (onset_fft_freq >= 0.5) & (onset_fft_freq <= 4.0)
    mask = positive_mask & freq_range_mask
    
    axes[2, 1].plot(onset_fft_freq[mask], np.abs(onset_fft[mask]), linewidth=1, color='purple')
    axes[2, 1].set_xlabel('频率 (Hz)')
    axes[2, 1].set_ylabel('强度')
    axes[2, 1].set_title('6. Onset Envelope FFT (检测节奏周期性)')
    axes[2, 1].grid(True, alpha=0.3)
    
    # 标注可能的 BPM
    peaks_x = []
    peaks_y = []
    for freq in np.linspace(1, 3, 5):  # 1-3 Hz (60-180 BPM)
        idx = np.argmin(np.abs(onset_fft_freq[mask] - freq))
        if np.abs(onset_fft_freq[mask][idx] - freq) < 0.1:
            peaks_x.append(freq)
            peaks_y.append(np.abs(onset_fft[mask][idx]))
            axes[2, 1].annotate(f'{freq*60:.0f} BPM', 
                               xy=(freq, np.abs(onset_fft[mask][idx])),
                               xytext=(5, 5), textcoords='offset points',
                               fontsize=9, color='purple')
    
    plt.tight_layout()
    
    # 保存
    output_path = Path(output_dir) / f"{Path(audio_path).stem}_fft_analysis.png"
    print(f"💾 保存：{output_path}")
    plt.savefig(str(output_path), dpi=150, bbox_inches='tight')
    
    print(f"✅ 完成！")
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description='📊 FFT 频谱图可视化',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python exp_fft_visualization.py ./test.mp3
  python exp_fft_visualization.py ./test.mp3 --output-dir ./results
  python exp_fft_visualization.py ./test.mp3 --nfft 4096
        '''
    )
    
    parser.add_argument('audio_file', help='输入音频文件')
    parser.add_argument('--output-dir', type=str, default='.', help='输出目录')
    parser.add_argument('--nfft', type=int, default=2048, help='FFT 窗口大小')
    parser.add_argument('--hop-length', type=int, default=512, help='跳跃长度')
    
    args = parser.parse_args()
    
    # 创建输出目录
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    plot_fft_spectrum(args.audio_file, args.output_dir, args.nfft, args.hop_length)


if __name__ == '__main__':
    main()
