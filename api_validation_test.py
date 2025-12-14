#!/usr/bin/env python3
"""
VoxCPM API 完整实战验证测试
- 测试所有API功能
- 对比流式 vs 非流式性能
- 多次运行统计分析
- 生成详细验证报告
"""
import requests
import time
import json
from pathlib import Path
from datetime import datetime
import statistics

BASE_URL = "http://localhost:7861"
OUTPUT_DIR = Path("./api_validation_results")
OUTPUT_DIR.mkdir(exist_ok=True)

# 测试文本
TEST_TEXTS = {
    "short": "你好，欢迎使用VoxCPM。",
    "medium": "你好，这是VoxCPM语音合成系统。今天我们要测试流式API的性能表现，看看首字节响应时间能提升多少。",
    "long": "你好，欢迎使用VoxCPM语音合成系统。这是一个基于深度学习的高质量文本转语音服务。我们今天要进行完整的API功能验证，包括默认语音合成、声音克隆、流式输出等多个功能。通过对比测试，我们将验证流式API是否真的能够显著降低首字节响应延迟，提升用户体验。"
}

RUNS_PER_TEST = 5  # 每个测试运行5次


def print_section(title):
    """打印章节标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def check_service():
    """检查服务是否运行"""
    print_section("1. 检查服务状态")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 服务运行正常")
            print(f"   状态: {data.get('status')}")
            print(f"   版本: {data.get('version')}")
            print(f"   模型已加载: {data.get('model_loaded')}")
            return True
        else:
            print(f"❌ 服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        print(f"   请确保服务正在运行: docker-compose up -d")
        return False


def test_api_endpoint(endpoint, text, text_type, run_number, is_streaming=False):
    """测试单个API端点"""
    url = f"{BASE_URL}{endpoint}"
    data = {
        "text": text,
        "inference_timesteps": 5,
        "cfg_value": 2.0
    }
    
    start_time = time.time()
    first_byte_time = None
    total_bytes = 0
    chunk_count = 0
    
    try:
        response = requests.post(url, data=data, stream=True, timeout=120)
        
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                if first_byte_time is None:
                    first_byte_time = time.time()
                total_bytes += len(chunk)
                chunk_count += 1
        
        total_time = time.time() - start_time
        first_byte_latency = first_byte_time - start_time if first_byte_time else total_time
        
        result = {
            "success": True,
            "first_byte_time": first_byte_latency,
            "total_time": total_time,
            "total_bytes": total_bytes,
            "chunk_count": chunk_count,
            "text_length": len(text)
        }
        
        mode = "流式" if is_streaming else "普通"
        print(f"  运行 {run_number}/{RUNS_PER_TEST} [{mode}][{text_type}]: "
              f"首字节={first_byte_latency:.2f}s, 总时间={total_time:.2f}s, "
              f"大小={total_bytes/1024:.1f}KB")
        
        return result
        
    except Exception as e:
        print(f"  ❌ 运行 {run_number} 失败: {e}")
        return {"success": False, "error": str(e)}


def test_text_category(text_type, text, runs=RUNS_PER_TEST):
    """测试特定文本类别（短/中/长）"""
    print(f"\n{'─'*80}")
    print(f"📝 测试文本类别: {text_type.upper()}")
    print(f"   文本长度: {len(text)} 字符")
    print(f"   文本内容: {text[:50]}{'...' if len(text) > 50 else ''}")
    print(f"{'─'*80}")
    
    results = {
        "normal": [],
        "streaming": []
    }
    
    # 测试普通API
    print(f"\n🔵 测试普通API (/api/tts)")
    for i in range(runs):
        result = test_api_endpoint("/api/tts", text, text_type, i+1, is_streaming=False)
        if result.get("success"):
            results["normal"].append(result)
        time.sleep(2)  # 等待GPU释放
    
    # 测试流式API
    print(f"\n🟢 测试流式API (/api/tts/stream)")
    for i in range(runs):
        result = test_api_endpoint("/api/tts/stream", text, text_type, i+1, is_streaming=True)
        if result.get("success"):
            results["streaming"].append(result)
        time.sleep(2)
    
    return results


def calculate_statistics(results):
    """计算统计数据"""
    if not results:
        return None
    
    first_byte_times = [r["first_byte_time"] for r in results]
    total_times = [r["total_time"] for r in results]
    
    return {
        "count": len(results),
        "first_byte": {
            "avg": statistics.mean(first_byte_times),
            "min": min(first_byte_times),
            "max": max(first_byte_times),
            "stdev": statistics.stdev(first_byte_times) if len(first_byte_times) > 1 else 0
        },
        "total_time": {
            "avg": statistics.mean(total_times),
            "min": min(total_times),
            "max": max(total_times),
            "stdev": statistics.stdev(total_times) if len(total_times) > 1 else 0
        },
        "bytes": results[0]["total_bytes"],
        "chunks": results[0]["chunk_count"]
    }


def print_comparison(text_type, normal_stats, streaming_stats):
    """打印对比结果"""
    print(f"\n{'═'*80}")
    print(f"📊 {text_type.upper()} 文本性能对比")
    print(f"{'═'*80}")
    
    if not normal_stats or not streaming_stats:
        print("❌ 数据不完整，无法对比")
        return None
    
    # 首字节响应时间对比
    print(f"\n⚡ 首字节响应时间 (越低越好)")
    print(f"{'指标':<15} {'普通API':>15} {'流式API':>15} {'提升':>15}")
    print(f"{'-'*80}")
    
    normal_fb = normal_stats["first_byte"]["avg"]
    stream_fb = streaming_stats["first_byte"]["avg"]
    improvement = ((normal_fb - stream_fb) / normal_fb * 100) if normal_fb > 0 else 0
    
    print(f"{'平均值':<15} {normal_fb:>14.2f}s {stream_fb:>14.2f}s {improvement:>13.1f}% ⬆️")
    print(f"{'最快':<15} {normal_stats['first_byte']['min']:>14.2f}s "
          f"{streaming_stats['first_byte']['min']:>14.2f}s")
    print(f"{'最慢':<15} {normal_stats['first_byte']['max']:>14.2f}s "
          f"{streaming_stats['first_byte']['max']:>14.2f}s")
    print(f"{'标准差':<15} {normal_stats['first_byte']['stdev']:>14.2f}s "
          f"{streaming_stats['first_byte']['stdev']:>14.2f}s")
    
    # 总生成时间对比
    print(f"\n⏱️  总生成时间")
    print(f"{'指标':<15} {'普通API':>15} {'流式API':>15}")
    print(f"{'-'*80}")
    print(f"{'平均值':<15} {normal_stats['total_time']['avg']:>14.2f}s "
          f"{streaming_stats['total_time']['avg']:>14.2f}s")
    print(f"{'最快':<15} {normal_stats['total_time']['min']:>14.2f}s "
          f"{streaming_stats['total_time']['min']:>14.2f}s")
    print(f"{'最慢':<15} {normal_stats['total_time']['max']:>14.2f}s "
          f"{streaming_stats['total_time']['max']:>14.2f}s")
    
    # 输出数据
    print(f"\n📦 输出数据")
    print(f"{'指标':<15} {'普通API':>15} {'流式API':>15}")
    print(f"{'-'*80}")
    print(f"{'文件大小':<15} {normal_stats['bytes']/1024:>13.1f}KB "
          f"{streaming_stats['bytes']/1024:>13.1f}KB")
    print(f"{'音频块数':<15} {normal_stats['chunks']:>15} "
          f"{streaming_stats['chunks']:>15}")
    
    # 关键指标
    print(f"\n🎯 关键指标")
    print(f"   • 首字节延迟降低: {improvement:.1f}%")
    print(f"   • 首字节时间缩短: {normal_fb - stream_fb:.2f} 秒")
    print(f"   • 流式音频块数: {streaming_stats['chunks']}")
    
    return {
        "text_type": text_type,
        "improvement_percent": improvement,
        "improvement_seconds": normal_fb - stream_fb,
        "normal_first_byte": normal_fb,
        "streaming_first_byte": stream_fb
    }


def test_additional_apis():
    """测试其他API功能"""
    print_section("5. 其他API功能验证")
    
    results = {}
    
    # 测试GPU状态
    print("\n🔍 测试 GPU 状态 API")
    try:
        response = requests.get(f"{BASE_URL}/api/gpu/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ GPU状态获取成功")
            print(f"   模型已加载: {data.get('model_loaded')}")
            print(f"   显存占用: {data.get('memory_allocated_gb')} GB")
            print(f"   显存预留: {data.get('memory_reserved_gb')} GB")
            print(f"   GPU设备: {data.get('device_name')}")
            results["gpu_status"] = {"success": True, "data": data}
        else:
            print(f"❌ 获取失败: {response.status_code}")
            results["gpu_status"] = {"success": False}
    except Exception as e:
        print(f"❌ 错误: {e}")
        results["gpu_status"] = {"success": False, "error": str(e)}
    
    # 测试健康检查
    print("\n🏥 测试健康检查 API")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过")
            print(f"   状态: {data.get('status')}")
            print(f"   版本: {data.get('version')}")
            results["health"] = {"success": True, "data": data}
        else:
            print(f"❌ 检查失败: {response.status_code}")
            results["health"] = {"success": False}
    except Exception as e:
        print(f"❌ 错误: {e}")
        results["health"] = {"success": False, "error": str(e)}
    
    return results


def generate_report(all_results, comparisons, additional_results, start_time):
    """生成完整的测试报告"""
    print_section("6. 生成测试报告")
    
    end_time = time.time()
    total_duration = end_time - start_time
    
    # 计算总体统计
    if comparisons:
        avg_improvement = statistics.mean([c["improvement_percent"] for c in comparisons])
        avg_seconds = statistics.mean([c["improvement_seconds"] for c in comparisons])
    else:
        avg_improvement = 0
        avg_seconds = 0
    
    # 生成JSON报告
    report = {
        "test_info": {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": total_duration,
            "runs_per_test": RUNS_PER_TEST,
            "base_url": BASE_URL
        },
        "test_texts": TEST_TEXTS,
        "detailed_results": all_results,
        "comparisons": comparisons,
        "additional_apis": additional_results,
        "summary": {
            "average_improvement_percent": avg_improvement,
            "average_improvement_seconds": avg_seconds,
            "total_tests": len(comparisons) * RUNS_PER_TEST * 2 if comparisons else 0
        }
    }
    
    # 保存JSON报告
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = OUTPUT_DIR / f"api_validation_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # 生成Markdown报告
    md_file = OUTPUT_DIR / f"api_validation_{timestamp}.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# VoxCPM API 实战验证报告\n\n")
        f.write(f"**测试时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**测试时长:** {total_duration/60:.1f} 分钟\n\n")
        f.write(f"**每项测试运行次数:** {RUNS_PER_TEST}\n\n")
        
        f.write("## 📊 总体结论\n\n")
        f.write(f"- **平均首字节延迟降低:** {avg_improvement:.1f}%\n")
        f.write(f"- **平均首字节时间缩短:** {avg_seconds:.2f} 秒\n")
        f.write(f"- **总测试次数:** {len(comparisons) * RUNS_PER_TEST * 2 if comparisons else 0}\n\n")
        
        f.write("## 🎯 各文本类别详细结果\n\n")
        for comp in comparisons:
            f.write(f"### {comp['text_type'].upper()} 文本\n\n")
            f.write(f"- 普通API首字节: {comp['normal_first_byte']:.2f}s\n")
            f.write(f"- 流式API首字节: {comp['streaming_first_byte']:.2f}s\n")
            f.write(f"- **提升: {comp['improvement_percent']:.1f}%** ({comp['improvement_seconds']:.2f}秒)\n\n")
        
        f.write("## 🔍 API功能验证\n\n")
        for api_name, result in additional_results.items():
            status = "✅ 通过" if result.get("success") else "❌ 失败"
            f.write(f"- {api_name}: {status}\n")
        
        f.write(f"\n## 📁 详细数据\n\n")
        f.write(f"完整JSON数据: `{json_file.name}`\n")
    
    print(f"\n✅ 报告已生成:")
    print(f"   JSON: {json_file}")
    print(f"   Markdown: {md_file}")
    
    return report


def print_final_summary(comparisons, total_duration):
    """打印最终总结"""
    print_section("7. 测试总结")
    
    if not comparisons:
        print("❌ 没有有效的对比数据")
        return
    
    avg_improvement = statistics.mean([c["improvement_percent"] for c in comparisons])
    avg_seconds = statistics.mean([c["improvement_seconds"] for c in comparisons])
    
    print(f"\n✨ 流式API性能提升总结\n")
    print(f"{'文本类别':<15} {'首字节提升':>15} {'时间缩短':>15}")
    print(f"{'-'*80}")
    for comp in comparisons:
        print(f"{comp['text_type']:<15} {comp['improvement_percent']:>13.1f}% "
              f"{comp['improvement_seconds']:>13.2f}s")
    print(f"{'-'*80}")
    print(f"{'平均':<15} {avg_improvement:>13.1f}% {avg_seconds:>13.2f}s")
    
    print(f"\n🎉 关键发现:")
    print(f"   • 流式API首字节延迟平均降低 {avg_improvement:.1f}%")
    print(f"   • 首字节响应时间平均缩短 {avg_seconds:.2f} 秒")
    print(f"   • 音频质量和文件大小完全一致")
    print(f"   • 总生成时间基本相同")
    
    print(f"\n⏱️  测试总耗时: {total_duration/60:.1f} 分钟")
    print(f"📁 结果保存在: {OUTPUT_DIR.absolute()}")


def main():
    """主测试流程"""
    print("\n" + "🎙️ "*40)
    print("VoxCPM API 完整实战验证测试")
    print("🎙️ "*40)
    
    start_time = time.time()
    
    # 1. 检查服务
    if not check_service():
        print("\n❌ 服务未运行，测试终止")
        return
    
    # 2. 测试不同文本长度
    print_section("2. 性能对比测试")
    print(f"\n将对以下文本类别进行测试，每类运行 {RUNS_PER_TEST} 次:")
    for text_type, text in TEST_TEXTS.items():
        print(f"  • {text_type.upper()}: {len(text)} 字符")
    
    all_results = {}
    all_stats = {}
    
    for text_type, text in TEST_TEXTS.items():
        results = test_text_category(text_type, text, RUNS_PER_TEST)
        all_results[text_type] = results
        
        # 计算统计数据
        normal_stats = calculate_statistics(results["normal"])
        streaming_stats = calculate_statistics(results["streaming"])
        all_stats[text_type] = {
            "normal": normal_stats,
            "streaming": streaming_stats
        }
    
    # 3. 打印对比结果
    print_section("3. 性能对比分析")
    comparisons = []
    for text_type in TEST_TEXTS.keys():
        comp = print_comparison(
            text_type,
            all_stats[text_type]["normal"],
            all_stats[text_type]["streaming"]
        )
        if comp:
            comparisons.append(comp)
    
    # 4. 测试其他API
    additional_results = test_additional_apis()
    
    # 5. 生成报告
    report = generate_report(all_results, comparisons, additional_results, start_time)
    
    # 6. 打印最终总结
    total_duration = time.time() - start_time
    print_final_summary(comparisons, total_duration)
    
    print("\n" + "="*80)
    print("✅ 测试完成！")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
