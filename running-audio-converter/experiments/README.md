# 🧪 实验与可视化

这个文件夹包含用于验证算法的数据实验工具。

## 📊 可视化工具

### 1. FFT 频谱分析

**文件：** `exp_fft_visualization.py`

**用途：** 可视化音频的频域特征，验证 BPM 检测的基础数据

**生成内容：**
- 原始音频波形
- 波形局部放大
- 频谱图（Spectrogram）
- 平均频谱
- Onset Envelope（用于 BPM 检测）
- Onset Envelope 的 FFT（检测节奏周期性）

**使用方法：**
```bash
# 基础用法
python exp_fft_visualization.py ./test.mp3

# 指定输出目录
python exp_fft_visualization.py ./test.mp3 --output-dir ./results

# 调整 FFT 参数
python exp_fft_visualization.py ./test.mp3 --nfft 4096 --hop-length 1024
```

**输出：** `test_fft_analysis.png`

---

### 2. BPM-时间曲线分析

**文件：** `exp_bpm_timeline.py`

**用途：** 分析 BPM 随时间的变化，验证变速检测算法

**生成内容：**
- BPM-时间曲线（带变化点标注）
- BPM 分布直方图
- BPM 变化幅度分析
- 统计信息文本框

**使用方法：**
```bash
# 基础用法
python exp_bpm_timeline.py ./test.mp3

# 更精细的检测（5 秒窗口，2 秒跳跃）
python exp_bpm_timeline.py ./test.mp3 --window-size 5 --hop-size 2

# 调整变化检测灵敏度
python exp_bpm_timeline.py ./test.mp3 --bpm-threshold 5

# 指定输出目录
python exp_bpm_timeline.py ./test.mp3 --output-dir ./results
```

**输出：** `test_bpm_timeline.png`

---

## 🔬 实验流程

### 验证算法可行性的步骤：

1. **运行 FFT 分析**
   ```bash
   python exp_fft_visualization.py ./test.mp3 --output-dir ./results
   ```
   
2. **检查 Onset Envelope**
   - 查看第 5 个子图：Onset Envelope 是否清晰
   - 查看第 6 个子图：FFT 是否有明显的峰值（对应 BPM）

3. **运行 BPM-时间曲线分析**
   ```bash
   python exp_bpm_timeline.py ./test.mp3 --output-dir ./results
   ```

4. **分析 BPM 变化**
   - 查看 BPM 范围：如果范围很大（如 80-150），说明是变速歌曲
   - 查看变化点数量：如果有很多变化点，需要使用变速版本
   - 查看平均 BPM：决定目标 BPM 的参考

5. **选择合适的转换器**
   - **固定 BPM** → `converter.py`
   - **变速歌曲** → `converter_variable_fast.py` 或 `converter_variable_gpu.py`

---

## 📈 参数调优指南

### FFT 分析参数

| 参数 | 默认值 | 说明 | 调整建议 |
|------|--------|------|----------|
| `--nfft` | 2048 | FFT 窗口大小 | 更大的值 = 更高的频率分辨率 |
| `--hop-length` | 512 | 跳跃长度 | 更小的值 = 更高的时间分辨率 |

### BPM 检测参数

| 参数 | 默认值 | 说明 | 调整建议 |
|------|--------|------|----------|
| `--window-size` | 10.0 | 检测窗口大小 | 更小的值 = 更灵敏，但噪声更多 |
| `--hop-size` | 5.0 | 检测跳跃大小 | 更小的值 = 更密集采样 |
| `--bpm-threshold` | 10.0 | 变化检测阈值 | 更小的值 = 检测更多变化点 |

### 推荐配置

**快节奏电子音乐：**
```bash
python exp_bpm_timeline.py song.mp3 --window-size 5 --hop-size 2 --bpm-threshold 5
```

**慢节奏古典音乐：**
```bash
python exp_bpm_timeline.py song.mp3 --window-size 15 --hop-size 8 --bpm-threshold 15
```

**流行音乐（中等节奏）：**
```bash
python exp_bpm_timeline.py song.mp3 --window-size 10 --hop-size 5 --bpm-threshold 10
```

---

## 📊 示例输出解读

### FFT 分析图

1. **原始波形** - 查看整体音量变化
2. **波形局部放大** - 观察节拍细节
3. **频谱图** - 查看频率分布随时间变化
4. **平均频谱** - 识别主要频率成分
5. **Onset Envelope** ⭐ - ** BPM 检测的关键**，应该有明显的周期性
6. **Onset FFT** ⭐ - **峰值对应的频率 × 60 = BPM**

### BPM-时间曲线图

1. **BPM-时间曲线** - 主图，查看 BPM 如何随时间变化
   - 蓝色线：检测到的 BPM
   - 红色点：BPM 变化点
   - 绿色虚线：目标 BPM（180）
   - 橙色虚线：平均 BPM

2. **BPM 分布** - 查看 BPM 的统计分布
   - 如果分布很窄 → 固定 BPM 歌曲
   - 如果分布很宽 → 变速歌曲

3. **BPM 变化幅度** - 查看变化的剧烈程度
   - 红色虚线：变化阈值
   - 超过阈值的点会被标记为变化点

---

## 🧪 实验案例

### 案例 1：验证固定 BPM 歌曲

```bash
# 运行分析
python exp_bpm_timeline.py fixed_bpm_song.mp3

# 预期结果:
# - BPM 范围窄（如 118-122）
# - 变化点少（1-2 个）
# - 标准差小（<5）

# 推荐使用:
python converter.py fixed_bpm_song.mp3 --target-bpm 180
```

### 案例 2：验证变速歌曲

```bash
# 运行分析
python exp_bpm_timeline.py variable_bpm_song.mp3 --window-size 5

# 预期结果:
# - BPM 范围宽（如 90-150）
# - 变化点多（>5 个）
# - 标准差大（>15）

# 推荐使用:
python converter_variable_fast.py variable_bpm_song.mp3 --target-bpm 180
```

### 案例 3：检测 BPM 渐变

```bash
# 运行分析（使用小窗口）
python exp_bpm_timeline.py gradual_song.mp3 --window-size 5 --hop-size 2 --bpm-threshold 5

# 预期结果:
# - BPM 随时间逐渐变化
# - 变化点连续分布

# 推荐使用:
python converter_variable_gpu.py gradual_song.mp3 --window-size 15 --hop-size 8
```

---

## 📝 依赖

确保安装了以下库：

```bash
pip install numpy librosa matplotlib scipy
```

---

Made with ❤️ for data-driven music processing!
