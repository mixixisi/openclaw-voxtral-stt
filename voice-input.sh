#!/bin/bash
# Voxtral Voice Recording and Transcription Script
# Usage: ./voice-input.sh [options]
#
# Options:
#   -r, --record    Record and transcribe (default)
#   -q, --quick     Quick 5-second recording
#   -l, --long      Extended 20-second recording
#   -m, --mic       Use Voxtral's built-in mic mode
#   -h, --help      Show this help

set -e

# Configuration
VOXTRAL_DIR="$HOME/.openclaw/workspace/voxtral.c"
VOXTRAL_BIN="$VOXTRAL_DIR/voxtral"
VOXTRAL_MODEL="$VOXTRAL_DIR/voxtral-model"
RECORDINGS_DIR="$HOME/.openclaw/workspace/voxtral-recordings"
TEMP_FILE="$RECORDINGS_DIR/recording_$(date +%s).wav"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check dependencies
check_dependencies() {
    if [ ! -f "$VOXTRAL_BIN" ]; then
        echo -e "${RED}❌ Voxtral binary not found at $VOXTRAL_BIN${NC}"
        exit 1
    fi
    
    if [ ! -d "$VOXTRAL_MODEL" ]; then
        echo -e "${RED}❌ Voxtral model not found at $VOXTRAL_MODEL${NC}"
        exit 1
    fi
    
    if ! command -v rec &> /dev/null; then
        echo -e "${RED}❌ sox 'rec' command not found. Install with: brew install sox${NC}"
        exit 1
    fi
}

# Show help
show_help() {
    cat << EOF
🎙️ Voxtral Voice Input Script

Usage: $0 [options]

Options:
  -r, --record    Record and transcribe (default 10s)
  -q, --quick     Quick 5-second recording
  -l, --long      Extended 20-second recording
  -m, --mic       Use Voxtral's built-in microphone mode
  -h, --help      Show this help

Examples:
  $0                    # Record and transcribe
  $0 --quick            # Quick 5-second recording
  $0 --long             # Record for up to 20 seconds
  $0 --mic              # Real-time mic mode (Ctrl+C to stop)

Requirements:
  - sox (brew install sox)
  - Voxtral at ~/.openclaw/workspace/voxtral.c/voxtral
  - Voxtral model at ~/.openclaw/workspace/voxtral.c/voxtral-model

EOF
}

# Record audio with sox
record_audio() {
    local duration=$1
    local timeout=$((duration + 5))
    
    # Create recordings directory if needed
    mkdir -p "$RECORDINGS_DIR"
    
    echo -e "${YELLOW}🎤 Recording for up to ${duration}s (press Enter to stop early)...${NC}"
    
    # Record using sox
    rec -b 16 -r 16000 -c 1 -e signed-integer "$TEMP_FILE" \
        silence 1 0.3 1% \
        $duration 2>/dev/null || true
    
    if [ -f "$TEMP_FILE" ] && [ -s "$TEMP_FILE" ]; then
        echo -e "${GREEN}✅ Recording saved: $TEMP_FILE${NC}"
        echo "$TEMP_FILE"
        return 0
    else
        echo -e "${RED}❌ Recording failed${NC}"
        return 1
    fi
}

# Transcribe audio file
transcribe_file() {
    local audio_file=$1
    
    echo -e "${YELLOW}📝 Transcribing with Voxtral...${NC}"
    
    # Run Voxtral
    if output=$("$VOXTRAL_BIN" -d "$VOXTRAL_MODEL" -i "$audio_file" --silent 2>&1); then
        echo -e "${GREEN}🎙️ Transcription:${NC}"
        echo ""
        echo "$output"
        echo ""
        
        # Clean up temp file
        rm -f "$audio_file"
    else
        echo -e "${RED}❌ Transcription failed${NC}"
        echo "$output"
        return 1
    fi
}

# Real-time microphone mode
mic_mode() {
    echo -e "${YELLOW}🎤 Starting Voxtral microphone mode...${NC}"
    echo -e "${YELLOW}Press Ctrl+C when done speaking.${NC}"
    echo ""
    
    cd "$VOXTRAL_DIR"
    ./voxtral -d "$VOXTRAL_MODEL" --from-mic
}

# Main
main() {
    check_dependencies
    
    case "${1:-}" in
        -h|--help|"")
            show_help
            ;;
        -q|--quick)
            echo -e "${GREEN}🔹 Quick Recording Mode (5s)${NC}"
            audio=$(record_audio 5)
            if [ -n "$audio" ]; then
                transcribe_file "$audio"
            fi
            ;;
        -l|--long)
            echo -e "${GREEN}🔹 Long Recording Mode (20s)${NC}"
            audio=$(record_audio 20)
            if [ -n "$audio" ]; then
                transcribe_file "$audio"
            fi
            ;;
        -m|--mic)
            mic_mode
            ;;
        -r|--record|*)
            echo -e "${GREEN}🔹 Recording Mode (default 10s)${NC}"
            audio=$(record_audio 10)
            if [ -n "$audio" ]; then
                transcribe_file "$audio"
            fi
            ;;
    esac
}

main "$@"
