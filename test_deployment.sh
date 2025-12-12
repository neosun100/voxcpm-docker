#!/bin/bash

echo "🧪 VoxCPM Deployment Test Suite"
echo "================================"

PORT=${PORT:-7861}
BASE_URL="http://localhost:$PORT"

# Wait for service
echo "⏳ Waiting for service to start..."
for i in {1..30}; do
    if curl -s "$BASE_URL/health" > /dev/null 2>&1; then
        echo "✅ Service is up!"
        break
    fi
    echo "   Attempt $i/30..."
    sleep 2
done

# Test 1: Health check
echo ""
echo "Test 1: Health Check"
response=$(curl -s "$BASE_URL/health")
if echo "$response" | grep -q "healthy"; then
    echo "✅ PASS: Health check"
else
    echo "❌ FAIL: Health check"
    echo "   Response: $response"
fi

# Test 2: GPU status
echo ""
echo "Test 2: GPU Status"
response=$(curl -s "$BASE_URL/api/gpu/status")
if echo "$response" | grep -q "memory"; then
    echo "✅ PASS: GPU status"
else
    echo "❌ FAIL: GPU status"
    echo "   Response: $response"
fi

# Test 3: Swagger docs
echo ""
echo "Test 3: Swagger Documentation"
status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/apidocs")
if [ "$status" = "200" ]; then
    echo "✅ PASS: Swagger docs accessible"
else
    echo "❌ FAIL: Swagger docs (HTTP $status)"
fi

# Test 4: UI
echo ""
echo "Test 4: UI Interface"
status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/")
if [ "$status" = "200" ]; then
    echo "✅ PASS: UI accessible"
else
    echo "❌ FAIL: UI (HTTP $status)"
fi

# Test 5: TTS API (simple)
echo ""
echo "Test 5: TTS API"
response=$(curl -s -X POST "$BASE_URL/api/tts" \
    -F "text=Test" \
    -F "inference_timesteps=5" \
    --output /tmp/test_output.wav \
    -w "%{http_code}")

if [ "$response" = "200" ] && [ -f /tmp/test_output.wav ]; then
    size=$(stat -f%z /tmp/test_output.wav 2>/dev/null || stat -c%s /tmp/test_output.wav)
    if [ "$size" -gt 1000 ]; then
        echo "✅ PASS: TTS API (output: ${size} bytes)"
    else
        echo "⚠️  WARN: TTS API (output too small: ${size} bytes)"
    fi
else
    echo "❌ FAIL: TTS API (HTTP $response)"
fi

echo ""
echo "================================"
echo "📊 Test Summary"
echo "   Access UI:      $BASE_URL"
echo "   Access API:     $BASE_URL/api"
echo "   Access Swagger: $BASE_URL/apidocs"
echo "================================"
