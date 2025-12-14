#!/usr/bin/env python3
"""
流式API性能测试脚本
对比普通API和流式API的响应时间
"""
import requests
import time
from pathlib import Path

BASE_URL = "http://localhost:7861"
OUTPUT_DIR = Path("./test_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def test_normal_api(text, use_prompt=False):
    """测试普通API（等待完整生成）"""
    print("\n" + "="*60)
    print("🔵 测试普通API（非流式）")
    print("="*60)
    
    url = f"{BASE_URL}/api/tts"
    data = {
        "text": text,
        "cfg_value": 2.0,
        "inference_timesteps": 5,
    }
    
    files = {}
    if use_prompt:
        prompt_path = "./examples/example.wav"
        if Path(prompt_path).exists():
            files["prompt_audio"] = open(prompt_path, "rb")
            data["prompt_text"] = "这是参考音频的文本内容"
            print(f"📎 使用参考音频: {prompt_path}")
    
    print(f"📝 输入文本: {text}")
    print(f"⏱️  开始请求...")
    
    start_time = time.time()
    first_byte_time = None
    
    try:
        response = requests.post(url, data=data, files=files, stream=True)
        
        # 记录首字节时间
        chunks = []
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                if first_byte_time is None:
                    first_byte_time = time.time()
                    print(f"⚡ 首字节响应时间: {first_byte_time - start_time:.2f} 秒")
                chunks.append(chunk)
        
        total_time = time.time() - start_time
        
        # 保存音频
        output_file = OUTPUT_DIR / f"normal_{'with_prompt' if use_prompt else 'no_prompt'}.wav"
        with open(output_file, "wb") as f:
            for chunk in chunks:
                f.write(chunk)
        
        file_size = output_file.stat().st_size
        
        print(f"✅ 完成！")
        print(f"📊 总耗时: {total_time:.2f} 秒")
        print(f"📦 文件大小: {file_size / 1024:.1f} KB")
        print(f"💾 保存到: {output_file}")
        
        return {
            "first_byte_time": first_byte_time - start_time if first_byte_time else total_time,
            "total_time": total_time,
            "file_size": file_size
        }
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None
    finally:
        if files:
            for f in files.values():
                f.close()


def test_streaming_api(text, use_prompt=False):
    """测试流式API（边生成边返回）"""
    print("\n" + "="*60)
    print("🟢 测试流式API")
    print("="*60)
    
    url = f"{BASE_URL}/api/tts/stream"
    data = {
        "text": text,
        "cfg_value": 2.0,
        "inference_timesteps": 5,
    }
    
    files = {}
    if use_prompt:
        prompt_path = "./examples/example.wav"
        if Path(prompt_path).exists():
            files["prompt_audio"] = open(prompt_path, "rb")
            data["prompt_text"] = "这是参考音频的文本内容"
            print(f"📎 使用参考音频: {prompt_path}")
    
    print(f"📝 输入文本: {text}")
    print(f"⏱️  开始请求...")
    
    start_time = time.time()
    first_byte_time = None
    chunk_times = []
    
    try:
        response = requests.post(url, data=data, files=files, stream=True)
        
        output_file = OUTPUT_DIR / f"streaming_{'with_prompt' if use_prompt else 'no_prompt'}.wav"
        
        with open(output_file, "wb") as f:
            chunk_count = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    chunk_count += 1
                    current_time = time.time()
                    
                    if first_byte_time is None:
                        first_byte_time = current_time
                        print(f"⚡ 首字节响应时间: {first_byte_time - start_time:.2f} 秒")
                    
                    chunk_times.append(current_time - start_time)
                    f.write(chunk)
                    print(f"  📦 收到第 {chunk_count} 块: {len(chunk)} 字节 (累计 {current_time - start_time:.2f}s)")
        
        total_time = time.time() - start_time
        file_size = output_file.stat().st_size
        
        print(f"✅ 完成！")
        print(f"📊 总耗时: {total_time:.2f} 秒")
        print(f"📦 文件大小: {file_size / 1024:.1f} KB")
        print(f"🎵 收到 {chunk_count} 个音频块")
        print(f"💾 保存到: {output_file}")
        
        return {
            "first_byte_time": first_byte_time - start_time if first_byte_time else total_time,
            "total_time": total_time,
            "file_size": file_size,
            "chunk_count": chunk_count,
            "chunk_times": chunk_times
        }
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None
    finally:
        if files:
            for f in files.values():
                f.close()


def compare_results(normal_result, streaming_result):
    """对比两种API的性能"""
    print("\n" + "="*60)
    print("📊 性能对比")
    print("="*60)
    
    if not normal_result or not streaming_result:
        print("❌ 测试数据不完整，无法对比")
        return
    
    print(f"\n⚡ 首字节响应时间:")
    print(f"  普通API:  {normal_result['first_byte_time']:.2f} 秒")
    print(f"  流式API:  {streaming_result['first_byte_time']:.2f} 秒")
    improvement = (normal_result['first_byte_time'] - streaming_result['first_byte_time']) / normal_result['first_byte_time'] * 100
    print(f"  ⬆️  提升: {improvement:.1f}% ({normal_result['first_byte_time'] - streaming_result['first_byte_time']:.2f}秒)")
    
    print(f"\n⏱️  总生成时间:")
    print(f"  普通API:  {normal_result['total_time']:.2f} 秒")
    print(f"  流式API:  {streaming_result['total_time']:.2f} 秒")
    
    print(f"\n📦 文件大小:")
    print(f"  普通API:  {normal_result['file_size'] / 1024:.1f} KB")
    print(f"  流式API:  {streaming_result['file_size'] / 1024:.1f} KB")
    
    if 'chunk_count' in streaming_result:
        print(f"\n🎵 流式输出:")
        print(f"  音频块数: {streaming_result['chunk_count']}")
        if streaming_result['chunk_times']:
            print(f"  首块时间: {streaming_result['chunk_times'][0]:.2f}s")
            if len(streaming_result['chunk_times']) > 1:
                print(f"  末块时间: {streaming_result['chunk_times'][-1]:.2f}s")


def main():
    print("🎙️ VoxCPM 流式API性能测试")
    print("="*60)
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务未运行，请先启动 VoxCPM 服务")
            return
        print("✅ 服务运行正常")
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        print("请确保 VoxCPM 服务正在运行: docker-compose up -d")
        return
    
    # 测试文本
    test_text = "你好，这是VoxCPM流式语音合成测试。我们正在对比普通API和流式API的性能差异。"
    
    # 测试1: 不使用参考音频
    print("\n\n" + "🔷"*30)
    print("测试场景 1: 使用默认语音（无参考音频）")
    print("🔷"*30)
    
    normal_result_1 = test_normal_api(test_text, use_prompt=False)
    time.sleep(2)  # 等待GPU释放
    streaming_result_1 = test_streaming_api(test_text, use_prompt=False)
    
    if normal_result_1 and streaming_result_1:
        compare_results(normal_result_1, streaming_result_1)
    
    # 测试2: 使用参考音频
    print("\n\n" + "🔶"*30)
    print("测试场景 2: 使用参考音频（声音克隆）")
    print("🔶"*30)
    
    normal_result_2 = test_normal_api(test_text, use_prompt=True)
    time.sleep(2)
    streaming_result_2 = test_streaming_api(test_text, use_prompt=True)
    
    if normal_result_2 and streaming_result_2:
        compare_results(normal_result_2, streaming_result_2)
    
    print("\n\n" + "="*60)
    print("✅ 测试完成！")
    print(f"📁 输出文件保存在: {OUTPUT_DIR.absolute()}")
    print("="*60)


if __name__ == "__main__":
    main()
