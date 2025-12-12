#!/usr/bin/env python3
import os
import sys
import soundfile as sf
import torch
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP
from gpu_manager import gpu_manager
import voxcpm

mcp = FastMCP("VoxCPM")

OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_model():
    model_path = os.getenv("HF_REPO_ID", "openbmb/VoxCPM1.5")
    return voxcpm.VoxCPM.from_pretrained(model_path)

@mcp.tool()
def text_to_speech(
    text: str,
    output_path: Optional[str] = None,
    cfg_value: float = 2.0,
    inference_timesteps: int = 10,
    min_len: int = 2,
    max_len: int = 4096,
    normalize: bool = False,
    denoise: bool = False,
    retry_badcase: bool = True,
    retry_badcase_max_times: int = 3,
    retry_badcase_ratio_threshold: float = 6.0
) -> dict:
    """
    Convert text to speech using VoxCPM.
    
    Args:
        text: Text to synthesize
        output_path: Output file path (optional, auto-generated if not provided)
        cfg_value: Guidance scale (0.5-5.0, default: 2.0)
        inference_timesteps: Number of inference steps (5-20, default: 10)
        min_len: Minimum token length (default: 2)
        max_len: Maximum token length (default: 4096)
        normalize: Enable text normalization
        denoise: Enable audio denoising
        retry_badcase: Enable retry for bad cases (default: True)
        retry_badcase_max_times: Maximum retry times (default: 3)
        retry_badcase_ratio_threshold: Audio-to-text ratio threshold (default: 6.0)
    
    Returns:
        Dictionary with status and output file path
    """
    try:
        model = gpu_manager.get_model(load_model)
        
        wav = model.generate(
            text=text,
            cfg_value=cfg_value,
            inference_timesteps=inference_timesteps,
            min_len=min_len,
            max_len=max_len,
            normalize=normalize,
            denoise=denoise,
            retry_badcase=retry_badcase,
            retry_badcase_max_times=retry_badcase_max_times,
            retry_badcase_ratio_threshold=retry_badcase_ratio_threshold
        )
        
        if output_path is None:
            output_path = str(OUTPUT_DIR / f"tts_{int(time.time())}.wav")
        
        sf.write(output_path, wav, model.tts_model.sample_rate)
        
        return {
            "status": "success",
            "output_path": output_path,
            "sample_rate": model.tts_model.sample_rate
        }
    
    except Exception as e:
        gpu_manager.force_offload()
        return {"status": "error", "error": str(e)}

@mcp.tool()
def voice_cloning(
    text: str,
    reference_audio: str,
    reference_text: Optional[str] = None,
    output_path: Optional[str] = None,
    cfg_value: float = 2.0,
    inference_timesteps: int = 10,
    min_len: int = 2,
    max_len: int = 4096,
    normalize: bool = False,
    denoise: bool = False,
    retry_badcase: bool = True,
    retry_badcase_max_times: int = 3,
    retry_badcase_ratio_threshold: float = 6.0
) -> dict:
    """
    Clone a voice from reference audio and synthesize new text.
    
    Args:
        text: Text to synthesize with cloned voice
        reference_audio: Path to reference audio file
        reference_text: Transcript of reference audio (optional)
        output_path: Output file path (optional)
        cfg_value: Guidance scale (0.5-5.0, default: 2.0)
        inference_timesteps: Number of inference steps (5-20, default: 10)
        min_len: Minimum token length (default: 2)
        max_len: Maximum token length (default: 4096)
        normalize: Enable text normalization
        denoise: Enable audio denoising for reference
        retry_badcase: Enable retry for bad cases (default: True)
        retry_badcase_max_times: Maximum retry times (default: 3)
        retry_badcase_ratio_threshold: Audio-to-text ratio threshold (default: 6.0)
    
    Returns:
        Dictionary with status and output file path
    """
    try:
        if not os.path.exists(reference_audio):
            return {"status": "error", "error": f"Reference audio not found: {reference_audio}"}
        
        model = gpu_manager.get_model(load_model)
        
        wav = model.generate(
            text=text,
            prompt_wav_path=reference_audio,
            prompt_text=reference_text,
            cfg_value=cfg_value,
            inference_timesteps=inference_timesteps,
            min_len=min_len,
            max_len=max_len,
            normalize=normalize,
            denoise=denoise,
            retry_badcase=retry_badcase,
            retry_badcase_max_times=retry_badcase_max_times,
            retry_badcase_ratio_threshold=retry_badcase_ratio_threshold
        )
        
        if output_path is None:
            output_path = str(OUTPUT_DIR / f"clone_{int(time.time())}.wav")
        
        sf.write(output_path, wav, model.tts_model.sample_rate)
        
        return {
            "status": "success",
            "output_path": output_path,
            "sample_rate": model.tts_model.sample_rate
        }
    
    except Exception as e:
        gpu_manager.force_offload()
        return {"status": "error", "error": str(e)}

@mcp.tool()
def get_gpu_status() -> dict:
    """
    Get current GPU memory usage and model status.
    
    Returns:
        Dictionary with GPU status information
    """
    try:
        if not torch.cuda.is_available():
            return {"status": "error", "error": "CUDA not available"}
        
        return {
            "status": "success",
            "model_loaded": gpu_manager.model is not None,
            "memory_allocated_gb": round(torch.cuda.memory_allocated() / 1024**3, 2),
            "memory_reserved_gb": round(torch.cuda.memory_reserved() / 1024**3, 2),
            "device_name": torch.cuda.get_device_name(0)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
def offload_model() -> dict:
    """
    Force offload model from GPU to free memory.
    
    Returns:
        Dictionary with operation status
    """
    try:
        gpu_manager.force_offload()
        return {"status": "success", "message": "Model offloaded from GPU"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import time
    mcp.run()
