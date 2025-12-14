"""
OpenAI-Compatible TTS API for VoxCPM
Implements /v1/audio/speech endpoint with full OpenAI compatibility
"""
import os
import time
import io
import json
import hashlib
import soundfile as sf
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel, Field
from typing import Literal, Optional
from gpu_manager import gpu_manager
import voxcpm

router = APIRouter(prefix="/v1", tags=["OpenAI Compatible"])

UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
VOICES_DIR = Path("/app/voices")
VOICES_DIR.mkdir(exist_ok=True)
VOICES_DB = VOICES_DIR / "voices.json"

# Voice mapping: OpenAI voices -> VoxCPM preset voices
VOICE_MAPPING = {
    "alloy": "default",
    "echo": "default",
    "fable": "default",
    "onyx": "default",
    "nova": "default",
    "shimmer": "default",
    "ash": "default",
    "ballad": "default",
    "coral": "default",
    "sage": "default",
    "verse": "default",
}

# Preset voices with audio files
PRESET_VOICES = {
    "default": {
        "path": "/app/examples/example.wav",
        "text": "这是一个示例参考音频"
    }
}

def load_custom_voices():
    """Load custom voices from database"""
    if VOICES_DB.exists():
        with open(VOICES_DB, 'r') as f:
            return json.load(f)
    return {}

def save_custom_voices(voices):
    """Save custom voices to database"""
    with open(VOICES_DB, 'w') as f:
        json.dump(voices, f, ensure_ascii=False, indent=2)

def get_voice_config(voice_id: str):
    """Get voice configuration by ID (preset or custom)"""
    # Check preset voices first
    preset_key = VOICE_MAPPING.get(voice_id)
    if preset_key and preset_key in PRESET_VOICES:
        return PRESET_VOICES[preset_key]
    
    # Check custom voices
    custom_voices = load_custom_voices()
    if voice_id in custom_voices:
        return custom_voices[voice_id]
    
    # Default fallback
    return PRESET_VOICES["default"]

class SpeechRequest(BaseModel):
    model: Literal["tts-1", "tts-1-hd", "gpt-4o-mini-tts"] = Field(default="tts-1")
    input: str = Field(..., max_length=4096)
    voice: str = Field(default="alloy")  # 支持预设或自定义 voice_id
    response_format: Optional[Literal["mp3", "opus", "aac", "flac", "wav", "pcm"]] = Field(default="mp3")
    speed: Optional[float] = Field(default=1.0, ge=0.25, le=4.0)

def load_model():
    model_path = os.getenv("HF_REPO_ID", "openbmb/VoxCPM1.5")
    return voxcpm.VoxCPM.from_pretrained(model_path)

def convert_audio_format(wav_data: bytes, sample_rate: int, target_format: str) -> bytes:
    """Convert WAV audio to target format"""
    import subprocess
    import tempfile
    
    if target_format == "wav":
        return wav_data
    
    if target_format == "pcm":
        # Return raw PCM data without WAV header
        audio_array, _ = sf.read(io.BytesIO(wav_data))
        return audio_array.tobytes()
    
    # Use ffmpeg for other formats
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
        wav_file.write(wav_data)
        wav_path = wav_file.name
    
    with tempfile.NamedTemporaryFile(suffix=f".{target_format}", delete=False) as out_file:
        out_path = out_file.name
    
    try:
        cmd = ["ffmpeg", "-i", wav_path, "-y"]
        
        if target_format == "mp3":
            cmd.extend(["-codec:a", "libmp3lame", "-b:a", "128k"])
        elif target_format == "opus":
            cmd.extend(["-codec:a", "libopus", "-b:a", "128k"])
        elif target_format == "aac":
            cmd.extend(["-codec:a", "aac", "-b:a", "128k"])
        elif target_format == "flac":
            cmd.extend(["-codec:a", "flac"])
        
        cmd.append(out_path)
        subprocess.run(cmd, check=True, capture_output=True)
        
        with open(out_path, "rb") as f:
            return f.read()
    finally:
        os.unlink(wav_path)
        if os.path.exists(out_path):
            os.unlink(out_path)

@router.post("/audio/speech")
async def create_speech(request: SpeechRequest):
    """
    OpenAI-compatible TTS endpoint
    Generates audio from input text with streaming support
    Supports both preset voices (alloy, echo, etc.) and custom voice IDs
    """
    try:
        # Get voice configuration (preset or custom)
        preset = get_voice_config(request.voice)
        
        if not preset or not Path(preset["path"]).exists():
            raise HTTPException(status_code=400, detail=f"Voice '{request.voice}' not available")
        
        # Load model
        model = gpu_manager.get_model(load_model)
        
        # Adjust inference steps based on model quality
        if request.model == "tts-1":
            inference_timesteps = 5  # Fast mode
        elif request.model == "tts-1-hd":
            inference_timesteps = 10  # High quality
        else:  # gpt-4o-mini-tts
            inference_timesteps = 7  # Balanced
        
        # Generate audio
        sample_rate = model.tts_model.sample_rate
        
        def audio_stream():
            import numpy as np
            
            # PCM format: true streaming (chunk by chunk)
            if request.response_format == "pcm":
                is_first_chunk = True
                dc_offset = 0.0  # 累积的 DC offset 估计
                alpha = 0.001   # DC offset 更新系数（低通滤波）
                
                for wav_chunk in model.generate_streaming(
                    text=request.input,
                    prompt_wav_path=preset["path"],
                    prompt_text=preset["text"],
                    cfg_value=2.0,
                    inference_timesteps=inference_timesteps,
                    min_len=2,
                    max_len=4096,
                    normalize=False,
                    denoise=False,
                    retry_badcase=False,
                ):
                    # 使用滑动平均更新 DC offset 估计
                    chunk_mean = np.mean(wav_chunk)
                    dc_offset = dc_offset * (1 - alpha) + chunk_mean * alpha
                    
                    # 去除 DC offset
                    wav_chunk = wav_chunk - dc_offset
                    
                    # Apply fade-in to first chunk (longer fade for smoother start)
                    if is_first_chunk:
                        fade_len = min(2048, len(wav_chunk))  # ~46ms @ 44.1kHz
                        fade = np.linspace(0, 1, fade_len)
                        wav_chunk[:fade_len] *= fade
                        is_first_chunk = False
                    
                    # Convert float32 to int16 PCM
                    pcm_data = (wav_chunk * 32767).astype(np.int16)
                    yield pcm_data.tobytes()
            else:
                # WAV/MP3: must collect all chunks for correct header
                all_chunks = []
                for wav_chunk in model.generate_streaming(
                    text=request.input,
                    prompt_wav_path=preset["path"],
                    prompt_text=preset["text"],
                    cfg_value=2.0,
                    inference_timesteps=inference_timesteps,
                    min_len=2,
                    max_len=4096,
                    normalize=False,
                    denoise=False,
                    retry_badcase=False,
                ):
                    all_chunks.append(wav_chunk)
                
                full_audio = np.concatenate(all_chunks)
                
                if request.response_format == "wav":
                    buffer = io.BytesIO()
                    sf.write(buffer, full_audio, sample_rate, format='WAV', subtype='PCM_16')
                    buffer.seek(0)
                    yield buffer.read()
                else:
                    buffer = io.BytesIO()
                    sf.write(buffer, full_audio, sample_rate, format='WAV', subtype='PCM_16')
                    buffer.seek(0)
                    wav_data = buffer.read()
                    try:
                        converted = convert_audio_format(wav_data, sample_rate, request.response_format)
                        yield converted
                    except Exception as e:
                        yield wav_data
        
        # Determine media type
        media_types = {
            "mp3": "audio/mpeg",
            "opus": "audio/opus",
            "aac": "audio/aac",
            "flac": "audio/flac",
            "wav": "audio/wav",
            "pcm": "audio/pcm"
        }
        media_type = media_types.get(request.response_format, "audio/wav")
        
        return StreamingResponse(audio_stream(), media_type=media_type)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def list_models():
    """List available TTS models (OpenAI compatible)"""
    return {
        "object": "list",
        "data": [
            {
                "id": "tts-1",
                "object": "model",
                "created": 1699053241,
                "owned_by": "voxcpm"
            },
            {
                "id": "tts-1-hd",
                "object": "model",
                "created": 1699053241,
                "owned_by": "voxcpm"
            },
            {
                "id": "gpt-4o-mini-tts",
                "object": "model",
                "created": 1699053241,
                "owned_by": "voxcpm"
            }
        ]
    }

@router.get("/voices")
async def list_voices():
    """List available voices (OpenAI compatible)"""
    return {
        "voices": [
            {"id": "alloy", "name": "Alloy"},
            {"id": "echo", "name": "Echo"},
            {"id": "fable", "name": "Fable"},
            {"id": "onyx", "name": "Onyx"},
            {"id": "nova", "name": "Nova"},
            {"id": "shimmer", "name": "Shimmer"},
            {"id": "ash", "name": "Ash"},
            {"id": "ballad", "name": "Ballad"},
            {"id": "coral", "name": "Coral"},
            {"id": "sage", "name": "Sage"},
            {"id": "verse", "name": "Verse"}
        ]
    }

# ============ Custom Voice API ============

@router.post("/voices/create")
async def create_voice(
    audio: UploadFile = File(..., description="参考音频文件 (WAV/MP3)"),
    name: str = Form(..., description="音色名称"),
    text: str = Form(..., description="音频对应的文本内容")
):
    """
    上传音频创建自定义音色
    返回 voice_id，可在 /v1/audio/speech 的 voice 参数中使用
    """
    try:
        # 读取音频文件
        content = await audio.read()
        
        # 生成唯一 ID (基于内容哈希)
        voice_id = hashlib.md5(content).hexdigest()[:12]
        
        # 保存音频文件
        audio_path = VOICES_DIR / f"{voice_id}.wav"
        
        # 如果不是 WAV 格式，转换为 WAV
        if audio.filename.lower().endswith('.mp3'):
            import subprocess
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            subprocess.run([
                'ffmpeg', '-y', '-i', tmp_path,
                '-ar', '44100', '-ac', '1',
                str(audio_path)
            ], check=True, capture_output=True)
            os.unlink(tmp_path)
        else:
            # 直接保存或转换 WAV
            audio_data, sr = sf.read(io.BytesIO(content))
            sf.write(str(audio_path), audio_data, sr, format='WAV', subtype='PCM_16')
        
        # 保存到数据库
        custom_voices = load_custom_voices()
        custom_voices[voice_id] = {
            "path": str(audio_path),
            "text": text,
            "name": name,
            "created_at": int(time.time())
        }
        save_custom_voices(custom_voices)
        
        return {
            "success": True,
            "voice_id": voice_id,
            "name": name,
            "message": f"音色创建成功，使用 voice='{voice_id}' 调用 /v1/audio/speech"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices/custom")
async def list_custom_voices():
    """列出所有自定义音色"""
    custom_voices = load_custom_voices()
    return {
        "voices": [
            {
                "id": vid,
                "name": v.get("name", vid),
                "text": v.get("text", ""),
                "created_at": v.get("created_at", 0)
            }
            for vid, v in custom_voices.items()
        ]
    }

@router.get("/voices/{voice_id}")
async def get_voice(voice_id: str):
    """获取音色详情"""
    # 检查预设音色
    if voice_id in VOICE_MAPPING:
        return {
            "id": voice_id,
            "type": "preset",
            "name": voice_id.capitalize()
        }
    
    # 检查自定义音色
    custom_voices = load_custom_voices()
    if voice_id in custom_voices:
        v = custom_voices[voice_id]
        return {
            "id": voice_id,
            "type": "custom",
            "name": v.get("name", voice_id),
            "text": v.get("text", ""),
            "created_at": v.get("created_at", 0)
        }
    
    raise HTTPException(status_code=404, detail=f"Voice '{voice_id}' not found")

@router.delete("/voices/{voice_id}")
async def delete_voice(voice_id: str):
    """删除自定义音色"""
    if voice_id in VOICE_MAPPING:
        raise HTTPException(status_code=400, detail="Cannot delete preset voice")
    
    custom_voices = load_custom_voices()
    if voice_id not in custom_voices:
        raise HTTPException(status_code=404, detail=f"Voice '{voice_id}' not found")
    
    # 删除音频文件
    audio_path = Path(custom_voices[voice_id]["path"])
    if audio_path.exists():
        audio_path.unlink()
    
    # 从数据库删除
    del custom_voices[voice_id]
    save_custom_voices(custom_voices)
    
    return {"success": True, "message": f"Voice '{voice_id}' deleted"}
