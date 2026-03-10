#!/bin/bash
# 🏃 跑步音频转换器 - 快速开始脚本

set -e

echo "=============================================="
echo "🏃 跑步音频转换器 - 环境检查"
echo "=============================================="
echo ""

# 检查 ffmpeg
echo "📦 检查 ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "   ✅ ffmpeg 已安装"
    ffmpeg -version | head -1
else
    echo "   ❌ ffmpeg 未安装"
    echo ""
    echo "   请安装 ffmpeg:"
    echo "   - Ubuntu/Debian: sudo apt-get install ffmpeg"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Windows: 从 https://ffmpeg.org/download.html 下载"
    echo ""
    exit 1
fi

echo ""

# 检查 Python
echo "🐍 检查 Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "   ✅ $PYTHON_VERSION"
    
    # 检查 pip
    if python3 -m pip --version &> /dev/null; then
        echo "   ✅ pip 可用"
        
        # 检查关键包
        echo ""
        echo "📦 检查 Python 依赖..."
        
        for pkg in librosa pydub numpy scipy soundfile; do
            if python3 -c "import $pkg" 2>/dev/null; then
                echo "   ✅ $pkg"
            else
                echo "   ⚠️  $pkg 未安装"
                MISSING_PYTHON=true
            fi
        done
        
        if [ "$MISSING_PYTHON" = true ]; then
            echo ""
            echo "   是否安装缺失的 Python 依赖？(y/n)"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                echo "   正在安装..."
                python3 -m pip install -r requirements.txt --user
                echo "   ✅ 安装完成"
            fi
        fi
    else
        echo "   ⚠️  pip 不可用"
    fi
else
    echo "   ❌ Python3 未安装"
fi

echo ""

# 检查 Node.js
echo "🟢 检查 Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "   ✅ Node.js $NODE_VERSION"
    
    # 检查 npm
    if command -v npm &> /dev/null; then
        echo "   ✅ npm 可用"
        
        # 检查 node_modules
        if [ -d "node_modules" ]; then
            echo "   ✅ node_modules 已存在"
        else
            echo "   ⚠️  node_modules 不存在"
            echo ""
            echo "   是否安装 Node.js 依赖？(y/n)"
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                echo "   正在安装..."
                npm install
                echo "   ✅ 安装完成"
            fi
        fi
    else
        echo "   ⚠️  npm 不可用"
    fi
else
    echo "   ❌ Node.js 未安装"
fi

echo ""
echo "=============================================="
echo "✅ 环境检查完成！"
echo "=============================================="
echo ""
echo "📖 使用方法:"
echo ""
echo "   Python 版本:"
echo "   python3 converter.py your-song.mp3 --metronome"
echo ""
echo "   Node.js 版本:"
echo "   node converter-node.js your-song.mp3 --metronome"
echo ""
echo "   GUI 版本 (Python):"
echo "   python3 gui_converter.py"
echo ""
echo "📖 查看帮助:"
echo "   python3 converter.py --help"
echo "   node converter-node.js --help"
echo ""
