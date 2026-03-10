#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏃 跑步音频转换器 - 变速歌曲版本
支持处理 BPM 随时间变化的歌曲！

原理：
1. 使用滑动窗口检测 BPM 随时间变化
2. 找到 BPM 变化点，分段处理
3. 每段独立拉伸到目标 BPM
4. 使用交叉渐变平滑连接各段
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import warnings

import numpy as np
import librosa
import soundfile as sf
from scipy import signal
from scipy.ndimage import median_filter

# 忽略一些警告
warnings.filterwarnings('ignore', category=UserWarning)


class BPMTimeline:
    """BPM 时间线检测器"""
    
    def __init__(self, window_size: float = 10.0, hop_size: float = 5.0):
        """
        初始化 BPM 检测器
        
        Args:
            window_size: 窗口大小（秒）
            hop_size: 窗口跳跃大小（秒）
        """
        self.window_size = window_size
        self.hop_size = hop_size
    
    def detect(self, audio_path: str) -> Tuple[List[float], List[float]]:
        """
        检测 BPM 随时间变化
        
        Returns:
            (times, bpms): 时间点和对应的 BPM
        """
        print(f"🎵 正在检测 BPM 时间线 (窗口={self.window_size}s, 跳跃={self.hop_size}s)...")
        
        # 加载音频
        y, sr = librosa.load(audio_path, sr=None)
        duration = len(y) / sr
        
        # 计算窗口和跳跃的样本数
        window_samples = int(self.window_size * sr)
        hop_samples = int(self.hop_size * sr)
        
        times = []
        bpms = []
        
        # 滑动窗口检测 BPM
        num_windows = max(1, int((len(y) - window_samples) / hop_samples) + 1)
        
        for i in range(num_windows):
            start = i * hop_samples
            end = start + window_samples
            
            if end > len(y):
                end = len(y)
            
            segment = y[start:end]
            
            # 计算当前窗口的 BPM
            try:
                tempo, _ = librosa.beat.beat_track(y=segment, sr=sr)
                if isinstance(tempo, np.ndarray):
                    tempo = tempo[0]
                
                # 过滤不合理的 BPM
                if 60 <= tempo <= 220:
                    time = start / sr
                    times.append(time)
                    bpms.append(float(tempo))
                    
            except Exception:
                pass
            
            # 进度显示
            if (i + 1) % 10 == 0 or i == num_windows - 1:
                progress = (i + 1) / num_windows * 100
                print(f"   进度：{progress:.1f}% ({i+1}/{num_windows})")
        
        # 使用中值滤波平滑 BPM 曲线
        if len(bpms) > 3:
            bpms_smooth = median_filter(bpms, size=3)
            bpms = bpms_smooth.tolist()
        
        print(f"   检测到 {len(times)} 个 BPM 采样点")
        
        return times, bpms
    
    def find_change_points(self, times: List[float], bpms: List[float], 
                          threshold: float = 10.0) -> List[Tuple[float, float]]:
        """
        找到 BPM 变化点
        
        Args:
            times: 时间点
            bpms: BPM 值
            threshold: BPM 变化阈值（超过这个值认为是变化点）
        
        Returns:
            [(time, bpm), ...] 变化点列表
        """
        if len(times) < 2:
            return [(times[0], bpms[0])] if times else []
        
        print(f"🔍 正在分析 BPM 变化点 (阈值={threshold} BPM)...")
        
        change_points = []
        
        # 第一个点总是添加
        change_points.append((times[0], bpms[0]))
        
        # 找变化点
        for i in range(1, len(times)):
            bpm_diff = abs(bpms[i] - bpms[i-1])
            
            if bpm_diff >= threshold:
                change_points.append((times[i], bpms[i]))
        
        # 最后一个点如果不是变化点也添加
        if change_points[-1][0] != times[-1]:
            change_points.append((times[-1], bpms[-1]))
        
        print(f"   找到 {len(change_points)} 个变化点")
        
        return change_points


class AudioSegmentProcessor:
    """音频分段处理器"""
    
    def __init__(self, target_bpm: int = 180, crossfade_duration: float = 2.0):
        """
        初始化处理器
        
        Args:
            target_bpm: 目标 BPM
            crossfade_duration: 交叉渐变时长（秒）
        """
        self.target_bpm = target_bpm
        self.crossfade_duration = crossfade_duration
    
    def stretch_segment(self, audio: np.ndarray, sr: int, 
                       original_bpm: float) -> np.ndarray:
        """
        拉伸音频片段到目标 BPM
        
        Args:
            audio: 音频数据
            sr: 采样率
            original_bpm: 原始 BPM
        
        Returns:
            拉伸后的音频
        """
        if original_bpm <= 0:
            return audio
        
        # 计算拉伸率
        rate = original_bpm / self.target_bpm
        
        # 时间拉伸
        stretched = librosa.effects.time_stretch(audio, rate=rate)
        
        return stretched
    
    def crossfade(self, audio1: np.ndarray, audio2: np.ndarray, 
                 sr: int, duration: float) -> np.ndarray:
        """
        交叉渐变连接两段音频
        
        Args:
            audio1: 第一段音频
            audio2: 第二段音频
            sr: 采样率
            duration: 渐变时长（秒）
        
        Returns:
            连接后的音频
        """
        fade_samples = int(duration * sr)
        
        # 确保渐变长度不超过音频长度
        fade_samples = min(fade_samples, len(audio1) // 4, len(audio2) // 4)
        
        if fade_samples < 100:
            # 太短了，直接拼接
            return np.concatenate([audio1, audio2])
        
        # 创建渐变曲线
        fade_out = np.linspace(1, 0, fade_samples) ** 2  # 指数渐变
        fade_in = np.linspace(0, 1, fade_samples) ** 2
        
        # 重叠部分
        overlap1 = audio1[-fade_samples:] * fade_out
        overlap2 = audio2[:fade_samples] * fade_in
        overlap = overlap1 + overlap2
        
        # 拼接：audio1(去掉尾部) + overlap + audio2(去掉头部)
        result = np.concatenate([
            audio1[:-fade_samples],
            overlap,
            audio2[fade_samples:]
        ])
        
        return result
    
    def process(self, audio_path: str, change_points: List[Tuple[float, float]],
               output_path: str):
        """
        处理整个音频文件
        
        Args:
            audio_path: 输入文件路径
            change_points: BPM 变化点 [(time, bpm), ...]
            output_path: 输出文件路径
        """
        print(f"⚡ 正在分段处理音频...")
        
        # 加载完整音频
        y, sr = librosa.load(audio_path, sr=None)
        duration = len(y) / sr
        
        print(f"   音频时长：{duration:.1f}秒")
        print(f"   分段数：{len(change_points)}")
        
        # 处理每一段
        segments = []
        
        for i, (start_time, bpm) in enumerate(change_points):
            # 确定段的结束时间
            if i < len(change_points) - 1:
                end_time = change_points[i + 1][0]
            else:
                end_time = duration
            
            segment_duration = end_time - start_time
            
            print(f"\n   段 {i+1}: {start_time:.1f}s - {end_time:.1f}s "
                  f"(时长={segment_duration:.1f}s, BPM={bpm:.1f})")
            
            # 提取这段音频
            start_sample = int(start_time * sr)
            end_sample = int(end_time * sr)
            segment_audio = y[start_sample:end_sample]
            
            # 拉伸到目标 BPM
            stretched = self.stretch_segment(segment_audio, sr, bpm)
            segments.append(stretched)
            
            print(f"      拉伸后时长：{len(stretched)/sr:.1f}s")
        
        # 连接所有段（带交叉渐变）
        print(f"\n🔗 正在连接各段...")
        final_audio = segments[0]
        
        for i in range(1, len(segments)):
            final_audio = self.crossfade(
                final_audio, 
                segments[i], 
                sr, 
                self.crossfade_duration
            )
            print(f"   已连接段 {i+1}/{len(segments)}")
        
        # 保存
        print(f"\n💾 正在保存：{output_path}")
        sf.write(output_path, final_audio, sr)
        
        final_duration = len(final_audio) / sr
        print(f"✅ 完成！输出时长：{final_duration:.1f}秒")
        
        return output_path


class VariableBPMConverter:
    """变速歌曲转换器（主类）"""
    
    def __init__(self, target_bpm: int = 180, 
                 window_size: float = 10.0,
                 hop_size: float = 5.0,
                 bpm_threshold: float = 10.0,
                 crossfade_duration: float = 2.0):
        """
        初始化转换器
        
        Args:
            target_bpm: 目标 BPM
            window_size: BPM 检测窗口大小（秒）
            hop_size: BPM 检测跳跃大小（秒）
            bpm_threshold: BPM 变化检测阈值
            crossfade_duration: 交叉渐变时长（秒）
        """
        self.target_bpm = target_bpm
        self.bpm_detector = BPMTimeline(window_size, hop_size)
        self.processor = AudioSegmentProcessor(target_bpm, crossfade_duration)
        self.bpm_threshold = bpm_threshold
    
    def convert(self, audio_path: str, output_dir: Optional[str] = None) -> str:
        """
        转换音频文件
        
        Args:
            audio_path: 输入文件路径
            output_dir: 输出目录
        
        Returns:
            输出文件路径
        """
        input_path = Path(audio_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"文件不存在：{audio_path}")
        
        # 确定输出路径
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = input_path.parent
        
        # 生成输出文件名
        output_filename = f"{input_path.stem}_variable_{self.target_bpm}bpm.wav"
        output_file = output_path / output_filename
        
        print("=" * 60)
        print("🏃 跑步音频转换器 - 变速歌曲版本")
        print("=" * 60)
        print(f"\n📁 输入：{audio_path}")
        print(f"🎯 目标 BPM: {self.target_bpm}")
        print()
        
        # 步骤 1: 检测 BPM 时间线
        times, bpms = self.bpm_detector.detect(audio_path)
        
        if len(times) == 0:
            raise ValueError("无法检测到 BPM 信息")
        
        # 步骤 2: 找到 BPM 变化点
        change_points = self.bpm_detector.find_change_points(
            times, bpms, self.bpm_threshold
        )
        
        # 步骤 3: 分段处理
        self.processor.process(audio_path, change_points, str(output_file))
        
        print("\n" + "=" * 60)
        print("✅ 转换完成！")
        print("=" * 60)
        
        return str(output_file)


def main():
    parser = argparse.ArgumentParser(
        description='🏃 跑步音频转换器 - 变速歌曲版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 基础用法（自动检测 BPM 变化）
  python converter_variable.py your-song.mp3

  # 自定义窗口大小（更精细的检测）
  python converter_variable.py your-song.mp3 --window-size 5 --hop-size 2

  # 调整 BPM 变化检测灵敏度
  python converter_variable.py your-song.mp3 --bpm-threshold 5

  # 添加节拍器
  python converter_variable.py your-song.mp3 --metronome

  # 指定输出目录
  python converter_variable.py your-song.mp3 --output-dir ./running-mix
        '''
    )
    
    parser.add_argument('files', nargs='+', help='输入音频文件')
    parser.add_argument('--target-bpm', type=int, default=180,
                        help='目标 BPM (默认：180)')
    parser.add_argument('--window-size', type=float, default=10.0,
                        help='BPM 检测窗口大小 秒 (默认：10.0)')
    parser.add_argument('--hop-size', type=float, default=5.0,
                        help='BPM 检测跳跃大小 秒 (默认：5.0)')
    parser.add_argument('--bpm-threshold', type=float, default=10.0,
                        help='BPM 变化检测阈值 (默认：10.0)')
    parser.add_argument('--crossfade-duration', type=float, default=2.0,
                        help='交叉渐变时长 秒 (默认：2.0)')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='输出目录')
    parser.add_argument('--metronome', action='store_true',
                        help='添加节拍器音轨')
    parser.add_argument('--metronome-volume', type=float, default=0.3,
                        help='节拍器音量 0.0-1.0 (默认：0.3)')
    parser.add_argument('--beat-frequency', type=int, default=1000,
                        help='节拍器频率 Hz (默认：1000)')
    
    args = parser.parse_args()
    
    # 打印标题
    print("=" * 60)
    print("🏃 跑步音频转换器 - 变速歌曲版本")
    print("=" * 60)
    print()
    
    # 处理每个文件
    success_count = 0
    error_count = 0
    
    for file_path in args.files:
        try:
            print(f"\n📁 处理：{file_path}")
            print("-" * 40)
            
            # 创建转换器
            converter = VariableBPMConverter(
                target_bpm=args.target_bpm,
                window_size=args.window_size,
                hop_size=args.hop_size,
                bpm_threshold=args.bpm_threshold,
                crossfade_duration=args.crossfade_duration
            )
            
            # 转换
            output_file = converter.convert(file_path, args.output_dir)
            
            # 添加节拍器（如果需要）
            if args.metronome:
                from converter import MetronomeGenerator
                
                print(f"\n🎛️ 正在添加节拍器...")
                y, sr = sf.read(output_file)
                duration = len(y) / sr
                
                metro_gen = MetronomeGenerator(
                    bpm=args.target_bpm,
                    frequency=args.beat_frequency,
                    volume=args.metronome_volume
                )
                metronome_track = metro_gen.generate_track(duration)
                
                # 混合
                min_len = min(len(y), len(metronome_track))
                mixed = y[:min_len] * 1.0 + metronome_track[:min_len] * args.metronome_volume
                mixed = np.clip(mixed, -0.99, 0.99)
                
                # 保存
                output_path = Path(output_file)
                metronome_file = output_path.parent / f"{output_path.stem}_metronome.wav"
                sf.write(str(metronome_file), mixed, sr)
                print(f"✅ 节拍器版本：{metronome_file}")
            
            success_count += 1
            
        except Exception as e:
            print(f"❌ 错误：{e}")
            import traceback
            traceback.print_exc()
            error_count += 1
    
    # 打印总结
    print("\n" + "=" * 60)
    print(f"✅ 完成！成功：{success_count}, 失败：{error_count}")
    print("=" * 60)
    
    return 0 if error_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
