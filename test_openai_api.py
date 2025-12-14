#!/usr/bin/env python3
"""
Test script for OpenAI-compatible TTS API
Tests all features including streaming, voice selection, and format conversion
"""
import requests
import time
import json
from pathlib import Path

BASE_URL = "http://localhost:7861"
OUTPUT_DIR = Path("test_outputs_openai")
OUTPUT_DIR.mkdir(exist_ok=True)

def test_list_models():
    """Test /v1/models endpoint"""
    print("\n" + "="*60)
    print("TEST 1: List Models")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/v1/models")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Models available: {len(data['data'])}")
        for model in data['data']:
            print(f"  - {model['id']}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_list_voices():
    """Test /v1/voices endpoint"""
    print("\n" + "="*60)
    print("TEST 2: List Voices")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/v1/voices")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Voices available: {len(data['voices'])}")
        for voice in data['voices']:
            print(f"  - {voice['id']}: {voice['name']}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_speech_generation(model="tts-1", voice="alloy", format="mp3", text="Hello, this is a test of the OpenAI compatible API."):
    """Test /v1/audio/speech endpoint"""
    print("\n" + "="*60)
    print(f"TEST: Speech Generation")
    print(f"Model: {model}, Voice: {voice}, Format: {format}")
    print("="*60)
    
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": format,
        "speed": 1.0
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    start_time = time.time()
    first_byte_time = None
    
    response = requests.post(
        f"{BASE_URL}/v1/audio/speech",
        json=payload,
        stream=True
    )
    
    if response.status_code == 200:
        output_file = OUTPUT_DIR / f"test_{model}_{voice}_{format}_{int(time.time())}.{format}"
        
        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    if first_byte_time is None:
                        first_byte_time = time.time()
                        print(f"⏱️  First byte received: {first_byte_time - start_time:.2f}s")
                    f.write(chunk)
        
        total_time = time.time() - start_time
        file_size = output_file.stat().st_size
        
        print(f"✅ Success!")
        print(f"  - First byte latency: {first_byte_time - start_time:.2f}s")
        print(f"  - Total time: {total_time:.2f}s")
        print(f"  - File size: {file_size / 1024:.1f} KB")
        print(f"  - Saved to: {output_file}")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"  Error: {response.text}")
        return False

def test_all_models():
    """Test all available models"""
    print("\n" + "="*60)
    print("TEST 3: All Models")
    print("="*60)
    
    models = ["tts-1", "tts-1-hd", "gpt-4o-mini-tts"]
    text = "Testing different model qualities."
    
    results = []
    for model in models:
        success = test_speech_generation(model=model, voice="alloy", format="mp3", text=text)
        results.append((model, success))
        time.sleep(1)
    
    print("\n" + "="*60)
    print("Model Test Summary:")
    for model, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {model}")
    
    return all(success for _, success in results)

def test_all_voices():
    """Test all available voices"""
    print("\n" + "="*60)
    print("TEST 4: All Voices")
    print("="*60)
    
    voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    text = "This is a voice test."
    
    results = []
    for voice in voices:
        success = test_speech_generation(model="tts-1", voice=voice, format="mp3", text=text)
        results.append((voice, success))
        time.sleep(1)
    
    print("\n" + "="*60)
    print("Voice Test Summary:")
    for voice, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {voice}")
    
    return all(success for _, success in results)

def test_all_formats():
    """Test all audio formats"""
    print("\n" + "="*60)
    print("TEST 5: All Formats")
    print("="*60)
    
    formats = ["mp3", "wav", "opus", "aac", "flac"]
    text = "Testing audio format conversion."
    
    results = []
    for fmt in formats:
        success = test_speech_generation(model="tts-1", voice="alloy", format=fmt, text=text)
        results.append((fmt, success))
        time.sleep(1)
    
    print("\n" + "="*60)
    print("Format Test Summary:")
    for fmt, success in results:
        status = "✅" if success else "❌"
        print(f"  {status} {fmt}")
    
    return all(success for _, success in results)

def test_chinese_text():
    """Test Chinese text generation"""
    print("\n" + "="*60)
    print("TEST 6: Chinese Text")
    print("="*60)
    
    chinese_texts = [
        "你好，这是一个中文语音测试。",
        "今天天气真不错，适合出去散步。",
        "人工智能技术正在改变我们的生活。"
    ]
    
    results = []
    for i, text in enumerate(chinese_texts, 1):
        print(f"\nChinese Test {i}: {text}")
        success = test_speech_generation(model="tts-1", voice="alloy", format="mp3", text=text)
        results.append(success)
        time.sleep(1)
    
    return all(results)

def test_long_text():
    """Test long text generation"""
    print("\n" + "="*60)
    print("TEST 7: Long Text")
    print("="*60)
    
    long_text = """
    The OpenAI Text-to-Speech API provides a simple way to convert text into natural-sounding audio.
    It supports multiple voices and audio formats, making it easy to integrate into various applications.
    The streaming capability allows for real-time audio generation, reducing latency and improving user experience.
    This is particularly useful for applications that require immediate audio feedback.
    """
    
    return test_speech_generation(model="tts-1-hd", voice="nova", format="mp3", text=long_text)

def run_all_tests():
    """Run all tests"""
    print("\n" + "🎯"*30)
    print("OpenAI-Compatible TTS API Test Suite")
    print("🎯"*30)
    
    tests = [
        ("List Models", test_list_models),
        ("List Voices", test_list_voices),
        ("All Models", test_all_models),
        ("All Voices", test_all_voices),
        ("All Formats", test_all_formats),
        ("Chinese Text", test_chinese_text),
        ("Long Text", test_long_text),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with exception: {e}")
            results.append((name, False))
        time.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("FINAL TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! OpenAI API is fully functional.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the logs.")

if __name__ == "__main__":
    run_all_tests()
