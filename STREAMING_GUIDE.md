# 🌊 流式音频输出优化指南

> 本文档记录了 VoxCPM 项目在实现流式音频输出过程中遇到的问题、解决方案和优化经验，可作为其他项目实现流式输出的参考。

## 📋 目录

1. [流式输出架构](#流式输出架构)
2. [音频格式选择](#音频格式选择)
3. [后端流式实现](#后端流式实现)
4. [前端流式播放](#前端流式播放)
5. [音频质量问题与解决](#音频质量问题与解决)
6. [性能优化](#性能优化)
7. [经验总结](#经验总结)

---

## 流式输出架构

### 整体流程

```
[TTS 模型] → [后端 chunk 生成] → [HTTP 流式响应] → [前端接收] → [Web Audio API 播放]
```

### 关键决策点

| 决策 | 选择 | 原因 |
|------|------|------|
| 传输格式 | PCM (s16le) | 无需头信息，支持真正的流式 |
| 采样率 | 44100 Hz | 高质量，兼容性好 |
| 位深度 | 16-bit | 平衡质量和带宽 |
| 声道 | 单声道 | TTS 不需要立体声 |

---

## 音频格式选择

### WAV vs PCM 的关键区别

#### WAV 格式的问题

WAV 文件头包含 `data` chunk 的大小字段，**必须在写入前知道总大小**：

```
WAV 文件结构:
├── RIFF header (4 bytes): "RIFF"
├── File size (4 bytes): 总大小 - 8
├── WAVE header (4 bytes): "WAVE"
├── fmt chunk (24 bytes): 格式信息
└── data chunk
    ├── "data" (4 bytes)
    ├── Data size (4 bytes): ⚠️ 必须预先知道！
    └── Audio data...
```

**问题**：流式生成时无法预知总大小，导致：
1. 每个 chunk 单独写 WAV 头 → 头信息声明的大小与实际不符
2. 播放器只播放头信息声明的长度，后面的数据被截断

#### PCM 格式的优势

PCM 是纯音频数据，**无任何头信息**：
- 可以直接拼接多个 chunk
- 支持真正的边生成边传输
- 首字节延迟极低（~0.001s）

### 格式选择建议

| 场景 | 推荐格式 | 原因 |
|------|----------|------|
| 流式播放 | PCM | 无头信息，真正流式 |
| 文件保存 | WAV | 兼容性好，可直接播放 |
| 网络传输 | MP3/Opus | 压缩率高，节省带宽 |

---

## 后端流式实现

### Python FastAPI 实现

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import numpy as np

@router.post("/v1/audio/speech")
async def create_speech(request: SpeechRequest):
    def audio_stream():
        # PCM 格式：真正的流式输出
        if request.response_format == "pcm":
            is_first_chunk = True
            dc_offset = 0.0
            alpha = 0.001  # DC offset 滑动平均系数
            
            for wav_chunk in model.generate_streaming(...):
                # 1. 去除 DC offset（滑动平均）
                chunk_mean = np.mean(wav_chunk)
                dc_offset = dc_offset * (1 - alpha) + chunk_mean * alpha
                wav_chunk = wav_chunk - dc_offset
                
                # 2. 第一个 chunk 应用淡入效果
                if is_first_chunk:
                    fade_len = min(2048, len(wav_chunk))
                    fade = np.linspace(0, 1, fade_len)
                    wav_chunk[:fade_len] *= fade
                    is_first_chunk = False
                
                # 3. 转换为 int16 PCM
                pcm_data = (wav_chunk * 32767).astype(np.int16)
                yield pcm_data.tobytes()
        
        # WAV 格式：必须收集所有数据后再输出
        else:
            all_chunks = []
            for wav_chunk in model.generate_streaming(...):
                all_chunks.append(wav_chunk)
            
            full_audio = np.concatenate(all_chunks)
            
            # 写入完整的 WAV 文件
            buffer = io.BytesIO()
            sf.write(buffer, full_audio, sample_rate, format='WAV', subtype='PCM_16')
            buffer.seek(0)
            yield buffer.read()
    
    return StreamingResponse(audio_stream(), media_type="audio/pcm")
```

### 关键点

1. **PCM 格式才能真正流式**：WAV 需要完整数据才能写正确的头
2. **DC offset 处理**：使用滑动平均而非每个 chunk 单独处理
3. **淡入效果**：只对第一个 chunk 应用，避免开头爆音

---

## 前端流式播放

### Web Audio API 实现

```javascript
const SAMPLE_RATE = 44100;
const MIN_BUFFER_SIZE = 22050;  // 500ms 缓冲
const FADE_SAMPLES = 2048;      // 淡入采样数

let audioContext = null;
let activeSources = [];
let nextPlayTime = 0;

// 停止所有播放
function stopAllAudio() {
    activeSources.forEach(s => { try { s.stop(); } catch(e) {} });
    activeSources = [];
}

// 淡入效果
function applyFadeIn(arr) {
    const len = Math.min(FADE_SAMPLES, arr.length);
    for (let i = 0; i < len; i++) arr[i] *= i / len;
}

async function playStreaming(url, text) {
    // 初始化 AudioContext
    if (!audioContext) {
        audioContext = new AudioContext({ sampleRate: SAMPLE_RATE });
    }
    if (audioContext.state === 'suspended') {
        await audioContext.resume();
    }
    
    // 停止之前的播放
    stopAllAudio();
    
    // 初始化播放时间（留出缓冲）
    nextPlayTime = audioContext.currentTime + 0.15;
    
    let pendingBytes = new Uint8Array(0);
    let samples = [];
    let isFirstChunk = true;
    
    // 播放累积的采样
    function playBuffer() {
        if (samples.length === 0) return;
        
        const float32Array = new Float32Array(samples);
        
        // 第一个块应用淡入
        if (isFirstChunk) {
            applyFadeIn(float32Array);
            isFirstChunk = false;
        }
        
        // 创建音频缓冲区
        const audioBuffer = audioContext.createBuffer(1, float32Array.length, SAMPLE_RATE);
        audioBuffer.getChannelData(0).set(float32Array);
        
        // 创建音频源
        const source = audioContext.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioContext.destination);
        
        // 跟踪音频源
        activeSources.push(source);
        source.onended = () => {
            const idx = activeSources.indexOf(source);
            if (idx > -1) activeSources.splice(idx, 1);
        };
        
        // 防止播放时间落后导致重叠
        if (nextPlayTime < audioContext.currentTime - 0.1) {
            console.warn('Buffer underrun, resetting playback time');
            nextPlayTime = audioContext.currentTime + 0.05;
        }
        
        // 调度播放
        source.start(nextPlayTime);
        nextPlayTime += audioBuffer.duration;
        
        samples = [];
    }
    
    // 获取流式响应
    const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            model: 'tts-1',
            input: text,
            voice: 'alloy',
            response_format: 'pcm'
        })
    });
    
    const reader = response.body.getReader();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) {
            playBuffer();  // 播放剩余数据
            break;
        }
        
        // 合并待处理字节
        const combined = new Uint8Array(pendingBytes.length + value.length);
        combined.set(pendingBytes);
        combined.set(value, pendingBytes.length);
        
        // ⚠️ 关键：确保字节数是偶数（Int16 = 2 bytes）
        const validLength = Math.floor(combined.length / 2) * 2;
        const validData = combined.slice(0, validLength);
        pendingBytes = combined.slice(validLength);
        
        // 转换 PCM 数据
        const int16Array = new Int16Array(validData.buffer, validData.byteOffset, validData.length / 2);
        for (let i = 0; i < int16Array.length; i++) {
            samples.push(int16Array[i] / 32768);
        }
        
        // 累积足够数据后播放
        if (samples.length >= MIN_BUFFER_SIZE) {
            playBuffer();
        }
    }
}
```

### 关键点

1. **字节对齐**：Int16 是 2 字节，网络包可能在奇数位置切分
2. **缓冲策略**：累积 500ms 数据后再播放，减少 buffer 切换
3. **时间同步**：检测 buffer underrun，重置播放时间
4. **停止机制**：新播放前停止之前的音频，防止重叠

---

## 音频质量问题与解决

### 问题 1：开头爆音（Pop/Click）

**现象**：音频开始时有明显的"啪"声

**原因**：
1. 音频从静音（0）突然跳到有声音的采样值
2. DC offset 导致基准线不在 0

**解决方案**：

```python
# 后端：淡入效果
if is_first_chunk:
    fade_len = min(2048, len(wav_chunk))  # ~46ms @ 44.1kHz
    fade = np.linspace(0, 1, fade_len)
    wav_chunk[:fade_len] *= fade
    is_first_chunk = False
```

```javascript
// 前端：淡入效果
function applyFadeIn(arr) {
    const fadeLen = Math.min(2048, arr.length);
    for (let i = 0; i < fadeLen; i++) {
        arr[i] *= i / fadeLen;
    }
}
```

### 问题 2：DC Offset（直流偏移）

**现象**：音频采样值整体偏离 0，导致播放时有底噪

**原因**：TTS 模型生成的音频本身带有 DC 偏移

**解决方案**：

```python
# 后端：滑动平均去除 DC offset
dc_offset = 0.0
alpha = 0.001  # 更新系数

for wav_chunk in model.generate_streaming(...):
    chunk_mean = np.mean(wav_chunk)
    dc_offset = dc_offset * (1 - alpha) + chunk_mean * alpha
    wav_chunk = wav_chunk - dc_offset
```

**注意**：不要对每个 chunk 单独去除 DC offset（减去各自的 mean），这会导致 chunk 之间基准线不一致，产生新的杂音。

### 问题 3：字节对齐问题

**现象**：播放中间出现杂音或噪声

**原因**：Int16 采样是 2 字节，网络传输可能在奇数位置切分数据包

**解决方案**：

```javascript
// 确保字节数是偶数
const validLength = Math.floor(combined.length / 2) * 2;
const validData = combined.slice(0, validLength);
pendingBytes = combined.slice(validLength);  // 保留多余的字节
```

### 问题 4：音频重叠（两个声音）

**现象**：听到两个声音同时播放

**原因**：
1. 多次点击播放，之前的音频还在播放
2. Buffer 调度时间计算错误，多个 buffer 同时开始

**解决方案**：

```javascript
// 1. 播放前停止之前的音频
function stopAllAudio() {
    activeSources.forEach(s => { try { s.stop(); } catch(e) {} });
    activeSources = [];
}

// 2. 检测 buffer underrun，重置时间而非重叠
if (nextPlayTime < audioContext.currentTime - 0.1) {
    nextPlayTime = audioContext.currentTime + 0.05;
}
```

### 问题 5：WAV 头大小不匹配

**现象**：WAV 文件只播放一小部分，或播放器显示错误时长

**原因**：流式输出时每个 chunk 单独写 WAV 头，头中声明的大小只是该 chunk 的大小

**解决方案**：WAV 格式必须收集所有数据后一次性写入

```python
# WAV 格式：收集所有 chunk 后再写
all_chunks = []
for wav_chunk in model.generate_streaming(...):
    all_chunks.append(wav_chunk)

full_audio = np.concatenate(all_chunks)
sf.write(buffer, full_audio, sample_rate, format='WAV', subtype='PCM_16')
```

---

## 性能优化

### 延迟优化

| 优化项 | 优化前 | 优化后 | 提升 |
|--------|--------|--------|------|
| 首字节延迟 | 0.250s | 0.001s | 250x |
| 总生成时间 | 13.90s | 7.87s | 43% |

### 优化措施

1. **使用 PCM 格式**：无需等待完整数据
2. **减少初始缓冲**：从 500ms 减到 150ms
3. **并行处理**：模型生成和网络传输并行

### 缓冲策略

```
缓冲太小 → 播放卡顿、杂音
缓冲太大 → 延迟增加

推荐值：
- 初始缓冲：150ms（首次播放前等待）
- 累积缓冲：500ms（每次播放的数据量）
```

---

## 经验总结

### ✅ 最佳实践

1. **流式传输用 PCM**：WAV/MP3 等格式需要完整数据
2. **后端处理 DC offset**：使用滑动平均，保持 chunk 间连续性
3. **前端处理字节对齐**：Int16 必须 2 字节对齐
4. **淡入效果双保险**：后端和前端都加淡入
5. **累积足够数据再播放**：减少 buffer 切换带来的杂音
6. **跟踪播放状态**：防止音频重叠

### ❌ 常见错误

1. **每个 chunk 单独写 WAV 头**：导致大小不匹配
2. **每个 chunk 单独去 DC offset**：导致 chunk 间跳变
3. **不处理字节对齐**：导致中间杂音
4. **缓冲太小**：导致播放卡顿
5. **不停止之前的播放**：导致声音重叠

### 🔧 调试技巧

```bash
# 分析 PCM 文件
python3 -c "
import numpy as np
with open('audio.pcm', 'rb') as f:
    data = f.read()
samples = np.frombuffer(data, dtype=np.int16)
print(f'采样数: {len(samples)}')
print(f'时长: {len(samples)/44100:.2f}s')
print(f'DC offset: {samples.mean():.1f}')
print(f'开头10采样: {samples[:10].tolist()}')
"

# PCM 转 WAV
ffmpeg -f s16le -ar 44100 -ac 1 -i audio.pcm audio.wav

# 直接播放 PCM
ffplay -f s16le -ar 44100 -ac 1 -autoexit -nodisp audio.pcm
```

### 📊 性能指标参考

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 首字节延迟 | < 100ms | PCM 格式可达 ~1ms |
| 播放延迟 | < 200ms | 从首字节到开始播放 |
| 音频质量 | 无杂音 | 开头无爆音，中间无噪声 |
| CPU 占用 | < 10% | 前端解码和播放 |

---

## 参考资料

- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [WAV 文件格式](http://soundfile.sapp.org/doc/WaveFormat/)
- [PCM 音频格式](https://en.wikipedia.org/wiki/Pulse-code_modulation)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)

---

*本文档基于 VoxCPM 项目的实际开发经验整理，持续更新中。*
