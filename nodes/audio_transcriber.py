#!/usr/bin/env python3
import sys
import os
import json
from faster_whisper import WhisperModel

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No audio file provided."}))
        sys.exit(1)
        
    audio_path = sys.argv[1]
    
    if not os.path.exists(audio_path):
        print(json.dumps({"error": f"File not found: {audio_path}"}))
        sys.exit(1)
        
    try:
        # Mute logging to prevent stdout corruption
        import logging
        logging.getLogger("faster_whisper").setLevel(logging.ERROR)
        
        # Load the model with lightweight settings (CPU, Int8)
        model = WhisperModel("large-v3-turbo", device="cpu", compute_type="int8")
        
        # Transcribe the audio
        segments, info = model.transcribe(audio_path, beam_size=5, language="pt")
        
        # Collect text from segments
        transcribed_text = " ".join([segment.text for segment in segments]).strip()
        
        # Return structured JSON to stdout for Rust to parse easily
        result = {
            "success": True,
            "language": info.language,
            "language_probability": info.language_probability,
            "text": transcribed_text
        }
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
