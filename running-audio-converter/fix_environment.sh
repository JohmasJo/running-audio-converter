#!/bin/bash
# 🔧 修复环境和依赖问题

set -e

echo "=============================================="
echo "🔧 跑步音频转换器 - 环境修复脚本"
echo "=============================================="
echo ""

# 检测 conda
if command -v conda &> /dev/null; then
    echo "✅ 检测到 conda"
    CONDA_CMD="conda"
elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    echo "✅ 找到 conda 安装"
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
    CONDA_CMD="conda"
elif [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    echo "✅ 找到 anaconda 安装"
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
    CONDA_CMD="conda"
else
    echo "❌ 未检测到 conda"
    echo ""
    echo "请手动激活 Audio 环境后运行："
    echo "  conda activate Audio"
    echo "  conda install -c conda-forge ffmpeg -y"
    exit 1
fi

# 激活 Audio 环境
echo ""
echo "📦 激活 Audio 环境..."
$CONDA_CMD activate Audio

# 检查 ffmpeg
echo ""
echo "🔍 检查 ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg 已安装"
    ffmpeg -version | head -1
else
    echo "❌ ffmpeg 未安装"
    echo ""
    echo "📦 正在安装 ffmpeg..."
    $CONDA_CMD install -c conda-forge ffmpeg -y
fi

# 验证 ffmpeg
echo ""
echo "🔍 验证 ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ ffmpeg 安装成功"
    ffmpeg -version | head -1
else
    echo "❌ ffmpeg 安装失败"
    echo ""
    echo "请手动运行："
    echo "  conda activate Audio"
    echo "  conda install -c conda-forge ffmpeg -y"
    exit 1
fi

# 检查 Python 依赖
echo ""
echo "🔍 检查 Python 依赖..."
cd "$(dirname "$0")"

if python -c "import librosa" 2>/dev/null; then
    echo "✅ librosa 已安装"
else
    echo "⚠️  librosa 未安装，正在安装..."
    pip install -r requirements.txt
fi

# 总结
echo ""
echo "=============================================="
echo "✅ 环境修复完成！"
echo "=============================================="
echo ""
echo "使用方法:"
echo "  conda activate Audio"
echo "  cd /home/tomoya/data/running-audio-converter"
echo "  python gui_unified.py"
echo ""
