import hashlib
import json
from pathlib import Path
from typing import Optional, Dict, Any

class CacheManager:
    def __init__(self, cache_dir: str = "/app/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.whisper_cache_dir = self.cache_dir / "whisper"
        self.audio_cache_dir = self.cache_dir / "audio"
        self.whisper_cache_dir.mkdir(exist_ok=True)
        self.audio_cache_dir.mkdir(exist_ok=True)
        
    def get_file_md5(self, file_path) -> str:
        """Calculate MD5 hash of file"""
        # Handle Gradio file object or string path
        if hasattr(file_path, 'name'):
            file_path = file_path.name
        elif not isinstance(file_path, (str, Path)):
            file_path = str(file_path)
        
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        return md5_hash.hexdigest()
    
    def get_whisper_cache(self, audio_path) -> Optional[str]:
        """Get cached Whisper transcription"""
        try:
            md5 = self.get_file_md5(audio_path)
            cache_file = self.whisper_cache_dir / f"{md5}.txt"
            if cache_file.exists():
                return cache_file.read_text(encoding='utf-8')
        except (FileNotFoundError, Exception):
            pass
        return None
    
    def set_whisper_cache(self, audio_path, text: str):
        """Cache Whisper transcription"""
        try:
            md5 = self.get_file_md5(audio_path)
            cache_file = self.whisper_cache_dir / f"{md5}.txt"
            cache_file.write_text(text, encoding='utf-8')
        except Exception:
            pass
    
    def get_audio_cache(self, audio_path) -> Optional[Dict[str, Any]]:
        """Get cached audio metadata"""
        try:
            md5 = self.get_file_md5(audio_path)
            cache_file = self.audio_cache_dir / f"{md5}.json"
            if cache_file.exists():
                return json.loads(cache_file.read_text())
        except Exception:
            pass
        return None
    
    def set_audio_cache(self, audio_path, metadata: Dict[str, Any]):
        """Cache audio metadata"""
        try:
            md5 = self.get_file_md5(audio_path)
            cache_file = self.audio_cache_dir / f"{md5}.json"
            cache_file.write_text(json.dumps(metadata, ensure_ascii=False))
        except Exception:
            pass

cache_manager = CacheManager()
