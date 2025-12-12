import os
import time
import threading
import torch
import gc
from typing import Optional, Callable, Any

class GPUManager:
    def __init__(self, idle_timeout: int = 60):
        self.model: Optional[Any] = None
        self.last_used = time.time()
        self.idle_timeout = idle_timeout
        self.lock = threading.Lock()
        self._monitor_thread = None
        self._stop_monitor = False
        
    def get_model(self, load_func: Callable[[], Any]) -> Any:
        with self.lock:
            if self.model is None:
                print("🔄 Loading model to GPU...")
                self.model = load_func()
            self.last_used = time.time()
            return self.model
    
    def force_offload(self):
        with self.lock:
            if self.model is not None:
                print("🗑️  Offloading model from GPU...")
                del self.model
                self.model = None
                gc.collect()
                torch.cuda.empty_cache()
                print("✅ GPU memory released")
    
    def start_monitor(self):
        if self._monitor_thread is None:
            self._stop_monitor = False
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
    
    def stop_monitor(self):
        self._stop_monitor = True
        if self._monitor_thread:
            self._monitor_thread.join()
    
    def _monitor_loop(self):
        while not self._stop_monitor:
            time.sleep(10)
            with self.lock:
                if self.model is not None:
                    idle_time = time.time() - self.last_used
                    if idle_time > self.idle_timeout:
                        print(f"⏰ Model idle for {idle_time:.0f}s, offloading...")
                        self.force_offload()

gpu_manager = GPUManager(idle_timeout=int(os.getenv("GPU_IDLE_TIMEOUT", "60")))
gpu_manager.start_monitor()
