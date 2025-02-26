import sys
import json
import io
import os
import importlib.util
import pathlib

# Dynamically add the parent directory to the path to ensure imports work
current_dir = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(current_dir))

from transcript import get_video_id, get_transcript
from summerize import setup_api_keys, summarize_text

def main():
    # Set UTF-8 encoding for stdout to handle Unicode characters
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    # Check if we have the right number of arguments
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing video URL"}))
        sys.exit(1)
    
    # Get arguments
    video_url = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else 'en'
    
    try:
        # Set up API keys
        setup_api_keys()
        
        # Get video ID
        video_id = get_video_id(video_url)
        
        # Get transcript
        transcript = get_transcript(video_id, language)
        
        # Generate summary
        summary = summarize_text(transcript)
        
        # Print the summary (will be captured by Node.js)
        print(summary)
        
    except Exception as e:
        error_message = str(e)
        print(json.dumps({"error": error_message}))
        sys.exit(1)

if __name__ == "__main__":
    # Set UTF-8 as the default encoding for the process
    os.environ["PYTHONIOENCODING"] = "utf-8"
    main() 