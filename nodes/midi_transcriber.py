#!/usr/bin/env python3
import sys
import os
import json

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Requires input_audio_path and output_directory."}))
        sys.exit(1)
        
    audio_path = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(audio_path):
        print(json.dumps({"error": f"File not found: {audio_path}"}))
        sys.exit(1)
        
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        from basic_pitch.inference import predict_and_save
        
        predict_and_save(
            [audio_path],
            output_dir,
            save_midi=True,
            sonify_midi=False,
            save_model_outputs=False,
            save_notes=False
        )
        
        output = {
            "success": True,
            "output_dir": output_dir,
            "message": "MIDI generated successfully."
        }
        print(json.dumps(output))
        
    except Exception as e:
        import traceback
        err_msg = str(e) + "\n" + traceback.format_exc()
        print(json.dumps({"error": err_msg}))
        sys.exit(1)

if __name__ == "__main__":
    main()
