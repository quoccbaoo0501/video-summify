import os
import sys
import json
import logging
import traceback
import google.generativeai as genai
from transcript import get_video_id, get_transcript
from typing import Dict, Any, Optional
from summerize import summarize_text  # Make sure to adjust if summerize.py isn't in the same folder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("video-summarizer")

# Default settings
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.7

def setup_api_keys() -> None:
    """
    Set up API keys from .env file.
    """
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    try:
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value
                    except ValueError:
                        # Skip lines that don't have the format KEY=VALUE
                        continue
    
    # Configure Gemini API
    if os.environ.get("GEMINI_API_KEY"):
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    else:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

def process_api_request(input_file: str, output_file: str) -> None:
    """
    Process an API request from input file and write result to output file.
    
    Args:
        input_file: Path to JSON file with input data
        output_file: Path to write output JSON data
    """
    try:
        # Read input data
        logger.info(f"Reading input file: {input_file}")
        with open(input_file, 'r') as f:
            input_data = json.load(f)

        url = input_data.get('url')
        language = input_data.get('language', 'en')
        
        if not url:
            logger.error("URL is required but not provided")
            raise ValueError("URL is required")
        
        # Process the video
        logger.info(f"Processing video URL: {url}")
        video_id = get_video_id(url)
        logger.info(f"Extracted video ID: {video_id}")
        
        try:
            transcript_text = get_transcript(video_id, language)
            logger.info(f"Retrieved transcript ({len(transcript_text)} characters)")
        except Exception as e:
            logger.error(f"Failed to get transcript: {str(e)}")
            raise ValueError(f"Failed to get transcript: {str(e)}")
        
        if not transcript_text or len(transcript_text.strip()) < 10:
            logger.error("Retrieved transcript is empty or too short")
            raise ValueError("Retrieved transcript is empty or too short")
            
        logger.info("Generating summary...")
        summary = summarize_text(transcript_text)
        
        # Prepare output data
        output_data = {
            'video_id': video_id,
            'language': language,
            'summary': summary,
            'video_title': f"YouTube Video ({video_id})"  # In a real implementation, you'd get the actual title
        }
        
        # Write output data
        logger.info(f"Writing output to file: {output_file}")
        with open(output_file, 'w') as f:
            json.dump(output_data, f)
        logger.info("Request processed successfully")
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        logger.debug(traceback.format_exc())
        # Write error to output file
        error_data = {
            'error': str(e),
            'error_type': type(e).__name__
        }
        try:
            with open(output_file, 'w') as f:
                json.dump(error_data, f)
        except Exception as write_error:
            logger.error(f"Failed to write error to output file: {str(write_error)}")
        raise

def main():
    """
    Main function to handle API requests.
    """
    try:
        if len(sys.argv) != 3:
            logger.error("Incorrect number of arguments")
            print("Usage: python summarize_api.py <input_file> <output_file>")
            sys.exit(1)
        
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        
        logger.info("Starting video summarization process")
        
        # Set up API keys
        try:
            setup_api_keys()
            logger.info("API keys configured successfully")
        except Exception as e:
            logger.error(f"Failed to set up API keys: {str(e)}")
            # Write error to output file
            with open(output_file, 'w') as f:
                json.dump({'error': f"API configuration error: {str(e)}"}, f)
            sys.exit(1)
        
        # Process the request
        try:
            process_api_request(input_file, output_file)
        except Exception as e:
            logger.error(f"Error in process_api_request: {str(e)}")
            # The function already writes errors to the output file
            sys.exit(1)
            
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}")
        logger.debug(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 