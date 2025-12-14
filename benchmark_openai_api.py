#!/usr/bin/env python3
"""
OpenAI API Benchmark Test
测试不同文本长度和语音设置下的性能
"""
import requests
import time
import json
from pathlib import Path
import statistics

BASE_URL = "https://voxcpm-tts.aws.xin"
OUTPUT_DIR = Path("benchmark_openai_results")
OUTPUT_DIR.mkdir(exist_ok=True)

# 测试文本
TEST_TEXTS = {
    "short": "你好，这是一个简短的测试。",
    "medium": "人工智能技术正在快速发展，语音合成作为其中的重要分支，已经在多个领域得到了广泛应用。VoxCPM 提供了高质量的语音合成服务。",
    "long": "在当今数字化时代，人工智能技术的发展日新月异，其中语音合成技术作为人机交互的重要组成部分，正在经历着革命性的变革。从早期的机械式合成到现在的神经网络驱动的自然语音生成，技术的进步让机器的声音越来越接近真人。VoxCPM 作为新一代的语音合成系统，采用了先进的深度学习模型，能够生成高质量、自然流畅的语音。无论是在智能客服、有声读物、还是辅助技术领域，语音合成都展现出了巨大的应用价值。"
}

def upload_voice_and_get_id(audio_file_path):
    """上传语音文件并获取 voice_id（模拟预设语音）"""
    # 注意：当前 OpenAI API 不支持上传，我们使用预设的 voice_id
    # 这里返回默认的 voice_id
    return "default"

def test_openai_api(text, voice="alloy", model="tts-1", format="mp3", run_num=1):
    """测试 OpenAI API"""
    print(f"\n{'='*60}")
    print(f"Run #{run_num}: {len(text)} chars, voice={voice}, model={model}")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/v1/audio/speech"
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": format
    }
    
    start_time = time.time()
    first_byte_time = None
    total_bytes = 0
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=120)
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return None
        
        # 接收流式数据
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                if first_byte_time is None:
                    first_byte_time = time.time()
                    first_byte_latency = first_byte_time - start_time
                    print(f"⏱️  首字节延迟: {first_byte_latency:.3f}s")
                total_bytes += len(chunk)
        
        total_time = time.time() - start_time
        
        result = {
            "text_length": len(text),
            "voice": voice,
            "model": model,
            "format": format,
            "first_byte_latency": first_byte_latency,
            "total_time": total_time,
            "total_bytes": total_bytes,
            "throughput_kbps": (total_bytes * 8 / 1024) / total_time if total_time > 0 else 0
        }
        
        print(f"✅ 完成!")
        print(f"   首字节: {first_byte_latency:.3f}s")
        print(f"   总时间: {total_time:.3f}s")
        print(f"   文件大小: {total_bytes/1024:.1f} KB")
        print(f"   吞吐量: {result['throughput_kbps']:.1f} Kbps")
        
        return result
        
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None

def test_native_api_with_voice_id(text, voice_id="default", run_num=1):
    """测试原生 API 使用 voice_id"""
    print(f"\n{'='*60}")
    print(f"Run #{run_num} (Native API): {len(text)} chars, voice_id={voice_id}")
    print(f"{'='*60}")
    
    url = f"{BASE_URL}/api/tts/stream"
    
    data = {
        "text": text,
        "voice_id": voice_id,
        "cfg_value": "2.0",
        "inference_timesteps": "5"
    }
    
    start_time = time.time()
    first_byte_time = None
    total_bytes = 0
    
    try:
        response = requests.post(url, data=data, stream=True, timeout=120)
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return None
        
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                if first_byte_time is None:
                    first_byte_time = time.time()
                    first_byte_latency = first_byte_time - start_time
                    print(f"⏱️  首字节延迟: {first_byte_latency:.3f}s")
                total_bytes += len(chunk)
        
        total_time = time.time() - start_time
        
        result = {
            "text_length": len(text),
            "voice_id": voice_id,
            "api_type": "native",
            "first_byte_latency": first_byte_latency,
            "total_time": total_time,
            "total_bytes": total_bytes,
            "throughput_kbps": (total_bytes * 8 / 1024) / total_time if total_time > 0 else 0
        }
        
        print(f"✅ 完成!")
        print(f"   首字节: {first_byte_latency:.3f}s")
        print(f"   总时间: {total_time:.3f}s")
        print(f"   文件大小: {total_bytes/1024:.1f} KB")
        
        return result
        
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None

def run_benchmark():
    """运行完整的 benchmark"""
    print("\n" + "🎯"*30)
    print("OpenAI API Benchmark Test")
    print("🎯"*30)
    
    all_results = []
    
    # 测试配置
    test_configs = [
        # OpenAI API 测试
        {"api": "openai", "text_type": "short", "model": "tts-1", "voice": "alloy", "runs": 3},
        {"api": "openai", "text_type": "medium", "model": "tts-1", "voice": "alloy", "runs": 3},
        {"api": "openai", "text_type": "long", "model": "tts-1", "voice": "alloy", "runs": 3},
        {"api": "openai", "text_type": "medium", "model": "tts-1-hd", "voice": "nova", "runs": 3},
        
        # Native API 测试（使用 voice_id）
        {"api": "native", "text_type": "short", "voice_id": "default", "runs": 3},
        {"api": "native", "text_type": "medium", "voice_id": "default", "runs": 3},
        {"api": "native", "text_type": "long", "voice_id": "default", "runs": 3},
    ]
    
    for config in test_configs:
        text = TEST_TEXTS[config["text_type"]]
        runs = config["runs"]
        
        print(f"\n{'#'*60}")
        print(f"测试配置: {config}")
        print(f"{'#'*60}")
        
        run_results = []
        
        for i in range(runs):
            time.sleep(2)  # 避免请求过快
            
            if config["api"] == "openai":
                result = test_openai_api(
                    text=text,
                    voice=config["voice"],
                    model=config["model"],
                    run_num=i+1
                )
            else:  # native
                result = test_native_api_with_voice_id(
                    text=text,
                    voice_id=config["voice_id"],
                    run_num=i+1
                )
            
            if result:
                result["config"] = config
                run_results.append(result)
        
        if run_results:
            # 计算统计数据
            first_byte_latencies = [r["first_byte_latency"] for r in run_results]
            total_times = [r["total_time"] for r in run_results]
            
            summary = {
                "config": config,
                "runs": len(run_results),
                "first_byte_latency": {
                    "mean": statistics.mean(first_byte_latencies),
                    "min": min(first_byte_latencies),
                    "max": max(first_byte_latencies),
                    "stdev": statistics.stdev(first_byte_latencies) if len(first_byte_latencies) > 1 else 0
                },
                "total_time": {
                    "mean": statistics.mean(total_times),
                    "min": min(total_times),
                    "max": max(total_times),
                    "stdev": statistics.stdev(total_times) if len(total_times) > 1 else 0
                },
                "results": run_results
            }
            
            all_results.append(summary)
            
            print(f"\n📊 统计结果:")
            print(f"   首字节延迟: {summary['first_byte_latency']['mean']:.3f}s ± {summary['first_byte_latency']['stdev']:.3f}s")
            print(f"   总时间: {summary['total_time']['mean']:.3f}s ± {summary['total_time']['stdev']:.3f}s")
    
    # 保存结果
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    json_file = OUTPUT_DIR / f"benchmark_openai_{timestamp}.json"
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 结果已保存到: {json_file}")
    
    # 生成 Markdown 报告
    generate_report(all_results, timestamp)
    
    return all_results

def generate_report(results, timestamp):
    """生成 Markdown 报告"""
    md_file = OUTPUT_DIR / f"benchmark_openai_{timestamp}.md"
    
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# OpenAI API Benchmark Report\n\n")
        f.write(f"**测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**测试服务器**: {BASE_URL}\n\n")
        
        f.write("## 测试配置\n\n")
        f.write("| API | 文本类型 | 文本长度 | 模型/语音 | 运行次数 |\n")
        f.write("|-----|---------|---------|----------|----------|\n")
        
        for result in results:
            config = result["config"]
            text_len = len(TEST_TEXTS[config["text_type"]])
            if config["api"] == "openai":
                model_voice = f"{config['model']}/{config['voice']}"
            else:
                model_voice = f"voice_id={config['voice_id']}"
            
            f.write(f"| {config['api']} | {config['text_type']} | {text_len} | {model_voice} | {result['runs']} |\n")
        
        f.write("\n## 性能结果\n\n")
        f.write("| API | 文本类型 | 首字节延迟 (s) | 总时间 (s) | 文件大小 (KB) |\n")
        f.write("|-----|---------|----------------|-----------|-------------|\n")
        
        for result in results:
            config = result["config"]
            fb_mean = result["first_byte_latency"]["mean"]
            fb_std = result["first_byte_latency"]["stdev"]
            tt_mean = result["total_time"]["mean"]
            tt_std = result["total_time"]["stdev"]
            
            avg_size = statistics.mean([r["total_bytes"]/1024 for r in result["results"]])
            
            f.write(f"| {config['api']} | {config['text_type']} | "
                   f"{fb_mean:.3f} ± {fb_std:.3f} | "
                   f"{tt_mean:.3f} ± {tt_std:.3f} | "
                   f"{avg_size:.1f} |\n")
        
        f.write("\n## 详细数据\n\n")
        
        for i, result in enumerate(results, 1):
            config = result["config"]
            f.write(f"### 测试 {i}: {config['api']} - {config['text_type']}\n\n")
            
            f.write("| Run | 首字节延迟 (s) | 总时间 (s) | 文件大小 (KB) | 吞吐量 (Kbps) |\n")
            f.write("|-----|----------------|-----------|--------------|---------------|\n")
            
            for j, run in enumerate(result["results"], 1):
                f.write(f"| {j} | {run['first_byte_latency']:.3f} | "
                       f"{run['total_time']:.3f} | "
                       f"{run['total_bytes']/1024:.1f} | "
                       f"{run['throughput_kbps']:.1f} |\n")
            
            f.write(f"\n**平均首字节延迟**: {result['first_byte_latency']['mean']:.3f}s\n")
            f.write(f"**平均总时间**: {result['total_time']['mean']:.3f}s\n\n")
    
    print(f"✅ 报告已保存到: {md_file}")

if __name__ == "__main__":
    run_benchmark()
