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

PORT = int(os.getenv("PORT", "7861"))
OUTPUT_DIR = Path("/app/outputs")
UPLOAD_DIR = Path("/app/uploads")
OUTPUT_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

# FastAPI app
app = FastAPI(title="VoxCPM API", version="1.5.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_model():
    model_path = os.getenv("HF_REPO_ID", "openbmb/VoxCPM1.5")
    return voxcpm.VoxCPM.from_pretrained(model_path)

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": gpu_manager.is_loaded()}

@app.post("/api/tts")
async def tts(
    text: str = Form(...),
    prompt_audio: UploadFile = File(None),
    prompt_text: str = Form(None),
    cfg_value: float = Form(2.0),
    inference_timesteps: int = Form(10),
    min_len: int = Form(2),
    max_len: int = Form(4096),
    normalize: bool = Form(False),
    denoise: bool = Form(False),
    retry_badcase: bool = Form(True),
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

# Gradio UI
def create_ui():
    with gr.Blocks(title="VoxCPM TTS") as demo:
        gr.Markdown("# 🎙️ VoxCPM - Text-to-Speech")
        
        with gr.Tab("🎤 Voice Synthesis"):
            text_input = gr.Textbox(label="Text", lines=3, placeholder="Enter text to synthesize...")
            
            with gr.Accordion("⚙️ Advanced Settings", open=False):
                cfg_value = gr.Slider(0.5, 5.0, value=2.0, step=0.1, label="CFG Value (Guidance scale)")
                inference_steps = gr.Slider(5, 20, value=10, step=1, label="Inference Steps (Higher = better quality, slower)")
                min_len = gr.Slider(1, 100, value=2, step=1, label="Min Length (Minimum token length)")
                max_len = gr.Slider(100, 8192, value=4096, step=100, label="Max Length (Maximum token length)")
                normalize = gr.Checkbox(label="Normalize Text", value=False)
                denoise = gr.Checkbox(label="Denoise", value=False)
                retry_badcase = gr.Checkbox(label="Retry Bad Cases (Auto-retry unstoppable cases)", value=True)
                retry_max_times = gr.Slider(1, 10, value=3, step=1, label="Max Retry Times")
                retry_threshold = gr.Slider(1.0, 20.0, value=6.0, step=0.5, label="Retry Threshold (Audio-to-text ratio)")
            
            synthesize_btn = gr.Button("🎵 Synthesize", variant="primary")
            audio_output = gr.Audio(label="Generated Audio")
        
        with gr.Tab("🎭 Voice Cloning"):
            clone_text = gr.Textbox(label="Text", lines=3, placeholder="Enter text to synthesize with cloned voice...")
            prompt_audio = gr.Audio(label="Reference Audio", type="filepath")
            prompt_text = gr.Textbox(label="Reference Transcript (optional)", lines=2, placeholder="Transcript of reference audio")
            
            with gr.Accordion("⚙️ Advanced Settings", open=False):
                clone_cfg = gr.Slider(0.5, 5.0, value=2.0, step=0.1, label="CFG Value")
                clone_steps = gr.Slider(5, 20, value=10, step=1, label="Inference Steps")
                clone_min_len = gr.Slider(1, 100, value=2, step=1, label="Min Length")
                clone_max_len = gr.Slider(100, 8192, value=4096, step=100, label="Max Length")
                clone_normalize = gr.Checkbox(label="Normalize Text", value=False)
                clone_denoise = gr.Checkbox(label="Denoise Reference", value=False)
                clone_retry = gr.Checkbox(label="Retry Bad Cases", value=True)
                clone_retry_max = gr.Slider(1, 10, value=3, step=1, label="Max Retry Times")
                clone_retry_threshold = gr.Slider(1.0, 20.0, value=6.0, step=0.5, label="Retry Threshold")
            
            clone_btn = gr.Button("🎭 Clone Voice", variant="primary")
            clone_output = gr.Audio(label="Cloned Audio")
        
        with gr.Tab("🖥️ GPU Status"):
            gpu_info = gr.Textbox(label="GPU Status", interactive=False)
            refresh_btn = gr.Button("🔄 Refresh")
            offload_btn = gr.Button("🗑️ Offload Model")
        
        def synthesize(text, cfg, steps, min_l, max_l, norm, den, retry, retry_max, retry_th):
            model = gpu_manager.get_model(load_model)
            wav = model.generate(
                text=text, 
                cfg_value=cfg, 
                inference_timesteps=steps,
                min_len=min_l,
                max_len=max_l,
                normalize=norm, 
                denoise=den,
                retry_badcase=retry,
                retry_badcase_max_times=retry_max,
                retry_badcase_ratio_threshold=retry_th
            )
            path = OUTPUT_DIR / f"synth_{int(time.time())}.wav"
            sf.write(path, wav, model.tts_model.sample_rate)
            return str(path)
        
        def clone_voice(text, audio, transcript, cfg, steps, min_l, max_l, norm, den, retry, retry_max, retry_th):
            model = gpu_manager.get_model(load_model)
            wav = model.generate(
                text=text, 
                prompt_wav_path=audio, 
                prompt_text=transcript,
                cfg_value=cfg, 
                inference_timesteps=steps,
                min_len=min_l,
                max_len=max_l,
                normalize=norm,
                denoise=den,
                retry_badcase=retry,
                retry_badcase_max_times=retry_max,
                retry_badcase_ratio_threshold=retry_th
            )
            path = OUTPUT_DIR / f"clone_{int(time.time())}.wav"
            sf.write(path, wav, model.tts_model.sample_rate)
            return str(path)
        
        def get_gpu_status():
            import torch
            if torch.cuda.is_available():
                return f"Model Loaded: {gpu_manager.is_loaded()}\nMemory: {torch.cuda.memory_allocated()/1024**3:.2f}GB"
            return "CUDA not available"
        
        synthesize_btn.click(
            synthesize, 
            [text_input, cfg_value, inference_steps, min_len, max_len, normalize, denoise, retry_badcase, retry_max_times, retry_threshold], 
            audio_output
        )
        clone_btn.click(
            clone_voice, 
            [clone_text, prompt_audio, prompt_text, clone_cfg, clone_steps, clone_min_len, clone_max_len, clone_normalize, clone_denoise, clone_retry, clone_retry_max, clone_retry_threshold], 
            clone_output
        )
        refresh_btn.click(get_gpu_status, None, gpu_info)
        offload_btn.click(lambda: (gpu_manager.force_offload(), "Model offloaded"), None, gpu_info)
    
    return demo

# Mount Gradio to FastAPI
ui = create_ui()
app = gr.mount_gradio_app(app, ui, path="/")

if __name__ == '__main__':
    print(f"🚀 Starting VoxCPM Server on 0.0.0.0:{PORT}")
    print(f"📍 UI:      http://0.0.0.0:{PORT}")
    print(f"📍 API:     http://0.0.0.0:{PORT}/api")
    print(f"📍 Docs:    http://0.0.0.0:{PORT}/docs")
    print(f"📍 Health:  http://0.0.0.0:{PORT}/health")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
