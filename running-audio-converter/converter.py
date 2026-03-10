#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏃 跑步音频转换器 - 180 BPM Edition
自动将任意音频转换为 180 BPM 版本，专为跑步设计！
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
from pydub.effects import normalize
from scipy import signal


class MetronomeGenerator:
    """节拍器生成器"""
    
    def __init__(self, bpm: int = 180, frequency: int = 1000, volume: float = 0.3):
        self.bpm = bpm
        self.frequency = frequency
        self.volume = volume
        self.sample_rate = 44100
    
    def generate_click(self, duration_ms: int = 50) -> np.ndarray:
        """生成单个节拍音"""
        n_samples = int(self.sample_rate * duration_ms / 1000)
        t = np.linspace(0, duration_ms / 1000, n_samples)
        
        # 生成正弦波
        click = np.sin(2 * np.pi * self.frequency * t)
        
        # 添加包络（淡入淡出）避免爆音
        envelope = np.ones_like(click)
        fade_samples = int(n_samples * 0.1)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        
        click = click * envelope * self.volume
        return click
    
    def generate_track(self, duration_seconds: float) -> np.ndarray:
        """生成完整的节拍器音轨"""
        beats_per_second = self.bpm / 60
        total_beats = int(duration_seconds * beats_per_second) + 1
        beat_interval = self.sample_rate / beats_per_second
        
        # 创建空白音轨
        metronome_track = np.zeros(int(duration_seconds * self.sample_rate))
        
        # 在每个节拍位置添加点击音
        click = self.generate_click()
        for i in range(total_beats):
            start_idx = int(i * beat_interval)
            end_idx = start_idx + len(click)
            if end_idx < len(metronome_track):
                metronome_track[start_idx:end_idx] += click
        
        # 限制振幅避免削波
        metronome_track = np.clip(metronome_track, -0.99, 0.99)
        return metronome_track


class AudioConverter:
    """音频转换器"""
    
    def __init__(self, target_bpm: int = 180):
        self.target_bpm = target_bpm
        self.sample_rate = 44100
    
    def detect_bpm(self, audio_path: str) -> float:
        """检测音频的 BPM"""
        print(f"🎵 正在分析 BPM...")
        
        # 加载音频（只加载前 60 秒用于分析，加快速度）
        y, sr = librosa.load(audio_path, duration=60, sr=None)
        
        # 使用 tempo 检测
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        # librosa 返回的 tempo 可能是数组
        if isinstance(tempo, np.ndarray):
            tempo = tempo[0]
        
        print(f"   检测到 BPM: {tempo:.1f}")
        return float(tempo)
    
    def time_stretch(self, audio_path: str, rate: float) -> Tuple[np.ndarray, int]:
        """时间拉伸音频（不改变音调）"""
        print(f"⚡ 正在时间拉伸 (速率：{rate:.2f}x)...")
        
        # 加载音频
        y, sr = librosa.load(audio_path, sr=None)
        
        # 使用时间拉伸（保持音调）
        y_stretched = librosa.effects.time_stretch(y, rate=rate)
        
        return y_stretched, sr
    
    def mix_audio(self, audio: np.ndarray, metronome: np.ndarray, 
                  audio_volume: float = 1.0, metro_volume: float = 0.3) -> np.ndarray:
        """混合音频和节拍器"""
        # 确保长度一致
        min_len = min(len(audio), len(metronome))
        audio = audio[:min_len]
        metronome = metronome[:min_len]
        
        # 混合
        mixed = audio * audio_volume + metronome * metro_volume
        
        # 限制振幅避免削波
        mixed = np.clip(mixed, -0.99, 0.99)
        
        return mixed
    
    def convert(self, audio_path: str, add_metronome: bool = False,
                metronome_volume: float = 0.3, beat_frequency: int = 1000,
                output_dir: Optional[str] = None) -> str:
        """转换音频文件"""
        input_path = Path(audio_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"文件不存在：{audio_path}")
        
        # 确定输出目录
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = input_path.parent
        
        # 检测 BPM
        original_bpm = self.detect_bpm(audio_path)
        
        if original_bpm <= 0:
            raise ValueError("无法检测到有效的 BPM")
        
        # 计算拉伸率
        stretch_rate = original_bpm / self.target_bpm
        print(f"   拉伸率：{stretch_rate:.4f} ({original_bpm:.1f} → {self.target_bpm} BPM)")
        
        # 时间拉伸
        stretched_audio, sr = self.time_stretch(audio_path, stretch_rate)
        
        # 计算新时长
        duration = len(stretched_audio) / sr
        print(f"   新时长：{duration:.1f} 秒")
        
        # 添加节拍器（如果需要）
        if add_metronome:
            print(f"🎛️ 正在生成节拍器 ({self.target_bpm} BPM, {beat_frequency}Hz)...")
            metro_gen = MetronomeGenerator(
                bpm=self.target_bpm,
                frequency=beat_frequency,
                volume=metronome_volume
            )
            metronome_track = metro_gen.generate_track(duration)
            
            print(f"🎚️ 正在混合音频...")
            final_audio = self.mix_audio(
                stretched_audio, 
                metronome_track,
                audio_volume=1.0,
                metro_volume=metronome_volume
            )
            suffix = f"_{self.target_bpm}bpm_metronome"
        else:
            final_audio = stretched_audio
            suffix = f"_{self.target_bpm}bpm"
        
        # 生成输出文件名
        output_filename = f"{input_path.stem}{suffix}.wav"
        output_file = output_path / output_filename
        
        # 保存文件
        print(f"💾 正在保存：{output_file}")
        sf.write(output_file, final_audio, sr)
        
        print(f"✅ 完成！输出：{output_file}")
        return str(output_file)


def main():
    parser = argparse.ArgumentParser(
        description='🏃 跑步音频转换器 - 将音频转换为 180 BPM 版本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python converter.py your-song.mp3                    # 基础转换
  python converter.py your-song.mp3 --metronome        # 添加节拍器
  python converter.py your-song.mp3 --target-bpm 170   # 指定目标 BPM
  python converter.py *.mp3 --metronome                # 批量处理
        '''
    )
    
    parser.add_argument('files', nargs='+', help='输入音频文件')
    parser.add_argument('--target-bpm', type=int, default=180,
                        help='目标 BPM (默认：180)')
    parser.add_argument('--metronome', action='store_true',
                        help='添加节拍器音轨')
    parser.add_argument('--metronome-volume', type=float, default=0.3,
                        help='节拍器音量 0.0-1.0 (默认：0.3)')
    parser.add_argument('--beat-frequency', type=int, default=1000,
                        help='节拍器频率 Hz (默认：1000)')
    parser.add_argument('--output-dir', type=str, default=None,
                        help='输出目录 (默认：与原文件同目录)')
    
    args = parser.parse_args()
    
    # 打印标题
    print("=" * 60)
    print("🏃 跑步音频转换器 - 180 BPM Edition")
    print("=" * 60)
    print()
    
    # 创建转换器
    converter = AudioConverter(target_bpm=args.target_bpm)
    
    # 处理每个文件
    success_count = 0
    error_count = 0
    
    for file_path in args.files:
        try:
            print(f"\n📁 处理：{file_path}")
            print("-" * 40)
            
            output_file = converter.convert(
                file_path,
                add_metronome=args.metronome,
                metronome_volume=args.metronome_volume,
                beat_frequency=args.beat_frequency,
                output_dir=args.output_dir
            )
            success_count += 1
            
        except Exception as e:
            print(f"❌ 错误：{e}")
            error_count += 1
    
    # 打印总结
    print("\n" + "=" * 60)
    print(f"✅ 完成！成功：{success_count}, 失败：{error_count}")
    print("=" * 60)
    
    return 0 if error_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
