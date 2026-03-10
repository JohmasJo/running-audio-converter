# 🏃 跑步音频转换器 - 快速开始

## 📦 第一步：安装 ffmpeg

**这是必须的！** 两个版本都需要 ffmpeg。

### Ubuntu/Debian
```bash
sudo apt-get update && sudo apt-get install ffmpeg
```

### macOS
```bash
brew install ffmpeg
```

### Windows
1. 访问 https://ffmpeg.org/download.html
2. 下载并解压
3. 将 `bin` 目录添加到系统 PATH

### 验证安装
```bash
ffmpeg -version
```

---

## 🚀 第二步：安装并运行

```bash
cd /home/tomoya/data/running-audio-converter

# 安装依赖
pip install -r requirements.txt

# 使用（无节拍器）
python3 converter.py your-song.mp3

# 使用（添加节拍器）
python3 converter.py your-song.mp3 --metronome

# 打开 GUI
python3 gui_converter.py
```

---

## 🎯 常用命令

### 基础转换
```bash
python3 converter.py song.mp3
```

### 添加节拍器
```bash
python3 converter.py song.mp3 --metronome
```

### 自定义目标 BPM
```bash
python3 converter.py song.mp3 --target-bpm 170
```

### 批量处理
```bash
python3 converter.py *.mp3 --metronome
```

### 指定输出目录
```bash
python3 converter.py song.mp3 --output-dir ./running-mix
```

---

## 📊 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--target-bpm` | 目标 BPM | 180 |
| `--metronome` | 添加节拍器音轨 | 关闭 |
| `--metronome-volume` | 节拍器音量 (0.0-1.0) | 0.3 |
| `--beat-frequency` | 节拍器频率 (Hz) | 1000 |
| `--output-dir` | 输出目录 | 原目录 |

---

## 💡 使用技巧

### 1. 确定原始 BPM
- 查看音乐网站信息（网易云、QQ 音乐等）
- 使用在线 BPM 检测工具
- 使用手机 APP（如 "BPM Counter"）

### 2. 选择合适的目标 BPM
- **180 BPM**：黄金步频，适合大多数跑者
- **170-175 BPM**：初跑者或轻松跑
- **185-190 BPM**：进阶跑者或间歇跑

### 3. 节拍器设置
- **音量**：0.2-0.4（能听到但不盖过音乐）
- **频率**：800-1200 Hz（清晰但不刺耳）

### 4. 批量处理跑步歌单
```bash
# 创建输出目录
mkdir running-playlist

# 批量转换整个歌单
python3 converter.py ./my-playlist/*.mp3 --metronome --output-dir ./running-playlist
```

---

## ⚠️ 常见问题

### Q: 转换后音质变差？
A: 输出使用 WAV 格式（无损），音质不会下降。如果输入是 MP3，会有 MP3 本身的压缩损失。

### Q: 转换速度很慢？
A: 时间拉伸是计算密集型操作。长音频（>5 分钟）可能需要几分钟。

### Q: BPM 检测不准确？
A: 自动检测对某些音乐类型（如古典、爵士）可能不准确。建议手动指定原始 BPM。

### Q: 节拍器声音太小/太大？
A: 使用 `--metronome-volume` 调整，推荐值 0.2-0.4。

### Q: 想要其他 BPM 怎么办？
A: 使用 `--target-bpm` 参数，例如 `--target-bpm 170`。

---

## 🎉 开始享受跑步吧！

转换完成后，把文件传到手机或播放器，跟着 180 BPM 的节奏奔跑吧！🏃‍♂️💨

---

Made with ❤️ by Niko for runners!
