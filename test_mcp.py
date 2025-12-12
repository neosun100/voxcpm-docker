#!/usr/bin/env python3
"""
Simple MCP client test for VoxCPM
"""
import asyncio
import json
from pathlib import Path

async def test_mcp():
    print("🧪 Testing VoxCPM MCP Server")
    print("=" * 50)
    
    # Note: This is a simplified test
    # In production, use proper MCP client library
    
    print("\n📋 Available Tools:")
    print("1. text_to_speech - Convert text to speech")
    print("2. voice_cloning - Clone voice from reference")
    print("3. get_gpu_status - Check GPU status")
    print("4. offload_model - Unload model from GPU")
    
    print("\n✅ MCP server configuration:")
    config_path = Path("mcp_client.json")
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            print(json.dumps(config, indent=2))
    else:
        print("❌ mcp_client.json not found")
    
    print("\n📖 Usage:")
    print("1. Add mcp_client.json to your MCP client config")
    print("2. Call tools through your MCP client")
    print("3. See MCP_GUIDE.md for detailed examples")

if __name__ == "__main__":
    asyncio.run(test_mcp())
