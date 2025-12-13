# Changelog

All notable changes to this project will be documented in this file.

## [1.0.8] - 2025-12-13

### Fixed
- Fixed FileNotFoundError when Gradio temporary files are deleted during processing
- Fixed Whisper transcription failure due to missing audio files
- Copy uploaded files to persistent directory immediately to prevent deletion

### Changed
- Improved file handling in voice cloning workflow
- Enhanced error handling for audio file operations

### Tested
- ✅ All API endpoints working correctly
- ✅ Voice cloning with Whisper auto-transcription
- ✅ Model auto-reload after manual offload
- ✅ GPU memory management

## [1.0.7] - 2025-12-13

### Changed
- Disabled automatic GPU model offload
- Model now stays resident in GPU until manual offload
- Removed GPU_IDLE_TIMEOUT monitoring

### Improved
- Eliminated 15-second model reload delay
- Consistent fast response times (~0.5s)
- Better user experience with no lag

## [1.0.6] - 2025-12-13

### Added
- Comprehensive logging for Whisper transcription
- Cache hit/miss indicators in logs

### Fixed
- Gradio file object path handling
- torch.compile cudagraph AssertionError

## [1.0.5] - 2025-12-12

### Fixed
- Audio path extraction for Whisper transcription
- Model.generate call with correct audio path

## [1.0.4] - 2025-12-12

### Added
- Whisper cache mechanism using MD5 hashing
- Exception handling for cache operations

### Fixed
- File path handling for Gradio file objects

## [1.0.3] - 2025-12-12

### Added
- Initial Docker deployment
- FastAPI REST API with 12 VoxCPM parameters
- Gradio Web UI
- MCP protocol integration
- GPU auto-management
- Health monitoring

### Features
- Text-to-Speech synthesis
- Voice cloning with reference audio
- Automatic Whisper transcription
- GPU memory optimization
