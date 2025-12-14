"""
OpenAI-Compatible TTS API for VoxCPM
Implements /v1/audio/speech endpoint with full OpenAI compatibility
"""
import os
import time
import io
import soundfile as sf
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel, Field
from typing import Literal, Optional
from gpu_manager import gpu_manager
import voxcpm

router = APIRouter(prefix="/v1", tags=["OpenAI Compatible"])

UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

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

class SpeechRequest(BaseModel):
    model: Literal["tts-1", "tts-1-hd", "gpt-4o-mini-tts"] = Field(default="tts-1")
    input: str = Field(..., max_length=4096)
    voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer", "ash", "ballad", "coral", "sage", "verse"] = Field(default="alloy")
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
    """
    try:
        # Map OpenAI voice to VoxCPM preset
        voxcpm_voice = VOICE_MAPPING.get(request.voice, "default")
        preset = PRESET_VOICES.get(voxcpm_voice)
        
        if not preset:
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
