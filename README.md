# Voxtral Speech-to-Text Skill for OpenClaw

## Quick Start

### Option 1: Use in OpenClaw Chat

Type in any chat dialog:
```
voice: record my message
```

### Option 2: Use Shell Script Directly

```bash
# Make executable
chmod +x voice-input.sh

# Record and transcribe (10s default)
./voice-input.sh

# Quick 5-second recording
./voice-input.sh --quick

# Extended 20-second recording
./voice-input.sh --long

# Real-time mic mode (Ctrl+C to stop)
./voice-input.sh --mic
```

### Option 3: Direct Voxtral Commands

```bash
cd ~/.openclaw/workspace/voxtral.c

# Real-time microphone transcription
./voxtral -d voxtral-model --from-mic

# Transcribe audio file
./voxtral -d voxtral-model -i audio.wav
```

## Files

- `__init__.py` - Python skill module for OpenClaw
- `voice-input.sh` - Shell script wrapper
- `SKILL.md` - Full documentation
- `_meta.json` - Skill metadata

## Requirements

- sox: `brew install sox`
- Voxtral binary: `~/.openclaw/workspace/voxtral.c/voxtral`
- Voxtral model: `~/.openclaw/workspace/voxtral.c/voxtral-model`
