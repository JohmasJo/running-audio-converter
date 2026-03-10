# 🏃 跑步音频转换器 - 180 BPM Edition

自动将任意音频转换为 180 BPM 版本，专为跑步设计！

## ✨ 功能特点

### 标准版本 (`converter.py`)
- 🎵 **自动 BPM 检测** - 智能分析音频原始节奏
- ⚡ **时间拉伸** - 调整到 180 BPM 而不改变音调
- 🎛️ **节拍器** - 可选添加清晰的节拍提示音
- 📁 **批量处理** - 支持一次处理多个文件
- 🎧 **高质量输出** - 保持原始音质

### 变速歌曲版本 (`converter_variable.py`) 🆕
- 📊 **滑动窗口 BPM 检测** - 每 10 秒检测一次 BPM 变化
- 📈 **BPM 时间线分析** - 自动找到 BPM 变化点
- 🔀 **分段处理** - 每段独立拉伸到目标 BPM
- 🌊 **交叉渐变** - 平滑连接各段，无接缝
- ⚙️ **可调节参数** - 窗口大小、灵敏度、渐变时长

### GPU 加速版本 (`converter_variable_gpu.py`) ⚡
- 🚀 **GPU 并行计算** - 使用 CuPy 加速 FFT 和矩阵运算
- ⚡ **10-50 倍速度提升** - 5 分钟歌曲只需 10-30 秒
- 🎯 **相同精度** - 结果与 CPU 版本一致
- 💻 **NVIDIA 显卡支持** - 需要 CUDA 11/12

## 🖥️ 图形界面（推荐！）

### 统一 GUI 界面

```bash
# 启动统一 GUI（整合所有转换器）
python gui_unified.py
```

**功能特点：**
- 🎯 **4 种转换器选择** - 标准/变速/快速/GPU 加速
- 📁 **批量文件处理** - 一次添加多个文件
- ⚙️ **完整参数控制** - 所有参数可调
- 📊 **实时进度显示** - 可视化处理进度
- 📝 **详细日志输出** - 查看处理详情

---

## 📦 安装依赖

### 前置要求

**必须安装 ffmpeg**：

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# 从 https://ffmpeg.org/download.html 下载并添加到 PATH
# 或使用 choco: choco install ffmpeg
```

### 安装 Python 依赖

```bash
pip install -r requirements.txt
```

## 🚀 命令行用法

### 🎵 标准版本（固定 BPM 歌曲）

```bash
# 基础用法（无节拍器）
python converter.py your-song.mp3

# 添加节拍器
python converter.py your-song.mp3 --metronome

# 指定目标 BPM（默认 180）
python converter.py your-song.mp3 --target-bpm 170

# 批量处理
python converter.py *.mp3 --metronome

# 指定输出目录
python converter.py your-song.mp3 --output-dir ./running-mix
```

### 🎶 变速歌曲版本（BPM 变化的歌曲）

```bash
# 基础用法（自动检测 BPM 变化）
python converter_variable.py your-song.mp3

# 添加节拍器
python converter_variable.py your-song.mp3 --metronome

# 自定义窗口大小（更精细的检测）
python converter_variable.py your-song.mp3 --window-size 5 --hop-size 2

# 调整 BPM 变化检测灵敏度
python converter_variable.py your-song.mp3 --bpm-threshold 5

# 指定目标 BPM
python converter_variable.py your-song.mp3 --target-bpm 175
```

### ⚡ GPU 加速版本（NVIDIA 显卡）

```bash
# 安装 GPU 支持
pip install cupy-cuda11x  # CUDA 11
# 或
pip install cupy-cuda12x  # CUDA 12

# GPU 加速处理（速度提升 10-50 倍！）
python converter_variable_gpu.py your-song.mp3

# 添加节拍器
python converter_variable_gpu.py your-song.mp3 --metronome

# 更精细的检测
python converter_variable_gpu.py your-song.mp3 --window-size 15 --hop-size 8
```

## 📋 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--metronome` | 添加节拍器音轨 | 关闭 |
| `--target-bpm` | 目标 BPM | 180 |
| `--output-dir` | 输出目录 | 原目录 |
| `--metronome-volume` | 节拍器音量 (0.0-1.0) | 0.3 |
| `--beat-frequency` | 节拍器频率 (Hz) | 1000 |

## 🎯 输出文件

处理后的文件会命名为：`原文件名_180bpm.wav`
如果添加了节拍器：`原文件名_180bpm_metronome.wav`

## ⚠️ 注意事项

- 处理时间取决于音频长度，长音频可能需要几分钟
- 建议使用 MP3 或 WAV 格式输入
- 输出格式为 WAV（无损）

## 📝 依赖

- Python 3.8+
- librosa (音频分析)
- pydub (音频处理)
- numpy (数值计算)
- scipy (信号处理)

---
Made with ❤️ for runners!
