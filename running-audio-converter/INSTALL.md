# 📦 安装指南

## 方法一：使用 pip（推荐）

```bash
# 进入项目目录
cd /home/tomoya/data/running-audio-converter

# 安装依赖
pip install -r requirements.txt

# 或者使用 pip3
pip3 install -r requirements.txt
```

## 方法二：使用虚拟环境（推荐用于隔离）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

## 方法三：使用 conda

```bash
# 创建环境
conda create -n running-audio python=3.10

# 激活环境
conda activate running-audio

# 安装依赖
pip install -r requirements.txt
```

## 方法四：逐个安装

如果 requirements.txt 有问题，可以逐个安装：

```bash
pip install librosa
pip install pydub
pip install numpy
pip install scipy
pip install soundfile
pip install audioread
```

## ⚠️ 额外依赖

### Linux

可能需要安装 ffmpeg：

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch
sudo pacman -S ffmpeg
```

### macOS

```bash
brew install ffmpeg
```

### Windows

下载并安装 ffmpeg：
https://ffmpeg.org/download.html

或者使用 choco：
```bash
choco install ffmpeg
```

## 🚀 运行

### 命令行版本

```bash
# 基础用法
python converter.py your-song.mp3

# 添加节拍器
python converter.py your-song.mp3 --metronome

# 查看帮助
python converter.py --help
```

### GUI 版本

```bash
python gui_converter.py
```

## 🔧 常见问题

### 问题：`librosa` 安装失败

尝试：
```bash
pip install librosa --no-cache-dir
```

### 问题：`pydub` 无法找到 ffmpeg

确保 ffmpeg 已安装并在 PATH 中：
```bash
ffmpeg -version  # 检查是否安装成功
```

### 问题：权限错误

使用 `--user` 标志：
```bash
pip install -r requirements.txt --user
```

### 问题：Python 版本不兼容

确保使用 Python 3.8+：
```bash
python3 --version
```

---

如有问题，请检查错误信息并尝试上述解决方案喵~
