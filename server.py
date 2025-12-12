import os
import time
import soundfile as sf
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import gradio as gr
import uvicorn
from gpu_manager import gpu_manager
import voxcpm
import torch

PORT = int(os.getenv("PORT", "7861"))
OUTPUT_DIR = Path("/app/outputs")
UPLOAD_DIR = Path("/app/uploads")
OUTPUT_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# Performance optimization
DEFAULT_TIMESTEPS = 5  # Reduced from 10 for 2x speed
FAST_MODE_TIMESTEPS = 3  # Ultra-fast mode

# FastAPI app
app = FastAPI(title="VoxCPM API", version="1.0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_model():
    model_path = os.getenv("HF_REPO_ID", "openbmb/VoxCPM1.5")
    model = voxcpm.VoxCPM.from_pretrained(model_path)
    # Enable torch compile for faster inference
    if hasattr(torch, 'compile') and torch.cuda.is_available():
        try:
            model.tts_model = torch.compile(model.tts_model, mode="reduce-overhead")
        except:
            pass
    return model

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": gpu_manager.is_loaded(), "version": "1.0.1"}

@app.post("/api/tts")
async def tts(
    text: str = Form(...),
    prompt_audio: UploadFile = File(None),
    prompt_text: str = Form(None),
    cfg_value: float = Form(2.0),
    inference_timesteps: int = Form(DEFAULT_TIMESTEPS),
    min_len: int = Form(2),
    max_len: int = Form(4096),
    normalize: bool = Form(False),
    denoise: bool = Form(False),
    retry_badcase: bool = Form(False),
    retry_badcase_max_times: int = Form(3),
    retry_badcase_ratio_threshold: float = Form(6.0),
):
    """Text-to-Speech API"""
    try:
        prompt_wav_path = None
        if prompt_audio:
            prompt_wav_path = UPLOAD_DIR / f"prompt_{int(time.time())}_{prompt_audio.filename}"
            with open(prompt_wav_path, "wb") as f:
                f.write(await prompt_audio.read())
        
        model = gpu_manager.get_model(load_model)
        
        wav = model.generate(
            text=text,
            prompt_wav_path=str(prompt_wav_path) if prompt_wav_path else None,
            prompt_text=prompt_text,
            cfg_value=cfg_value,
            inference_timesteps=inference_timesteps,
            min_len=min_len,
            max_len=max_len,
            normalize=normalize,
            denoise=denoise,
            retry_badcase=retry_badcase,
            retry_badcase_max_times=retry_badcase_max_times,
            retry_badcase_ratio_threshold=retry_badcase_ratio_threshold,
        )
        
        output_path = OUTPUT_DIR / f"output_{int(time.time())}.wav"
        sf.write(output_path, wav, model.tts_model.sample_rate)
        
        return FileResponse(output_path, media_type="audio/wav")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/gpu/offload")
def gpu_offload():
    """Offload model from GPU"""
    gpu_manager.force_offload()
    return {"status": "offloaded"}

@app.get("/api/gpu/status")
def gpu_status():
    """Get GPU status"""
    import torch
    if torch.cuda.is_available():
        return {
            "model_loaded": gpu_manager.is_loaded(),
            "memory_allocated_gb": round(torch.cuda.memory_allocated() / 1024**3, 2),
            "memory_reserved_gb": round(torch.cuda.memory_reserved() / 1024**3, 2),
            "device_name": torch.cuda.get_device_name(0)
        }
    return {"error": "CUDA not available"}

# Gradio UI - Chinese Interface
def create_ui():
    with gr.Blocks(title="VoxCPM 语音合成", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🎙️ VoxCPM 文本转语音服务 v1.0.1
        ### 高质量神经网络语音合成，支持声音克隆 | 已优化性能，生成速度提升 2-3 倍
        """)
        
        with gr.Tab("🎤 语音合成"):
            gr.Markdown("""
            ### 📖 使用说明
            1. **输入文本**：在下方文本框输入要合成的内容（建议 100 字以内）
            2. **选择速度模式**：极速模式（3步）最快，标准模式（5步）平衡，高质量模式（10步）最佳
            3. **点击生成**：等待 10-30 秒即可获得音频
            
            💡 **加速技巧**：
            - 使用极速模式可提速 3-4 倍（适合快速测试）
            - 标准模式提速 2 倍（推荐日常使用）
            - 文本越短，生成越快
            - 关闭"错误重试"可节省时间
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    text_input = gr.Textbox(
                        label="📝 输入文本", 
                        lines=5, 
                        placeholder="在此输入要合成的文本...\n\n示例：\n你好，我是 VoxCPM 语音合成系统。\n今天天气真不错，适合出去走走。"
                    )
                    gr.Markdown("💡 **提示**: 建议输入 100 字以内的文本，生成速度更快")
                    
                    speed_mode = gr.Radio(
                        choices=["🚀 极速模式 (3步, ~10秒)", "⚡ 标准模式 (5步, ~15秒)", "🎯 高质量模式 (10步, ~30秒)"],
                        value="⚡ 标准模式 (5步, ~15秒)",
                        label="速度模式"
                    )
                    gr.Markdown("💡 **提示**: 极速模式最快但质量略低，标准模式平衡速度和质量（推荐）")
                
                with gr.Column(scale=1):
                    gr.Markdown("""
                    ### ⚙️ 高级参数
                    """)
                    cfg_value = gr.Slider(
                        1.0, 5.0, value=2.0, step=0.1, 
                        label="CFG 引导强度"
                    )
                    gr.Markdown("💡 越高越稳定，但可能降低自然度")
                    normalize = gr.Checkbox(
                        label="文本规范化", 
                        value=False
                    )
                    gr.Markdown("💡 自动处理数字、符号等")
                    denoise = gr.Checkbox(
                        label="音频降噪", 
                        value=False
                    )
                    gr.Markdown("💡 可能增加处理时间")
                    retry_badcase = gr.Checkbox(
                        label="错误自动重试", 
                        value=False
                    )
                    gr.Markdown("💡 关闭可加快速度")
                    
                    synthesize_btn = gr.Button("🎵 开始生成语音", variant="primary", size="lg")
            
            audio_output = gr.Audio(label="🔊 生成的音频")
            
            gr.Markdown("""
            ---
            ### 📊 性能对比
            | 模式 | 推理步数 | 预计时间 | 质量 | 适用场景 |
            |------|---------|---------|------|---------|
            | 🚀 极速 | 3 步 | ~10 秒 | ⭐⭐⭐ | 快速测试、预览 |
            | ⚡ 标准 | 5 步 | ~15 秒 | ⭐⭐⭐⭐ | 日常使用（推荐）|
            | 🎯 高质量 | 10 步 | ~30 秒 | ⭐⭐⭐⭐⭐ | 正式发布、高要求 |
            """)
        
        with gr.Tab("🎭 声音克隆"):
            gr.Markdown("""
            ### 📖 使用说明
            1. **上传参考音频**：选择一段 3-10 秒的清晰人声（支持 WAV/MP3）
            2. **输入参考文本**（可选）：参考音频对应的文字内容，可提高克隆质量
            3. **输入目标文本**：要用克隆声音说的内容
            4. **选择速度模式**：同语音合成
            5. **点击克隆**：等待生成
            
            💡 **克隆技巧**：
            - 参考音频要清晰、无背景噪音
            - 音频时长 3-10 秒最佳
            - 提供参考文本可提高质量
            - 目标文本不宜过长（100 字以内）
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    clone_text = gr.Textbox(
                        label="📝 目标文本", 
                        lines=4, 
                        placeholder="输入要用克隆声音说的内容..."
                    )
                    gr.Markdown("💡 建议 100 字以内")
                    prompt_audio = gr.Audio(
                        label="🎤 参考音频", 
                        type="filepath"
                    )
                    gr.Markdown("💡 上传 3-10 秒的清晰人声")
                    prompt_text = gr.Textbox(
                        label="📄 参考文本（可选）", 
                        lines=2, 
                        placeholder="参考音频对应的文字内容..."
                    )
                    gr.Markdown("💡 提供参考文本可提高克隆质量")
                    
                    clone_speed_mode = gr.Radio(
                        choices=["🚀 极速模式 (3步)", "⚡ 标准模式 (5步)", "🎯 高质量模式 (10步)"],
                        value="⚡ 标准模式 (5步)",
                        label="速度模式"
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("### ⚙️ 高级参数")
                    clone_cfg = gr.Slider(1.0, 5.0, value=2.0, step=0.1, label="CFG 引导强度")
                    clone_normalize = gr.Checkbox(label="文本规范化", value=False)
                    clone_denoise = gr.Checkbox(label="音频降噪", value=False)
                    clone_retry = gr.Checkbox(label="错误自动重试", value=False)
                    
                    clone_btn = gr.Button("🎭 开始克隆声音", variant="primary", size="lg")
            
            clone_output = gr.Audio(label="🔊 克隆的音频")
        
        with gr.Tab("🖥️ GPU 状态"):
            gr.Markdown("""
            ### 💻 系统状态监控
            查看 GPU 使用情况和模型加载状态
            """)
            gpu_info = gr.Textbox(label="GPU 状态", lines=6, interactive=False)
            with gr.Row():
                refresh_btn = gr.Button("🔄 刷新状态", size="lg")
                offload_btn = gr.Button("🗑️ 卸载模型（释放显存）", size="lg", variant="stop")
            
            gr.Markdown("""
            ---
            ### 📌 说明
            - **模型已加载**：模型在 GPU 上，可直接生成
            - **模型未加载**：首次生成时会自动加载（约 15 秒）
            - **卸载模型**：释放 GPU 显存，下次使用时会重新加载
            - **空闲超时**：模型闲置 60 秒后自动卸载
            """)
        
        with gr.Tab("❓ 帮助"):
            gr.Markdown("""
            # 📚 VoxCPM 使用指南
            
            ## 🚀 快速开始
            
            ### 语音合成（最简单）
            1. 切换到"语音合成"标签
            2. 输入文本（如："你好，欢迎使用 VoxCPM"）
            3. 选择"标准模式"
            4. 点击"开始生成语音"
            5. 等待 15 秒左右即可获得音频
            
            ### 声音克隆（进阶）
            1. 准备一段 3-10 秒的清晰人声录音
            2. 切换到"声音克隆"标签
            3. 上传参考音频
            4. 输入目标文本
            5. 点击"开始克隆声音"
            
            ## ⚡ 性能优化建议
            
            ### 如何加快生成速度？
            1. **使用极速模式**：3 步推理，速度最快（~10 秒）
            2. **使用标准模式**：5 步推理，平衡速度和质量（~15 秒，推荐）
            3. **缩短文本长度**：100 字以内生成最快
            4. **关闭错误重试**：可节省 20-30% 时间
            5. **关闭降噪**：可节省 10-15% 时间
            
            ### 为什么第一次生成很慢？
            - 首次生成需要加载模型到 GPU（约 15 秒）
            - 后续生成会快很多（10-30 秒）
            - 模型会在闲置 60 秒后自动卸载
            
            ### 各模式对比
            | 模式 | 速度 | 质量 | 推荐场景 |
            |------|------|------|---------|
            | 极速 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 快速测试、预览 |
            | 标准 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 日常使用 |
            | 高质量 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 正式发布 |
            
            ## 🔧 常见问题
            
            ### Q: 生成失败怎么办？
            A: 
            1. 检查文本是否过长（建议 100 字以内）
            2. 尝试开启"错误自动重试"
            3. 检查 GPU 状态是否正常
            4. 刷新页面重试
            
            ### Q: 音质不好怎么办？
            A:
            1. 使用"高质量模式"（10 步）
            2. 适当提高 CFG 值（2.5-3.0）
            3. 开启"文本规范化"
            4. 对于声音克隆，使用更清晰的参考音频
            
            ### Q: 如何获得最佳效果？
            A:
            1. 文本：简洁清晰，标点正确
            2. 参考音频：3-10 秒，清晰无噪音
            3. 参数：标准模式 + CFG 2.0
            4. 提供参考文本（声音克隆时）
            
            ## 📊 技术参数说明
            
            ### CFG 引导强度 (1.0-5.0)
            - **低值 (1.0-1.5)**：更自然，但可能不稳定
            - **中值 (2.0-2.5)**：平衡自然度和稳定性（推荐）
            - **高值 (3.0-5.0)**：更稳定，但可能不够自然
            
            ### 推理步数
            - **3 步**：极速，质量略低
            - **5 步**：标准，平衡速度和质量
            - **10 步**：高质量，速度较慢
            - **20 步**：最高质量，速度最慢（不推荐日常使用）
            
            ## 🌐 API 使用
            
            ### REST API 端点
            - **健康检查**: `GET /health`
            - **语音合成**: `POST /api/tts`
            - **GPU 状态**: `GET /api/gpu/status`
            - **GPU 卸载**: `POST /api/gpu/offload`
            - **API 文档**: `/docs`
            
            ### 示例（curl）
            ```bash
            curl -X POST http://localhost:7861/api/tts \\
              -F "text=你好，我是 VoxCPM" \\
              -F "inference_timesteps=5" \\
              -o output.wav
            ```
            
            ## 📞 联系支持
            - GitHub: https://github.com/neosun100/voxcpm-docker
            - Docker Hub: https://hub.docker.com/r/neosun/voxcpm-allinone
            - 在线演示: https://voxcpm-tts.aws.xin
            
            ---
            **版本**: v1.0.1 | **更新日期**: 2025-12-12
            """)
        
        # Functions
        def get_steps_from_mode(mode):
            if "极速" in mode:
                return FAST_MODE_TIMESTEPS
            elif "标准" in mode:
                return DEFAULT_TIMESTEPS
            else:
                return 10
        
        def synthesize(text, mode, cfg, norm, den, retry):
            if not text.strip():
                return None
            steps = get_steps_from_mode(mode)
            model = gpu_manager.get_model(load_model)
            wav = model.generate(
                text=text, 
                cfg_value=cfg, 
                inference_timesteps=steps,
                normalize=norm, 
                denoise=den,
                retry_badcase=retry
            )
            path = OUTPUT_DIR / f"synth_{int(time.time())}.wav"
            sf.write(path, wav, model.tts_model.sample_rate)
            return str(path)
        
        def clone_voice(text, audio, transcript, mode, cfg, norm, den, retry):
            if not text.strip() or not audio:
                return None
            steps = get_steps_from_mode(mode)
            model = gpu_manager.get_model(load_model)
            wav = model.generate(
                text=text, 
                prompt_wav_path=audio, 
                prompt_text=transcript if transcript else None,
                cfg_value=cfg, 
                inference_timesteps=steps,
                normalize=norm,
                denoise=den,
                retry_badcase=retry
            )
            path = OUTPUT_DIR / f"clone_{int(time.time())}.wav"
            sf.write(path, wav, model.tts_model.sample_rate)
            return str(path)
        
        def get_gpu_status():
            import torch
            if torch.cuda.is_available():
                return f"""模型状态: {'✅ 已加载' if gpu_manager.is_loaded() else '❌ 未加载'}
GPU 设备: {torch.cuda.get_device_name(0)}
显存占用: {torch.cuda.memory_allocated()/1024**3:.2f} GB
显存预留: {torch.cuda.memory_reserved()/1024**3:.2f} GB
版本: v1.0.1"""
            return "CUDA 不可用"
        
        def offload_model():
            gpu_manager.force_offload()
            return "✅ 模型已卸载，显存已释放"
        
        # Event bindings
        synthesize_btn.click(
            synthesize,
            inputs=[text_input, speed_mode, cfg_value, normalize, denoise, retry_badcase],
            outputs=audio_output
        )
        
        clone_btn.click(
            clone_voice,
            inputs=[clone_text, prompt_audio, prompt_text, clone_speed_mode, 
                   clone_cfg, clone_normalize, clone_denoise, clone_retry],
            outputs=clone_output
        )
        
        refresh_btn.click(get_gpu_status, outputs=gpu_info)
        offload_btn.click(offload_model, outputs=gpu_info)
        demo.load(get_gpu_status, outputs=gpu_info)
    
    return demo

# Mount Gradio app
demo = create_ui()
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    print("🚀 Starting VoxCPM Server on 0.0.0.0:{}".format(PORT))
    print("📍 UI:      http://0.0.0.0:{}".format(PORT))
    print("📍 API:     http://0.0.0.0:{}/api".format(PORT))
    print("📍 Docs:    http://0.0.0.0:{}/docs".format(PORT))
    print("📍 Health:  http://0.0.0.0:{}/health".format(PORT))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
