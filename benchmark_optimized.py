#!/usr/bin/env python3
"""
Optimized OpenAI API Benchmark - WAV format only
对比优化前后的性能差异
"""
import requests
import time
import json
from pathlib import Path
import statistics

BASE_URL = "http://localhost:7861"
OUTPUT_DIR = Path("benchmark_optimized_results")
OUTPUT_DIR.mkdir(exist_ok=True)

TEST_TEXTS = {
    "short": "你好，这是一个简短的测试。",
    "medium": "人工智能技术正在快速发展，语音合成作为其中的重要分支，已经在多个领域得到了广泛应用。VoxCPM 提供了高质量的语音合成服务。",
    "long": "在当今数字化时代，人工智能技术的发展日新月异，其中语音合成技术作为人机交互的重要组成部分，正在经历着革命性的变革。从早期的机械式合成到现在的神经网络驱动的自然语音生成，技术的进步让机器的声音越来越接近真人。VoxCPM 作为新一代的语音合成系统，采用了先进的深度学习模型，能够生成高质量、自然流畅的语音。"
}

def test_api(text, api_type, format="wav", run_num=1):
    """测试 API"""
    print(f"\n{'='*60}")
    print(f"Run #{run_num}: {api_type}, {len(text)} chars, format={format}")
    print(f"{'='*60}")
    
    if api_type == "openai":
        url = f"{BASE_URL}/v1/audio/speech"
        payload = {
            "model": "tts-1",
            "input": text,
            "voice": "alloy",
            "response_format": format
        }
        response = requests.post(url, json=payload, stream=True, timeout=120)
    else:  # native
        url = f"{BASE_URL}/api/tts/stream"
        data = {
            "text": text,
            "voice_id": "default",
            "cfg_value": "2.0",
            "inference_timesteps": "5"
        }
        response = requests.post(url, data=data, stream=True, timeout=120)
    
    start_time = time.time()
    first_byte_time = None
    total_bytes = 0
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        return None
    
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            if first_byte_time is None:
                first_byte_time = time.time()
                first_byte_latency = first_byte_time - start_time
                print(f"⏱️  首字节: {first_byte_latency:.3f}s")
            total_bytes += len(chunk)
    
    total_time = time.time() - start_time
    
    result = {
        "api_type": api_type,
        "format": format,
        "text_length": len(text),
        "first_byte_latency": first_byte_latency,
        "total_time": total_time,
        "total_bytes": total_bytes
    }
    
    print(f"✅ 完成! 首字节: {first_byte_latency:.3f}s, 总时间: {total_time:.3f}s, 大小: {total_bytes/1024:.1f}KB")
    return result

def run_benchmark():
    """运行优化后的 benchmark"""
    print("\n" + "🎯"*30)
    print("Optimized OpenAI API Benchmark - WAV Format")
    print("🎯"*30)
    
    all_results = []
    
    # 测试配置：对比 OpenAI WAV vs Native
    configs = [
        {"api": "openai", "format": "wav", "text": "short", "runs": 5},
        {"api": "native", "format": "wav", "text": "short", "runs": 5},
        {"api": "openai", "format": "wav", "text": "medium", "runs": 5},
        {"api": "native", "format": "wav", "text": "medium", "runs": 5},
        {"api": "openai", "format": "wav", "text": "long", "runs": 5},
        {"api": "native", "format": "wav", "text": "long", "runs": 5},
    ]
    
    for config in configs:
        text = TEST_TEXTS[config["text"]]
        print(f"\n{'#'*60}")
        print(f"测试: {config['api']} - {config['text']} ({len(text)} chars)")
        print(f"{'#'*60}")
        
        run_results = []
        for i in range(config["runs"]):
            time.sleep(1)
            result = test_api(text, config["api"], config["format"], i+1)
            if result:
                run_results.append(result)
        
        if run_results:
            fb_latencies = [r["first_byte_latency"] for r in run_results]
            total_times = [r["total_time"] for r in run_results]
            
            summary = {
                "config": config,
                "runs": len(run_results),
                "first_byte_latency": {
                    "mean": statistics.mean(fb_latencies),
                    "min": min(fb_latencies),
                    "max": max(fb_latencies),
                    "stdev": statistics.stdev(fb_latencies) if len(fb_latencies) > 1 else 0
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
            
            print(f"\n📊 统计:")
            print(f"   首字节: {summary['first_byte_latency']['mean']:.3f}s ± {summary['first_byte_latency']['stdev']:.3f}s")
            print(f"   总时间: {summary['total_time']['mean']:.3f}s ± {summary['total_time']['stdev']:.3f}s")
    
    # 保存结果
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    json_file = OUTPUT_DIR / f"benchmark_optimized_{timestamp}.json"
    
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    # 生成报告
    generate_report(all_results, timestamp)
    
    return all_results

def generate_report(results, timestamp):
    """生成对比报告"""
    md_file = OUTPUT_DIR / f"benchmark_optimized_{timestamp}.md"
    
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# OpenAI API 优化后性能报告\n\n")
        f.write(f"**测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("**优化内容**: 使用 WAV 格式，避免 MP3 编码转换\n\n")
        
        f.write("## 性能对比\n\n")
        f.write("| API | 文本 | 首字节延迟 (s) | 总时间 (s) | 文件大小 (KB) |\n")
        f.write("|-----|------|----------------|-----------|-------------|\n")
        
        for result in results:
            config = result["config"]
            fb = result["first_byte_latency"]["mean"]
            fb_std = result["first_byte_latency"]["stdev"]
            tt = result["total_time"]["mean"]
            tt_std = result["total_time"]["stdev"]
            size = statistics.mean([r["total_bytes"]/1024 for r in result["results"]])
            
            f.write(f"| {config['api']} | {config['text']} | "
                   f"{fb:.3f} ± {fb_std:.3f} | "
                   f"{tt:.3f} ± {tt_std:.3f} | "
                   f"{size:.1f} |\n")
        
        # 计算改进
        f.write("\n## 性能改进分析\n\n")
        
        for i in range(0, len(results), 2):
            if i+1 < len(results):
                openai_result = results[i]
                native_result = results[i+1]
                
                text_type = openai_result["config"]["text"]
                
                openai_fb = openai_result["first_byte_latency"]["mean"]
                native_fb = native_result["first_byte_latency"]["mean"]
                fb_diff = ((openai_fb - native_fb) / native_fb) * 100
                
                openai_tt = openai_result["total_time"]["mean"]
                native_tt = native_result["total_time"]["mean"]
                tt_diff = ((openai_tt - native_tt) / native_tt) * 100
                
                f.write(f"### {text_type.upper()} 文本\n\n")
                f.write(f"- **首字节延迟**: OpenAI {openai_fb:.3f}s vs Native {native_fb:.3f}s ({fb_diff:+.1f}%)\n")
                f.write(f"- **总时间**: OpenAI {openai_tt:.3f}s vs Native {native_tt:.3f}s ({tt_diff:+.1f}%)\n\n")
    
    print(f"\n✅ 报告已保存: {md_file}")

if __name__ == "__main__":
    run_benchmark()
