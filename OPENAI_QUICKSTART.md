# OpenAI API Quick Start Guide

## 🚀 5-Minute Setup

### 1. Restart Service
```bash
docker-compose restart
```

### 2. Verify Service
```bash
# Check health
curl http://localhost:7861/health

# List models
curl http://localhost:7861/v1/models

# List voices
curl http://localhost:7861/v1/voices
```

### 3. Generate Your First Audio
```bash
curl http://localhost:7861/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Hello! This is VoxCPM speaking.",
    "voice": "alloy"
  }' \
  --output hello.mp3

# Play it
mpv hello.mp3
```

## 🐍 Python Example

```python
from openai import OpenAI

# Configure client
client = OpenAI(
    api_key="not-needed",
    base_url="http://localhost:7861/v1"
)

# Generate speech
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello from VoxCPM!"
)

# Save to file
response.stream_to_file("output.mp3")
print("✅ Audio saved to output.mp3")
```

## 🧪 Run Tests

```bash
# Install dependencies
pip install requests openai

# Run comprehensive tests
python test_openai_api.py
```

## 📊 Expected Results

- ✅ First-byte latency: ~0.08s
- ✅ Total generation: 10-30s
- ✅ Audio quality: 44.1kHz
- ✅ All formats supported: mp3, wav, opus, aac, flac

## 🎯 Use Cases

### 1. Replace OpenAI TTS
```python
# Just change the base_url
client = OpenAI(
    api_key="not-needed",
    base_url="http://localhost:7861/v1"  # ← Only change this
)
```

### 2. Chinese Text
```bash
curl http://localhost:7861/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "你好，欢迎使用VoxCPM。",
    "voice": "nova"
  }' \
  --output chinese.mp3
```

### 3. High Quality
```bash
curl http://localhost:7861/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "High quality audio generation.",
    "voice": "shimmer",
    "response_format": "wav"
  }' \
  --output hq.wav
```

## 🔧 Troubleshooting

### Service not responding
```bash
docker-compose logs -f voxcpm
docker-compose restart
```

### Format conversion fails
```bash
# Install ffmpeg in container
docker exec -it voxcpm-service apt-get update
docker exec -it voxcpm-service apt-get install -y ffmpeg
```

### Slow generation
- Use `tts-1` instead of `tts-1-hd`
- Reduce text length
- Check GPU status: `curl http://localhost:7861/api/gpu/status`

## 📚 Next Steps

- Read full documentation: [OPENAI_API.md](OPENAI_API.md)
- Explore streaming API: [STREAMING_API_TEST_GUIDE.md](STREAMING_API_TEST_GUIDE.md)
- Check performance: [STREAMING_SUCCESS_REPORT.md](STREAMING_SUCCESS_REPORT.md)

## 🎉 Success Indicators

You're ready when:
- ✅ Health check returns `{"status": "healthy"}`
- ✅ Models endpoint returns 3 models
- ✅ Voices endpoint returns 11 voices
- ✅ First audio generation completes in <30s
- ✅ Test script passes all tests

---

**Need help?** Check the logs: `docker-compose logs -f voxcpm`
