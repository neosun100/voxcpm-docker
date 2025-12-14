#!/usr/bin/env python3
"""快速测试流式API"""
import requests
import time

BASE_URL = "http://localhost:7861"

def quick_test():
    print("🚀 快速测试流式API")
    print("="*50)
    
    # 检查服务
    try:
        requests.get(f"{BASE_URL}/health", timeout=3)
        print("✅ 服务运行中\n")
    except:
        print("❌ 服务未运行")
        return
    
    text = "你好，这是流式测试。"
    
    # 测试流式API
    print("🟢 测试流式API...")
    start = time.time()
    first_byte = None
    
    response = requests.post(
        f"{BASE_URL}/api/tts/stream",
        data={"text": text, "inference_timesteps": 5},
        stream=True
    )
    
    chunks = []
    for i, chunk in enumerate(response.iter_content(8192)):
        if chunk:
            if first_byte is None:
                first_byte = time.time()
                print(f"⚡ 首字节: {first_byte - start:.2f}秒")
            chunks.append(chunk)
            print(f"  📦 块{i+1}: {len(chunk)}字节")
    
    total = time.time() - start
    
    with open("quick_test_stream.wav", "wb") as f:
        for c in chunks:
            f.write(c)
    
    print(f"\n✅ 完成")
    print(f"⚡ 首字节: {first_byte - start:.2f}秒")
    print(f"⏱️  总时间: {total:.2f}秒")
    print(f"💾 保存: quick_test_stream.wav")

if __name__ == "__main__":
    quick_test()
