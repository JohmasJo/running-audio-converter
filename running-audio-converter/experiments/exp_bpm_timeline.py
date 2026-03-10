#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📈 BPM-时间曲线可视化
分析 BPM 随时间的变化，验证变速检测算法
"""

import argparse
import numpy as np
import librosa
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.ndimage import median_filter
from typing import List, Tuple


def detect_bpm_timeline(audio_path: str, window_size: float = 10.0, 
                        hop_size: float = 5.0) -> Tuple[List[float], List[float]]:
    """检测 BPM 时间线"""
    print(f"🎵 检测 BPM 时间线 (窗口={window_size}s, 跳跃={hop_size}s)...")
    
    y, sr = librosa.load(audio_path, sr=22050, mono=True)
    duration = len(y) / sr
    
    window_samples = int(window_size * sr)
    hop_samples = int(hop_size * sr)
    
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    
    times = []
    bpms = []
    
    num_windows = max(1, int((len(onset_env) - window_samples) / hop_samples) + 1)
    
    for i in range(num_windows):
        start = i * hop_samples
        end = start + window_samples
        
        if end > len(onset_env):
            end = len(onset_env)
        
        segment_env = onset_env[start:end]
        
        if len(segment_env) < 100:
            continue
        
        try:
            autocorr = np.correlate(segment_env, segment_env, mode='full')
            autocorr = autocorr[len(autocorr)//2:]
            
            min_lag = int(sr / 200 * 60)
            max_lag = int(sr / 60 * 60)
            
            if max_lag > len(autocorr):
                max_lag = len(autocorr)
            
            peak_region = autocorr[min_lag:max_lag]
            peak_lag = np.argmax(peak_region) + min_lag
            
            if peak_lag > 0:
                bpm = 60 * sr / peak_lag
                
                if 60 <= bpm <= 220:
                    time = start / sr
                    times.append(time)
                    bpms.append(float(bpm))
        except Exception:
            pass
        
        if (i + 1) % 10 == 0 or i == num_windows - 1:
            progress = (i + 1) / num_windows * 100
            print(f"   进度：{progress:.1f}%")
    
    if len(bpms) > 3:
        bpms = median_filter(bpms, size=3).tolist()
    
    print(f"   检测到 {len(times)} 个 BPM 采样点")
    
    return times, bpms


def find_change_points(times: List[float], bpms: List[float], 
                       threshold: float = 10.0) -> List[Tuple[float, float]]:
    """找到 BPM 变化点"""
    if len(times) < 2:
        return [(times[0], bpms[0])] if times else []
    
    change_points = [(times[0], bpms[0])]
    
    for i in range(1, len(times)):
        if abs(bpms[i] - bpms[i-1]) >= threshold:
            change_points.append((times[i], bpms[i]))
    
    if change_points[-1][0] != times[-1]:
        change_points.append((times[-1], bpms[-1]))
    
    return change_points


def plot_bpm_timeline(audio_path: str, output_dir: str = ".",
                      window_size: float = 10.0, hop_size: float = 5.0,
                      bpm_threshold: float = 10.0):
    """
    绘制 BPM-时间曲线
    
    Args:
        audio_path: 音频文件路径
        output_dir: 输出目录
        window_size: BPM 检测窗口大小
        hop_size: BPM 检测跳跃大小
        bpm_threshold: BPM 变化检测阈值
    """
    print(f"🎵 加载音频：{audio_path}")
    
    # 检测 BPM 时间线
    times, bpms = detect_bpm_timeline(audio_path, window_size, hop_size)
    
    if not times:
        print("❌ 无法检测到 BPM")
        return
    
    # 找到变化点
    change_points = find_change_points(times, bpms, bpm_threshold)
    
    # 加载音频获取时长
    y, sr = librosa.load(audio_path, sr=None)
    duration = len(y) / sr
    
    # 创建图形
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    fig.suptitle(f'BPM-时间曲线分析 - {Path(audio_path).name}', fontsize=16, fontweight='bold')
    
    # 1. BPM-时间曲线
    print("📊 绘制 BPM-时间曲线...")
    axes[0].plot(times, bpms, 'o-', linewidth=1, markersize=4, label='检测到的 BPM', color='blue')
    
    # 标注变化点
    if len(change_points) > 1:
        cp_times = [p[0] for p in change_points]
        cp_bpms = [p[1] for p in change_points]
        axes[0].plot(cp_times, cp_bpms, 'ro', markersize=10, label='BPM 变化点', zorder=5)
        
        # 标注 BPM 值
        for i, (t, bpm) in enumerate(change_points):
            axes[0].annotate(f'{bpm:.0f}', (t, bpm), textcoords='offset points',
                           xytext=(5, 5), fontsize=9, color='red')
    
    axes[0].axhline(y=180, color='green', linestyle='--', linewidth=2, label='目标 BPM (180)', alpha=0.7)
    axes[0].axhline(y=np.mean(bpms), color='orange', linestyle=':', linewidth=2, 
                   label=f'平均 BPM ({np.mean(bpms):.0f})')
    
    axes[0].set_xlabel('时间 (秒)')
    axes[0].set_ylabel('BPM')
    axes[0].set_title(f'1. BPM-时间曲线 (窗口={window_size}s, 跳跃={hop_size}s)')
    axes[0].set_ylim([min(bpms) - 10, max(bpms) + 10])
    axes[0].legend(loc='upper right')
    axes[0].grid(True, alpha=0.3)
    
    # 2. BPM 直方图
    print("📊 绘制 BPM 分布...")
    axes[1].hist(bpms, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    axes[1].axvline(x=np.mean(bpms), color='red', linestyle='--', linewidth=2, 
                   label=f'平均：{np.mean(bpms):.1f}')
    axes[1].axvline(x=np.median(bpms), color='green', linestyle=':', linewidth=2,
                   label=f'中位数：{np.median(bpms):.1f}')
    axes[1].set_xlabel('BPM')
    axes[1].set_ylabel('出现次数')
    axes[1].set_title('2. BPM 分布直方图')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # 3. BPM 变化幅度
    print("📊 分析 BPM 变化...")
    if len(bpms) > 1:
        bpm_diffs = np.abs(np.diff(bpms))
        diff_times = times[:-1]
        
        axes[2].bar(diff_times, bpm_diffs, width=hop_size, alpha=0.7, color='purple', 
                   label='BPM 变化幅度')
        axes[2].axhline(y=bpm_threshold, color='red', linestyle='--', linewidth=2,
                       label=f'变化阈值 ({bpm_threshold})')
        
        # 标注超过阈值的点
        for i, diff in enumerate(bpm_diffs):
            if diff >= bpm_threshold:
                axes[2].annotate(f'{diff:.1f}', (diff_times[i], diff),
                               textcoords='offset points', xytext=(0, 5),
                               fontsize=8, color='red')
        
        axes[2].set_xlabel('时间 (秒)')
        axes[2].set_ylabel('BPM 变化量')
        axes[2].set_title(f'3. BPM 变化幅度 (检测到 {len([d for d in bpm_diffs if d >= bpm_threshold])} 个显著变化)')
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)
    
    # 添加统计信息文本框
    stats_text = (
        f"统计信息:\n"
        f"• 音频时长：{duration:.2f}秒\n"
        f"• 检测点数：{len(times)}\n"
        f"• 变化点数：{len(change_points)}\n"
        f"• BPM 范围：{min(bpms):.1f} - {max(bpms):.1f}\n"
        f"• 平均 BPM: {np.mean(bpms):.1f}\n"
        f"• BPM 标准差：{np.std(bpms):.1f}"
    )
    
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    axes[0].text(0.02, 0.98, stats_text, transform=axes[0].transAxes, fontsize=10,
                verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    
    # 保存
    output_path = Path(output_dir) / f"{Path(audio_path).stem}_bpm_timeline.png"
    print(f"💾 保存：{output_path}")
    plt.savefig(str(output_path), dpi=150, bbox_inches='tight')
    
    print(f"✅ 完成！")
    
    # 打印总结
    print("\n" + "=" * 60)
    print("BPM 分析总结")
    print("=" * 60)
    print(f"音频时长：{duration:.2f}秒")
    print(f"检测窗口：{window_size}秒")
    print(f"检测跳跃：{hop_size}秒")
    print(f"BPM 采样点：{len(times)}个")
    print(f"BPM 变化点：{len(change_points)}个")
    print(f"BPM 范围：{min(bpms):.1f} - {max(bpms):.1f}")
    print(f"平均 BPM: {np.mean(bpms):.1f}")
    print(f"推荐目标 BPM: {np.median(bpms):.0f} (中位数)")
    print("=" * 60)
    
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description='📈 BPM-时间曲线可视化',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python exp_bpm_timeline.py ./test.mp3
  python exp_bpm_timeline.py ./test.mp3 --window-size 5 --hop-size 2
  python exp_bpm_timeline.py ./test.mp3 --bpm-threshold 5
  python exp_bpm_timeline.py ./test.mp3 --output-dir ./results
        '''
    )
    
    parser.add_argument('audio_file', help='输入音频文件')
    parser.add_argument('--output-dir', type=str, default='.', help='输出目录')
    parser.add_argument('--window-size', type=float, default=10.0,
                        help='BPM 检测窗口大小 秒 (默认：10.0)')
    parser.add_argument('--hop-size', type=float, default=5.0,
                        help='BPM 检测跳跃大小 秒 (默认：5.0)')
    parser.add_argument('--bpm-threshold', type=float, default=10.0,
                        help='BPM 变化检测阈值 (默认：10.0)')
    
    args = parser.parse_args()
    
    # 创建输出目录
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    plot_bpm_timeline(
        args.audio_file, 
        args.output_dir,
        args.window_size,
        args.hop_size,
        args.bpm_threshold
    )


if __name__ == '__main__':
    main()
