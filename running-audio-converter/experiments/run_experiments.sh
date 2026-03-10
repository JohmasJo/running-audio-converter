#!/bin/bash
# 🧪 快速实验脚本
# 一键运行所有可视化分析

set -e

echo "=============================================="
echo "🧪 跑步音频转换器 - 实验分析"
echo "=============================================="
echo ""

# 检查参数
if [ $# -lt 1 ]; then
    echo "用法：./run_experiments.sh <音频文件> [输出目录]"
    echo ""
    echo "示例:"
    echo "  ./run_experiments.sh ./test.mp3"
    echo "  ./run_experiments.sh ./test.mp3 ./results"
    exit 1
fi

AUDIO_FILE="$1"
OUTPUT_DIR="${2:-./experiments/results}"

# 检查文件是否存在
if [ ! -f "$AUDIO_FILE" ]; then
    echo "❌ 错误：文件不存在 - $AUDIO_FILE"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo "📁 输入文件：$AUDIO_FILE"
echo "📂 输出目录：$OUTPUT_DIR"
echo ""

# 运行 FFT 分析
echo "=============================================="
echo "📊 实验 1: FFT 频谱分析"
echo "=============================================="
python3 experiments/exp_fft_visualization.py "$AUDIO_FILE" --output-dir "$OUTPUT_DIR"
echo ""

# 运行 BPM 分析
echo "=============================================="
echo "📈 实验 2: BPM-时间曲线分析"
echo "=============================================="
python3 experiments/exp_bpm_timeline.py "$AUDIO_FILE" --output-dir "$OUTPUT_DIR"
echo ""

# 显示结果
echo "=============================================="
echo "✅ 实验完成！"
echo "=============================================="
echo ""
echo "生成的文件:"
ls -lh "$OUTPUT_DIR"/*.png 2>/dev/null || echo "未找到 PNG 文件"
echo ""
echo "查看结果:"
echo "  FFT 分析：$OUTPUT_DIR/*_fft_analysis.png"
echo "  BPM 分析：$OUTPUT_DIR/*_bpm_timeline.png"
echo ""
echo "提示:"
echo "  - 如果 BPM 变化很大（>20 BPM），建议使用 converter_variable_fast.py"
echo "  - 如果 BPM 相对固定（<10 BPM 变化），建议使用 converter.py"
echo ""
