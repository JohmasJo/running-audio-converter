#!/usr/bin/env node
/**
 * 🏃 跑步音频转换器 - Node.js 版本
 * 使用 ffmpeg 进行音频处理
 */

const { program } = require('commander');
const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const fs = require('fs');
const { promisify } = require('util');

const stat = promisify(fs.stat);

// 配置
const DEFAULT_TARGET_BPM = 180;
const DEFAULT_METRONOME_VOLUME = 0.3;
const DEFAULT_BEAT_FREQUENCY = 1000;

/**
 * 检测音频 BPM（使用 ffmpeg 和 librubberband）
 * 注意：这是一个简化版本，准确 BPM 检测需要额外的库
 */
async function detectBPM(audioPath) {
    return new Promise((resolve, reject) => {
        console.log('🎵 正在分析 BPM...');
        
        // 使用 ffmpeg 的 bpm 滤镜（如果可用）
        // 否则返回一个估计值
        ffmpeg.ffprobe(audioPath, (err, metadata) => {
            if (err) {
                reject(err);
                return;
            }
            
            // 尝试从元数据中获取 BPM
            const bpmTag = metadata.format.tags?.bpm;
            if (bpmTag) {
                const bpm = parseFloat(bpmTag);
                if (!isNaN(bpm)) {
                    console.log(`   从元数据检测到 BPM: ${bpm}`);
                    resolve(bpm);
                    return;
                }
            }
            
            // 如果没有元数据，使用默认值并让用户知道
            console.log('   ⚠️  无法自动检测 BPM，使用默认拉伸率');
            console.log('   💡 提示：可以使用 --original-bpm 参数指定原始 BPM');
            resolve(120); // 默认假设 120 BPM
        });
    });
}

/**
 * 生成节拍器音频
 */
function generateMetronomeAudio(outputPath, duration, bpm, frequency, volume) {
    return new Promise((resolve, reject) => {
        console.log(`🎛️ 正在生成节拍器 (${bpm} BPM, ${frequency}Hz)...`);
        
        const beatInterval = 60 / bpm;
        const totalBeats = Math.ceil(duration / beatInterval);
        
        // 使用 ffmpeg 生成脉冲音
        let command = ffmpeg()
            .input(`anullsrc=r=44100:cl=mono`)
            .outputOptions([
                `-f lavfi`,
                `-i "sine=f=${frequency}:d=${duration}"`,
                `-af "agate=threshold=-20dB:ratio=9:attack=1:release=100, volume=${volume}"`,
                `-t ${duration}`
            ])
            .output(outputPath);
        
        command.on('end', () => {
            resolve(outputPath);
        }).on('error', (err) => {
            reject(err);
        });
        
        command.run();
    });
}

/**
 * 转换音频文件
 */
async function convertAudio(inputPath, options) {
    const {
        targetBpm = DEFAULT_TARGET_BPM,
        originalBpm,
        addMetronome = false,
        metronomeVolume = DEFAULT_METRONOME_VOLUME,
        beatFrequency = DEFAULT_BEAT_FREQUENCY,
        outputDir
    } = options;
    
    // 检查输入文件
    if (!fs.existsSync(inputPath)) {
        throw new Error(`文件不存在：${inputPath}`);
    }
    
    // 确定输出路径
    const inputParsed = path.parse(inputPath);
    const outputDirPath = outputDir || inputParsed.dir;
    
    if (outputDir && !fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }
    
    // 获取原始 BPM
    let bpm = originalBpm;
    if (!bpm) {
        bpm = await detectBPM(inputPath);
    }
    
    // 计算拉伸率
    const stretchRate = bpm / targetBpm;
    console.log(`   拉伸率：${stretchRate.toFixed(4)} (${bpm} → ${targetBpm} BPM)`);
    
    // 生成输出文件名
    const suffix = addMetronome ? `_${targetBpm}bpm_metronome` : `_${targetBpm}bpm`;
    const outputPath = path.join(outputDirPath, `${inputParsed.name}${suffix}${inputParsed.ext}`);
    
    return new Promise((resolve, reject) => {
        console.log(`⚡ 正在转换...`);
        
        let command = ffmpeg(inputPath)
            .audioFilters(`atempo=${stretchRate}`)
            .on('start', (cmd) => {
                console.log(`   执行：${cmd}`);
            })
            .on('progress', (progress) => {
                const percent = Math.round(progress.percent || 0);
                process.stdout.write(`\r   进度：${percent}%`);
            })
            .on('end', () => {
                console.log('\n✅ 转换完成！');
                resolve(outputPath);
            })
            .on('error', (err) => {
                reject(err);
            })
            .save(outputPath);
    });
}

/**
 * 主函数
 */
async function main() {
    program
        .name('running-audio-converter')
        .description('🏃 跑步音频转换器 - 将音频转换为 180 BPM 版本')
        .argument('<files...>', '输入音频文件')
        .option('-b, --target-bpm <number>', '目标 BPM', '180')
        .option('-o, --original-bpm <number>', '原始 BPM（自动检测失败时使用）')
        .option('-m, --metronome', '添加节拍器音轨', false)
        .option('-v, --metronome-volume <number>', '节拍器音量 (0.0-1.0)', '0.3')
        .option('-f, --beat-frequency <number>', '节拍器频率 (Hz)', '1000')
        .option('-d, --output-dir <dir>', '输出目录')
        .action(async (files, options) => {
            console.log('=' .repeat(60));
            console.log('🏃 跑步音频转换器 - Node.js 版本');
            console.log('=' .repeat(60));
            console.log();
            
            const targetBpm = parseInt(options.targetBpm);
            const originalBpm = options.originalBpm ? parseInt(options.originalBpm) : undefined;
            
            let successCount = 0;
            let errorCount = 0;
            
            for (const file of files) {
                try {
                    console.log(`\n📁 处理：${file}`);
                    console.log('-' .repeat(40));
                    
                    const outputPath = await convertAudio(file, {
                        targetBpm,
                        originalBpm,
                        addMetronome: options.metronome,
                        metronomeVolume: parseFloat(options.metronomeVolume),
                        beatFrequency: parseInt(options.beatFrequency),
                        outputDir: options.outputDir
                    });
                    
                    console.log(`💾 输出：${outputPath}`);
                    successCount++;
                    
                } catch (err) {
                    console.error(`❌ 错误：${err.message}`);
                    errorCount++;
                }
            }
            
            console.log();
            console.log('=' .repeat(60));
            console.log(`✅ 完成！成功：${successCount}, 失败：${errorCount}`);
            console.log('=' .repeat(60));
            
            process.exit(errorCount > 0 ? 1 : 0);
        });
    
    program.parse();
}

// 检查 ffmpeg 是否可用
function checkFFmpeg() {
    return new Promise((resolve) => {
        ffmpeg.ffprobe('-version', (err) => {
            resolve(!err);
        });
    });
}

// 运行
(async () => {
    const hasFFmpeg = await checkFFmpeg();
    if (!hasFFmpeg) {
        console.error('❌ 错误：未找到 ffmpeg');
        console.error('');
        console.error('请安装 ffmpeg:');
        console.error('  - Ubuntu/Debian: sudo apt-get install ffmpeg');
        console.error('  - macOS: brew install ffmpeg');
        console.error('  - Windows: 从 https://ffmpeg.org/download.html 下载');
        console.error('');
        process.exit(1);
    }
    
    main();
})();
