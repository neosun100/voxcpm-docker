#!/usr/bin/env python3
"""
流式API性能基准测试
生成详细的性能对比报告
"""
import requests
import time
import json
from pathlib import Path
from datetime import datetime

BASE_URL = "http://localhost:7861"
OUTPUT_DIR = Path("./benchmark_results")
OUTPUT_DIR.mkdir(exist_ok=True)

def benchmark_api(endpoint, text, use_prompt=False, runs=3):
    """对API进行多次测试并返回统计数据"""
    results = []
    
    for i in range(runs):
        print(f"  运行 {i+1}/{runs}...", end=" ")
        
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
                data["prompt_text"] = "参考音频文本"
        
        start_time = time.time()
        first_byte_time = None
        total_bytes = 0
        chunk_count = 0
        
        try:
            response = requests.post(
                f"{BASE_URL}{endpoint}",
                data=data,
                files=files,
                stream=True,
                timeout=60
            )
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    if first_byte_time is None:
                        first_byte_time = time.time()
                    total_bytes += len(chunk)
                    chunk_count += 1
            
            total_time = time.time() - start_time
            
            result = {
                "first_byte_time": first_byte_time - start_time if first_byte_time else total_time,
                "total_time": total_time,
                "total_bytes": total_bytes,
                "chunk_count": chunk_count,
                "success": True
            }
            
            print(f"✅ {result['first_byte_time']:.2f}s / {result['total_time']:.2f}s")
            results.append(result)
            
        except Exception as e:
            print(f"❌ {e}")
            results.append({"success": False, "error": str(e)})
        
        finally:
            if files:
                for f in files.values():
                    f.close()
        
        if i < runs - 1:
            time.sleep(2)  # 等待GPU释放
    
    # 计算统计数据
    successful = [r for r in results if r.get("success")]
    if not successful:
        return None
    
    return {
        "runs": len(successful),
        "first_byte_avg": sum(r["first_byte_time"] for r in successful) / len(successful),
        "first_byte_min": min(r["first_byte_time"] for r in successful),
        "first_byte_max": max(r["first_byte_time"] for r in successful),
        "total_time_avg": sum(r["total_time"] for r in successful) / len(successful),
        "total_time_min": min(r["total_time"] for r in successful),
        "total_time_max": max(r["total_time"] for r in successful),
        "total_bytes": successful[0]["total_bytes"],
        "chunk_count": successful[0].get("chunk_count", 1),
    }


def print_report(normal_stats, streaming_stats, scenario_name):
    """打印性能对比报告"""
    print("\n" + "="*70)
    print(f"📊 {scenario_name} - 性能对比报告")
    print("="*70)
    
    if not normal_stats or not streaming_stats:
        print("❌ 测试数据不完整")
        return
    
    print(f"\n⚡ 首字节响应时间 (越低越好)")
    print(f"{'':20} {'普通API':>15} {'流式API':>15} {'提升':>15}")
    print("-"*70)
    print(f"{'平均':20} {normal_stats['first_byte_avg']:>14.2f}s {streaming_stats['first_byte_avg']:>14.2f}s", end="")
    improvement = (normal_stats['first_byte_avg'] - streaming_stats['first_byte_avg']) / normal_stats['first_byte_avg'] * 100
    print(f" {improvement:>13.1f}% ⬆️")
    print(f"{'最快':20} {normal_stats['first_byte_min']:>14.2f}s {streaming_stats['first_byte_min']:>14.2f}s")
    print(f"{'最慢':20} {normal_stats['first_byte_max']:>14.2f}s {streaming_stats['first_byte_max']:>14.2f}s")
    
    print(f"\n⏱️  总生成时间")
    print(f"{'':20} {'普通API':>15} {'流式API':>15}")
    print("-"*70)
    print(f"{'平均':20} {normal_stats['total_time_avg']:>14.2f}s {streaming_stats['total_time_avg']:>14.2f}s")
    print(f"{'最快':20} {normal_stats['total_time_min']:>14.2f}s {streaming_stats['total_time_min']:>14.2f}s")
    print(f"{'最慢':20} {normal_stats['total_time_max']:>14.2f}s {streaming_stats['total_time_max']:>14.2f}s")
    
    print(f"\n📦 输出数据")
    print(f"{'':20} {'普通API':>15} {'流式API':>15}")
    print("-"*70)
    print(f"{'文件大小':20} {normal_stats['total_bytes']/1024:>13.1f}KB {streaming_stats['total_bytes']/1024:>13.1f}KB")
    print(f"{'音频块数':20} {normal_stats['chunk_count']:>15} {streaming_stats['chunk_count']:>15}")
    
    print(f"\n🎯 关键指标")
    print(f"  • 首字节延迟降低: {improvement:.1f}%")
    print(f"  • 首字节时间缩短: {normal_stats['first_byte_avg'] - streaming_stats['first_byte_avg']:.2f}秒")
    print(f"  • 流式音频块数: {streaming_stats['chunk_count']}")
    
    return {
        "scenario": scenario_name,
        "normal": normal_stats,
        "streaming": streaming_stats,
        "improvement_percent": improvement,
        "improvement_seconds": normal_stats['first_byte_avg'] - streaming_stats['first_byte_avg']
    }


def main():
    print("🎙️ VoxCPM 流式API性能基准测试")
    print("="*70)
    
    # 检查服务
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ 服务未运行")
            return
        print("✅ 服务运行正常\n")
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        return
    
    test_text = "你好，这是VoxCPM流式语音合成性能测试。我们正在对比普通API和流式API的响应时间差异。"
    runs = 3
    
    all_results = []
    
    # 场景1: 默认语音
    print("\n" + "🔷"*35)
    print("场景 1: 默认语音（无参考音频）")
    print("🔷"*35)
    
    print("\n🔵 测试普通API...")
    normal_stats_1 = benchmark_api("/api/tts", test_text, use_prompt=False, runs=runs)
    
    print("\n🟢 测试流式API...")
    streaming_stats_1 = benchmark_api("/api/tts/stream", test_text, use_prompt=False, runs=runs)
    
    result_1 = print_report(normal_stats_1, streaming_stats_1, "默认语音")
    if result_1:
        all_results.append(result_1)
    
    # 场景2: 声音克隆
    print("\n\n" + "🔶"*35)
    print("场景 2: 声音克隆（使用参考音频）")
    print("🔶"*35)
    
    print("\n🔵 测试普通API...")
    normal_stats_2 = benchmark_api("/api/tts", test_text, use_prompt=True, runs=runs)
    
    print("\n🟢 测试流式API...")
    streaming_stats_2 = benchmark_api("/api/tts/stream", test_text, use_prompt=True, runs=runs)
    
    result_2 = print_report(normal_stats_2, streaming_stats_2, "声音克隆")
    if result_2:
        all_results.append(result_2)
    
    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = OUTPUT_DIR / f"benchmark_{timestamp}.json"
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "test_text": test_text,
            "runs_per_test": runs,
            "results": all_results
        }, f, indent=2, ensure_ascii=False)
    
    # 总结
    print("\n\n" + "="*70)
    print("📈 总体性能提升")
    print("="*70)
    
    if all_results:
        avg_improvement = sum(r["improvement_percent"] for r in all_results) / len(all_results)
        avg_seconds = sum(r["improvement_seconds"] for r in all_results) / len(all_results)
        
        print(f"\n✨ 流式API平均性能提升:")
        print(f"  • 首字节延迟降低: {avg_improvement:.1f}%")
        print(f"  • 首字节时间缩短: {avg_seconds:.2f}秒")
        print(f"  • 测试场景数: {len(all_results)}")
        print(f"  • 每场景测试次数: {runs}")
    
    print(f"\n💾 详细报告已保存: {report_file}")
    print("\n✅ 基准测试完成！")
    print("="*70)


if __name__ == "__main__":
    main()
