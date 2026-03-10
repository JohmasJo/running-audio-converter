# 🔧 问题解决指南

## ❗ 常见问题

### 问题 1: "Couldn't find ffmpeg" 警告

**原因：** ffmpeg 未安装或不在 PATH 中

**解决方案：**

#### 方法 A: Conda 安装（推荐）
```bash
# 激活环境
conda activate Audio

# 安装 ffmpeg
conda install -c conda-forge ffmpeg -y
```

#### 方法 B: 系统安装
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows (使用 choco)
choco install ffmpeg
```

#### 方法 C: 使用修复脚本
```bash
cd /home/tomoya/data/running-audio-converter
chmod +x fix_environment.sh
./fix_environment.sh
```

---

### 问题 2: Ctrl+C 无法中断程序

**原因：** tkinter 的 mainloop 默认会捕获 SIGINT 信号

**解决方案：**

已修复！新版本的 `gui_unified.py` 已经添加了信号处理。

**更新方法：**
```bash
cd /home/tomoya/data/running-audio-converter
git pull
```

**如果还是无法中断，尝试：**

1. **使用终端的 Job Control**
   ```bash
   # 按 Ctrl+Z 挂起程序
   Ctrl+Z
   
   # 查看任务
   jobs
   
   # 终止任务
   kill %1
   ```

2. **打开新终端杀死进程**
   ```bash
   # 找到进程 ID
   ps aux | grep gui_unified
   
   # 杀死进程
   kill -9 <PID>
   ```

3. **使用 pkill**
   ```bash
   pkill -f gui_unified.py
   ```

---

## ✅ 完整安装流程

### 1. 激活 conda 环境
```bash
conda activate Audio
```

### 2. 安装 ffmpeg
```bash
conda install -c conda-forge ffmpeg -y
```

### 3. 验证安装
```bash
# 检查 ffmpeg
ffmpeg -version

# 应该看到类似输出：
# ffmpeg version 6.x.x Copyright (c) 2000-2024 the FFmpeg developers
```

### 4. 安装 Python 依赖
```bash
cd /home/tomoya/data/running-audio-converter
pip install -r requirements.txt
```

### 5. 运行 GUI
```bash
python gui_unified.py
```

---

## 🐛 其他问题

### 问题：导入错误 "No module named 'librosa'"

**解决：**
```bash
conda activate Audio
pip install -r requirements.txt
```

### 问题：GPU 版本 "No module named 'cupy'"

**解决：**
```bash
# 检查 CUDA 版本
nvcc --version

# 安装对应的 CuPy
pip install cupy-cuda11x  # CUDA 11
# 或
pip install cupy-cuda12x  # CUDA 12
```

### 问题：tkinter 不可用

**解决：**
```bash
# Conda 安装 tkinter
conda install -c conda-forge tk

# 或者系统安装
sudo apt-get install python3-tk  # Ubuntu/Debian
brew install python-tk           # macOS
```

---

## 📞 仍然有问题？

### 1. 检查环境
```bash
# 查看当前环境
conda info --envs

# 查看已安装的包
conda list

# 检查 ffmpeg 路径
which ffmpeg
```

### 2. 重新创建环境
```bash
# 删除旧环境
conda env remove -n Audio

# 创建新环境
conda create -n Audio python=3.10 -y

# 激活
conda activate Audio

# 安装依赖
conda install -c conda-forge ffmpeg -y
pip install -r requirements.txt
```

### 3. 查看日志
```bash
# 运行并保存错误日志
python gui_unified.py 2>&1 | tee error.log
```

---

## 🎯 快速测试

运行以下命令验证一切正常：

```bash
conda activate Audio

# 测试 ffmpeg
ffmpeg -version

# 测试 librosa
python -c "import librosa; print('librosa OK')"

# 测试 tkinter
python -c "import tkinter; print('tkinter OK')"

# 测试转换器
python -c "from converter import AudioConverter; print('converter OK')"
```

如果所有测试都通过，GUI 应该可以正常运行喵~ (≧ω≦)

---

Made with ❤️ by Niko!
