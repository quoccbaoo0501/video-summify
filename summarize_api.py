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

def log_environment_info():
    """
    Log information about the current environment for debugging purposes.
    """
    logger.info("Environment Information:")
    logger.info(f"NODE_ENV: {os.environ.get('NODE_ENV', 'not set')}")
    logger.info(f"RENDER: {os.environ.get('RENDER', 'not set')}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info(f"Files in current directory: {', '.join(os.listdir('.')[:10])}...")

def process_api_request(input_file: str, output_file: str) -> None:
    """
    Process an API request from input file and write result to output file.
    
    Args:
        input_file: Path to JSON file with input data
        output_file: Path to write output JSON data
    """
    try:
        # Log environment information for debugging
        log_environment_info()
        
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
        
        # Check if we're in the Render environment
        is_render = os.environ.get('RENDER') == 'true'
        
        # Try multiple times to get the transcript with different methods
        max_retries = 3
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Transcript retrieval attempt {attempt}/{max_retries}")
                transcript_text = get_transcript(video_id, language)
                transcript_length = len(transcript_text)
                logger.info(f"Retrieved transcript ({transcript_length} characters)")
                
                if transcript_length < 10:
                    logger.warning("Retrieved transcript is very short, might be incomplete")
                
                # If we got here, we have a transcript
                break
                
            except Exception as e:
                last_error = e
                logger.error(f"Attempt {attempt} failed: {str(e)}")
                if attempt == max_retries:
                    logger.error(f"All {max_retries} attempts to get transcript failed")
                    # Create more specific error message for no transcripts case
                    error_msg = str(last_error)
                    if "subtitles are disabled" in error_msg.lower() or "no transcripts available" in error_msg.lower() or "does not have available subtitles" in error_msg:
                        # Write a user-friendly error response for videos without subtitles
                        error_data = {
                            'error': "This video does not have subtitles/captions available. Please try a different video that has captions enabled.",
                            'error_type': "NoTranscriptAvailable",
                            'video_id': video_id,
                            'suggestion': "YouTube requires videos to have captions/subtitles for summarization to work."
                        }
                        with open(output_file, 'w') as f:
                            json.dump(error_data, f)
                        logger.info("Wrote no-transcript error response to output file")
                        return  # Exit without raising an exception
                    else:
                        # For other types of errors
                        raise ValueError(f"Failed to get transcript after {max_retries} attempts: {str(last_error)}")
        
        # If we're here, we have a transcript
        if not transcript_text or len(transcript_text.strip()) < 10:
            logger.error("Retrieved transcript is empty or too short")
            # Handle empty transcript case with user-friendly error
            error_data = {
                'error': "Retrieved transcript is too short to generate a meaningful summary.",
                'error_type': "EmptyTranscript",
                'video_id': video_id,
                'suggestion': "Please try a video with more substantial captions."
            }
            with open(output_file, 'w') as f:
                json.dump(error_data, f)
            logger.info("Wrote empty-transcript error response to output file")
            return  # Exit without raising an exception
            
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
        error_message = str(e)
        error_type = type(e).__name__
        
        # Check for common error types and provide user-friendly messages
        if "subtitles are disabled" in error_message.lower() or "no transcripts available" in error_message.lower() or "does not have available subtitles" in error_message:
            error_type = "NoTranscriptAvailable"
            error_message = "This video does not have subtitles/captions available. Please try a different video that has captions enabled."
        
        error_data = {
            'error': error_message,
            'error_type': error_type,
            'suggestion': "YouTube requires videos to have captions/subtitles for summarization to work."
        }
        
        try:
            with open(output_file, 'w') as f:
                json.dump(error_data, f)
        except Exception as write_error:
            logger.error(f"Failed to write error to output file: {str(write_error)}")
        # Don't re-raise the exception since we've already handled it by writing to the output file
        return

def main():
    """
    Main function to handle API requests.
    """
    exit_code = 0  # Default to success
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
            exit_code = 1
        
        if exit_code == 0:  # Only proceed if API keys were successfully configured
            # Process the request
            try:
                process_api_request(input_file, output_file)
            except Exception as e:
                logger.error(f"Error in process_api_request: {str(e)}")
                # The process_api_request function already writes errors to the output file
                # But we don't need to exit with an error code because we've handled the error gracefully
                # Only set exit_code if it's a critical error that should be propagated
                if "This video does not have" not in str(e) and "no transcripts available" not in str(e).lower():
                    exit_code = 1
            
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}")
        logger.debug(traceback.format_exc())
        # Try to write a generic error response if possible
        try:
            output_file = sys.argv[2] if len(sys.argv) >= 3 else "error_output.json"
            with open(output_file, 'w') as f:
                json.dump({
                    'error': f"An unexpected error occurred: {str(e)}", 
                    'error_type': "UnhandledException"
                }, f)
        except Exception:
            pass
        exit_code = 1
    
    # Exit with appropriate code
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 