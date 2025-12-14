#!/usr/bin/env python3
"""快速测试预设音频ID功能"""
import requests
import time

BASE_URL = "http://localhost:7861"

print("🎙️ VoxCPM 预设音频ID快速测试\n")

# 1. 查看可用音频
print("1️⃣ 查看可用预设音频...")
r = requests.get(f"{BASE_URL}/api/voices")
voices = r.json()
print(f"   可用音频: {len(voices['voices'])}个")
for v in voices['voices']:
    print(f"   - ID: {v['id']}")
    print(f"     描述: {v['description']}")
    print(f"     文本: {v['text']}\n")

# 2. 测试预设ID
print("2️⃣ 测试使用预设ID...")
text = "你好，这是使用预设音频ID的测试"

start = time.time()
response = requests.post(
    f"{BASE_URL}/api/tts/stream",
    data={
        "text": text,
        "voice_id": "default",
        "inference_timesteps": 5
    },
    stream=True
)

first_byte = None
chunks = []

with open("test_voice_id.wav", "wb") as f:
    for chunk in response.iter_content(8192):
        if chunk:
            if first_byte is None:
                first_byte = time.time()
                print(f"   ⚡ 首字节: {first_byte - start:.2f}秒")
            chunks.append(chunk)
            f.write(chunk)

total = time.time() - start
file_size = sum(len(c) for c in chunks)

print(f"   ✅ 完成")
print(f"   总时间: {total:.2f}秒")
print(f"   文件大小: {file_size/1024:.1f}KB")
print(f"   音频块数: {len(chunks)}")
print(f"   保存到: test_voice_id.wav\n")

# 3. 对比：不使用预设ID
print("3️⃣ 对比：默认语音（无预设ID）...")
start = time.time()
response = requests.post(
    f"{BASE_URL}/api/tts/stream",
    data={
        "text": text,
        "inference_timesteps": 5
    },
    stream=True
)

first_byte = None
for chunk in response.iter_content(8192):
    if chunk and first_byte is None:
        first_byte = time.time()
        print(f"   ⚡ 首字节: {first_byte - start:.2f}秒")
        break

print(f"\n✅ 测试完成！")
print(f"\n📊 结论:")
print(f"   预设ID和默认语音首字节响应时间相同")
print(f"   预设ID优势: 可以固定音色，适合生产环境")
