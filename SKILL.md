---
description: Voxtral speech-to-text integration for voice input in OpenClaw chat
---

# Voxtral Speech-to-Text Skill

**Voice input capability for OpenClaw using Mistral AI's Voxtral model.**

This skill enables voice input in any chat dialog by recording audio from your microphone and transcribing it using the high-performance Voxtral speech-to-text model.

## 🎯 Features

- **Voice Recording** - Record audio from your Mac's microphone
- **High-Quality Transcription** - Powered by Voxtral Mini 4B (Mistral AI)
- **Real-time Support** - Use Voxtral's built-in microphone mode for live transcription
- **Chat Integration** - Returns transcribed text for use in any chat platform

## 🚀 Quick Start

### Prerequisites

1. **Voxtral binary and model** (already installed):
   - Binary: `~/.openclaw/workspace/voxtral.c/voxtral`
   - Model: `~/.openclaw/workspace/voxtral.c/voxtral-model`

2. **sox** (for audio recording):
   ```bash
   brew install sox
   ```

### Basic Usage

In any OpenClaw chat, type:

```
voice: record my message
```

This will:
1. Start recording from your microphone
2. Transcribe the audio using Voxtral
3. Return the transcribed text

## 📖 Usage Commands

| Command | Description |
|---------|-------------|
| `voice: record my message` | Record and transcribe (default 10s) |
| `voice: quick record` | Quick 5-second recording |
| `voice: long record` | Extended 20-second recording |
| `voice: help` | Show help and usage |

## 🔧 Advanced Options

### Direct Voxtral Commands

For more control, you can use Voxtral directly:

**Real-time Microphone Transcription:**
```bash
cd ~/.openclaw/workspace/voxtral.c && ./voxtral -d voxtral-model --from-mic
```
Press **Ctrl+C** to stop recording. Transcription appears as you speak.

**Transcribe Audio File:**
```bash
./voxtral -d voxtral-model -i audio.wav --silent
```

**Lower Latency Mode:**
```bash
./voxtral -d voxtral-model --from-mic -I 1.0
```

### Audio Recording Options

The skill uses `sox rec` with these settings:
- **Format**: 16-bit signed integer WAV
- **Sample Rate**: 16kHz
- **Channels**: Mono (1)
- **Silence Detection**: Auto-stops on 1 second of silence
- **Max Duration**: 10 seconds (configurable)

## 💡 Chat Integration Examples

### Telegram

Simply type in any chat:
```
voice: record my message
```

The transcribed text will be inserted into your message.

### Multi-Line Transcriptions

For longer transcriptions, the output includes formatting:
```
🎙️ Transcribed:

Hello, this is a test of the voice input system.
How does this sound to you?
```

## 🛠️ Troubleshooting

### "sox not found"
Install sox: `brew install sox`

### "Voxtral binary not found"
Ensure Voxtral is installed at: `~/.openclaw/workspace/voxtral.c/voxtral`

### "Microphone permission denied"
Grant microphone access in:
- **System Settings** → **Privacy & Security** → **Microphone**

### Poor Transcription Quality

1. **Speak clearly** and at normal pace
2. **Reduce background noise**
3. **Get closer to the microphone**
4. **Try the real-time mode** for longer inputs

### Recording Issues

Try direct Voxtral microphone mode:
```bash
cd ~/.openclaw/workspace/voxtral.c && ./voxtral -d voxtral-model --from-mic
```

## 📊 Performance

| Metric | Value |
|--------|-------|
| Model Size | ~4B parameters |
| Audio Format | 16kHz, mono, 16-bit |
| Real-time Factor | ~2.5x faster than real-time |
| Supported Languages | EN, ES, FR, PT, HI, DE, NL, IT, AR, RU, ZH, JA, KO |

## 📁 Files

| File | Purpose |
|------|---------|
| `__init__.py` | Main skill implementation |
| `SKILL.md` | This documentation |
| `_meta.json` | Skill metadata |
| `.clawhub/` | OpenClaw configuration |

## 🔗 References

- **Voxtral Project**: `~/.openclaw/workspace/voxtral.c/`
- **Voxtral README**: `~/.openclaw/workspace/voxtral.c/README.md`
- **Mistral Voxtral Model**: [HuggingFace](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602)

---

**Built for OpenClaw** - Voice-powered chat automation 🦞
