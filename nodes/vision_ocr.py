#!/usr/bin/env python3
import sys
import os
import json
import logging

# Mute generic paddle logs from stdout to prevent JSON corruption
logging.getLogger("ppocr").setLevel(logging.ERROR)

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No image file provided."}))
        sys.exit(1)
        
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(json.dumps({"error": f"File not found: {image_path}"}))
        sys.exit(1)
        
    try:
        # Import only when running to save CLI init time if error happens before
        from paddleocr import PaddleOCR
        
        # Initialize PaddleOCR (downloads models automatically if missing)
        ocr = PaddleOCR(use_angle_cls=True, lang='pt', show_log=False)
        
        result = ocr.ocr(image_path, cls=True)
        
        if not result or result[0] is None:
            print(json.dumps({"success": True, "text": ""}))
            sys.exit(0)
            
        # Parse the structured list of boxes and texts
        lines = []
        for idx in range(len(result)):
            res = result[idx]
            for line in res:
                text_content = line[1][0]
                lines.append(text_content)
                
        final_text = "\n".join(lines)
        
        output = {
            "success": True,
            "text": final_text
        }
        print(json.dumps(output))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
