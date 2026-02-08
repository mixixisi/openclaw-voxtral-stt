#!/usr/bin/env python3
"""
Voxtral Speech-to-Text Skill for OpenClaw

This skill provides voice input capability by recording audio from the microphone
and transcribing it using the Voxtral model.

Requirements:
- sox (for audio recording): brew install sox
- Voxtral binary: ~/.openclaw/workspace/voxtral.c/voxtral
- Voxtral model: ~/.openclaw/workspace/voxtral.c/voxtral-model

Usage in chat:
- "voice: record my message" - Records and transcribes
- "voice: transcribe" - Transcribes recorded audio
- "voice: help" - Shows usage instructions
"""

import os
import sys
import json
import tempfile
import subprocess
import signal
from pathlib import Path

# Configuration
VOXTRAL_BIN = Path.home() / ".openclaw/workspace/voxtral.c/voxtral"
VOXTRAL_MODEL = Path.home() / ".openclaw/workspace/voxtral.c/voxtral-model"
DEFAULT_AUDIO_FORMAT = "wav"
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHANNELS = 1


class VoxtralSkill:
    """Voice input skill using Voxtral speech-to-text."""
    
    def __init__(self):
        self.voxtral_bin = VOXTRAL_BIN
        self.voxtral_model = VOXTRAL_MODEL
        self.temp_dir = Path.home() / ".openclaw/workspace/voxtral-recordings"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def _check_dependencies(self) -> tuple[bool, str]:
        """Check if required dependencies are available."""
        # Check Voxtral binary
        if not self.voxtral_bin.exists():
            return False, f"Voxtral binary not found at {self.voxtral_bin}"
        
        # Check Voxtral model
        if not self.voxtral_model.exists():
            return False, f"Voxtral model not found at {self.voxtral_model}"
        
        # Check sox for recording
        try:
            subprocess.run(["which", "sox"], capture_output=True, check=True)
        except subprocess.CalledProcessError:
            return False, "sox not found. Install with: brew install sox"
        
        return True, "OK"
    
    def _record_audio(self, duration: int = 10, timeout: int = 15) -> Path | None:
        """
        Record audio from microphone using sox.
        
        Args:
            duration: Maximum recording duration in seconds
            timeout: Timeout for recording command
            
        Returns:
            Path to recorded audio file, or None on failure
        """
        timestamp = int(Path.home() / ".openclaw/workspace".stat().st_mtime * 1000)
        output_file = self.temp_dir / f"recording_{timestamp}.wav"
        
        # sox command for recording
        cmd = [
            "rec",
            "-b", "16",           # 16-bit
            "-r", str(DEFAULT_SAMPLE_RATE),  # Sample rate
            "-c", str(DEFAULT_CHANNELS),    # Mono
            "-e", "signed-integer",  # Signed integer
            str(output_file),
            "silence", "1", "0.3", "1%",    # Stop on 1 second of silence
            str(duration)                    # Max duration
        ]
        
        try:
            # Check if we can record (sox might prompt for microphone access)
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 5,
                # Don't wait for input - use silence detection
                input="n\n"  # Answer "no" to any prompts, rely on silence detection
            )
            
            if output_file.exists() and output_file.stat().st_size > 1000:
                return output_file
            else:
                print(f"Recording failed: file not created or too small", file=sys.stderr)
                return None
                
        except subprocess.TimeoutExpired:
            print(f"Recording timed out after {timeout}s", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Recording error: {e}", file=sys.stderr)
            return None
    
    def _transcribe_file(self, audio_file: Path) -> str:
        """
        Transcribe an audio file using Voxtral.
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            Transcribed text
        """
        if not audio_file.exists():
            return "Error: Audio file not found"
        
        cmd = [
            str(self.voxtral_bin),
            "-d", str(self.voxtral_model),
            "-i", str(audio_file),
            "--silent"  # Suppress stderr output
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                return f"Transcription error: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return "Transcription timed out"
        except Exception as e:
            return f"Transcription error: {e}"
    
    def _transcribe_mic_realtime(self) -> str:
        """
        Use Voxtral's built-in microphone mode.
        This opens the microphone and transcribes in real-time.
        
        Note: This runs Voxtral directly with --from-mic flag.
        The user can speak and see transcription as they speak.
        """
        cmd = [
            str(self.voxtral_bin),
            "-d", str(self.voxtral_model),
            "--from-mic",
            "--silent"
        ]
        
        try:
            print("\n🎤 Speak now (press Ctrl+C when done)...\n")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # Max 60 seconds of recording
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return "Microphone transcription was interrupted or failed."
                
        except subprocess.TimeoutExpired:
            return "Recording timed out (max 60 seconds)"
        except KeyboardInterrupt:
            return "Recording cancelled by user"
        except Exception as e:
            return f"Microphone error: {e}"
    
    def process_command(self, command: str) -> str:
        """
        Process a voice command.
        
        Args:
            command: Command string (e.g., "record my message")
            
        Returns:
            Response text
        """
        cmd = command.lower().strip()
        
        # Check dependencies first
        ok, msg = self._check_dependencies()
        if not ok:
            return f"❌ {msg}"
        
        # Help command
        if cmd in ["help", "--help", "-h", "usage"]:
            return self.get_help()
        
        # Record and transcribe
        if "record" in cmd or "voice" in cmd:
            # Check for duration parameter
            duration = 10
            if "quick" in cmd:
                duration = 5
            elif "long" in cmd:
                duration = 20
            
            # Option 1: Record to file then transcribe
            print("🎤 Recording audio...")
            audio_file = self._record_audio(duration=duration)
            
            if audio_file:
                print(f"📝 Transcribing: {audio_file.name}")
                result = self._transcribe_file(audio_file)
                return f"🎙️ Transcribed:\n\n{result}"
            else:
                # Fall back to realtime mode
                print("Trying realtime microphone mode...")
                return self._transcribe_mic_realtime()
        
        # Just transcribe (if user has a file)
        if "transcribe" in cmd:
            return "Use 'voice: record my message' to record and transcribe."
        
        # Unknown command
        return self.get_help()
    
    def get_help(self) -> str:
        """Return help text."""
        return """
🎙️ **Voxtral Voice Input Skill**

**Commands:**
- `voice: record my message` - Record audio and transcribe
- `voice: quick record` - Quick 5-second recording
- `voice: long record` - Extended 20-second recording
- `voice: transcribe` - Show transcription help
- `voice: help` - Show this help

**Requirements:**
- sox (brew install sox)
- Voxtral at ~/.openclaw/workspace/voxtral.c/voxtral
- Voxtral model at ~/.openclaw/workspace/voxtral.c/voxtral-model

**Note:** For direct microphone access, you can also run:
```
cd ~/.openclaw/workspace/voxtral.c && ./voxtral -d voxtral-model --from-mic
```
"""


def main():
    """Main entry point for the skill."""
    skill = VoxtralSkill()
    
    # Get command from args or stdin
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
    else:
        # Read from stdin
        command = sys.stdin.read().strip()
    
    if not command:
        print(skill.get_help())
        return
    
    result = skill.process_command(command)
    print(result)


if __name__ == "__main__":
    main()
