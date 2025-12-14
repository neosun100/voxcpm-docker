# OpenAI-Compatible TTS API

VoxCPM now provides a fully OpenAI-compatible Text-to-Speech API, allowing seamless integration with any application that uses OpenAI's TTS service.

## 🎯 Features

- ✅ **100% OpenAI API Compatible** - Drop-in replacement for OpenAI TTS
- ✅ **Streaming Audio** - Real-time audio generation with low latency
- ✅ **Multiple Voices** - 11 voice options (alloy, echo, fable, onyx, nova, shimmer, ash, ballad, coral, sage, verse)
- ✅ **Multiple Formats** - mp3, wav, opus, aac, flac, pcm
- ✅ **Multiple Models** - tts-1 (fast), tts-1-hd (high quality), gpt-4o-mini-tts (balanced)
- ✅ **Chinese & English** - Full multilingual support

## 📡 API Endpoints

### Base URL
```
http://localhost:7861/v1
```

### 1. Create Speech (POST /v1/audio/speech)

Generate audio from text input.

**Request Body:**
```json
{
  "model": "tts-1",
  "input": "Hello, this is a test.",
  "voice": "alloy",
  "response_format": "mp3",
  "speed": 1.0
}
```

**Parameters:**
- `model` (required): `tts-1`, `tts-1-hd`, or `gpt-4o-mini-tts`
- `input` (required): Text to convert to speech (max 4096 characters)
- `voice` (required): Voice selection (see available voices below)
- `response_format` (optional): Audio format - `mp3`, `opus`, `aac`, `flac`, `wav`, `pcm` (default: `mp3`)
- `speed` (optional): Speed of audio (0.25 to 4.0, default: 1.0)

**Response:**
- Streaming audio data in the specified format

### 2. List Models (GET /v1/models)

Get available TTS models.

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "tts-1",
      "object": "model",
      "created": 1699053241,
      "owned_by": "voxcpm"
    },
    {
      "id": "tts-1-hd",
      "object": "model",
      "created": 1699053241,
      "owned_by": "voxcpm"
    },
    {
      "id": "gpt-4o-mini-tts",
      "object": "model",
      "created": 1699053241,
      "owned_by": "voxcpm"
    }
  ]
}
```

### 3. List Voices (GET /v1/voices)

Get available voice options.

**Response:**
```json
{
  "voices": [
    {"id": "alloy", "name": "Alloy"},
    {"id": "echo", "name": "Echo"},
    {"id": "fable", "name": "Fable"},
    {"id": "onyx", "name": "Onyx"},
    {"id": "nova", "name": "Nova"},
    {"id": "shimmer", "name": "Shimmer"},
    {"id": "ash", "name": "Ash"},
    {"id": "ballad", "name": "Ballad"},
    {"id": "coral", "name": "Coral"},
    {"id": "sage", "name": "Sage"},
    {"id": "verse", "name": "Verse"}
  ]
}
```

## 💻 Usage Examples

### cURL

```bash
# Basic usage
curl http://localhost:7861/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "Hello, this is a test of the VoxCPM OpenAI-compatible API.",
    "voice": "alloy"
  }' \
  --output speech.mp3

# High quality with different voice
curl http://localhost:7861/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1-hd",
    "input": "This is high quality audio.",
    "voice": "nova",
    "response_format": "wav"
  }' \
  --output speech.wav

# Chinese text
curl http://localhost:7861/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "你好，这是一个中文语音测试。",
    "voice": "alloy"
  }' \
  --output chinese.mp3
```

### Python (OpenAI SDK)

```python
from openai import OpenAI

# Point to VoxCPM server
client = OpenAI(
    api_key="not-needed",  # VoxCPM doesn't require API key
    base_url="http://localhost:7861/v1"
)

# Generate speech
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input="Hello, this is a test of the VoxCPM API."
)

# Save to file
response.stream_to_file("output.mp3")
```

### Python (Requests)

```python
import requests

url = "http://localhost:7861/v1/audio/speech"
payload = {
    "model": "tts-1",
    "input": "Hello world!",
    "voice": "alloy",
    "response_format": "mp3"
}

response = requests.post(url, json=payload, stream=True)

with open("output.mp3", "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
```

### JavaScript/Node.js

```javascript
import OpenAI from 'openai';
import fs from 'fs';

const openai = new OpenAI({
  apiKey: 'not-needed',
  baseURL: 'http://localhost:7861/v1'
});

async function generateSpeech() {
  const mp3 = await openai.audio.speech.create({
    model: "tts-1",
    voice: "alloy",
    input: "Hello, this is a test.",
  });
  
  const buffer = Buffer.from(await mp3.arrayBuffer());
  await fs.promises.writeFile("speech.mp3", buffer);
}

generateSpeech();
```

## 🎨 Available Voices

All 11 OpenAI voices are supported:

| Voice | Description |
|-------|-------------|
| alloy | Neutral and balanced |
| echo | Clear and articulate |
| fable | Expressive and warm |
| onyx | Deep and authoritative |
| nova | Energetic and friendly |
| shimmer | Soft and gentle |
| ash | Clear and professional |
| ballad | Smooth and melodic |
| coral | Warm and conversational |
| sage | Wise and measured |
| verse | Poetic and expressive |

**Note:** Currently all voices map to the same VoxCPM model. Voice-specific characteristics will be added in future updates.

## 🎯 Model Comparison

| Model | Quality | Speed | Use Case |
|-------|---------|-------|----------|
| tts-1 | Standard | Fast (5 steps) | Real-time applications, quick testing |
| tts-1-hd | High | Slower (10 steps) | High-quality audio, production use |
| gpt-4o-mini-tts | Balanced | Medium (7 steps) | General purpose, good balance |

## 📊 Performance

- **First-byte latency**: ~0.08s (streaming)
- **Generation speed**: 10-30s depending on text length and model
- **Supported text length**: Up to 4096 characters
- **Audio quality**: 44.1kHz, 16-bit PCM

## 🔄 Migration from OpenAI

To migrate from OpenAI TTS to VoxCPM:

1. **Change base URL**:
   ```python
   # Before
   client = OpenAI(api_key="sk-...")
   
   # After
   client = OpenAI(
       api_key="not-needed",
       base_url="http://localhost:7861/v1"
   )
   ```

2. **No other code changes needed** - All parameters and responses are identical

3. **Remove API key requirements** - VoxCPM doesn't require authentication

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_openai_api.py
```

This will test:
- ✅ Model listing
- ✅ Voice listing
- ✅ All models (tts-1, tts-1-hd, gpt-4o-mini-tts)
- ✅ All voices (11 voices)
- ✅ All formats (mp3, wav, opus, aac, flac)
- ✅ Chinese text support
- ✅ Long text generation

## 🚀 Quick Start

1. **Start the service**:
   ```bash
   docker-compose up -d
   ```

2. **Test the API**:
   ```bash
   curl http://localhost:7861/v1/audio/speech \
     -H "Content-Type: application/json" \
     -d '{"model": "tts-1", "input": "Hello!", "voice": "alloy"}' \
     --output test.mp3
   ```

3. **Play the audio**:
   ```bash
   mpv test.mp3  # or any audio player
   ```

## 📝 API Compatibility

This implementation is compatible with:
- ✅ OpenAI Python SDK
- ✅ OpenAI Node.js SDK
- ✅ Any HTTP client (curl, requests, fetch, etc.)
- ✅ Applications using OpenAI TTS API

## 🔧 Advanced Features

### Custom Voice Upload

While the OpenAI API doesn't support custom voices, VoxCPM's native API does:

```bash
# Use VoxCPM native API for custom voice
curl http://localhost:7861/api/tts/stream \
  -F "text=Hello with custom voice" \
  -F "prompt_audio=@my_voice.wav" \
  -F "prompt_text=Reference transcript" \
  -o output.wav
```

### Preset Voice IDs

Use VoxCPM's preset voice feature for faster generation:

```bash
curl http://localhost:7861/api/tts/stream \
  -F "text=Hello" \
  -F "voice_id=default" \
  -o output.wav
```

## 🐛 Troubleshooting

### Audio format conversion fails

If you get format conversion errors, ensure ffmpeg is installed:
```bash
docker exec -it voxcpm-service apt-get update && apt-get install -y ffmpeg
```

### Slow generation

- Use `tts-1` model for faster generation
- Reduce text length
- Use preset voices via native API

### Connection refused

Ensure the service is running:
```bash
docker ps | grep voxcpm
curl http://localhost:7861/health
```

## 📚 Related Documentation

- [Streaming API Guide](STREAMING_API_TEST_GUIDE.md)
- [Voice ID Feature](VOICE_ID_FEATURE.md)
- [Performance Report](STREAMING_SUCCESS_REPORT.md)
- [Main README](README.md)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Voice-specific model fine-tuning
- Additional audio format support
- Performance optimizations
- Better error handling

## 📄 License

Apache License 2.0 - Same as VoxCPM project
