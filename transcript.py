from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import os
import sys
import logging
import requests
import re
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("transcript-fetcher")

def get_video_id(url: str) -> str:
    """
    Extract the video ID from various YouTube URL formats.
    
    Supported formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    """
    if not url:
        raise ValueError("URL cannot be empty")
        
    # Handle youtu.be URLs
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    
    # Handle all other YouTube URL formats
    parsed_url = urlparse(url)
    
    # Handle URLs with 'v' parameter (most common format)
    if "youtube.com" in parsed_url.netloc:
        query_params = parse_qs(parsed_url.query)
        if "v" in query_params:
            return query_params["v"][0]
            
        # Handle embed URLs
        path = parsed_url.path
        if path.startswith(("/embed/", "/v/")):
            return path.split("/")[2]
    
    raise ValueError("Could not extract video ID from URL")

def get_transcript_from_api(video_id: str, language: str = 'en') -> str:
    """
    Try to get transcript using youtube_transcript_api
    """
    logger.info(f"Attempting to fetch transcript for video ID {video_id} with language {language} using primary API")
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
    return " ".join([entry["text"] for entry in transcript])

def get_transcript_from_alternative(video_id: str, language: str = 'en') -> str:
    """
    Alternative method to get transcript by simulating browser requests
    """
    logger.info(f"Attempting to fetch transcript for video ID {video_id} with language {language} using alternative method")
    
    # Use a browser-like user agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.youtube.com/',
    }
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch video page, status code: {response.status_code}")
    
    # Try to extract transcript data from the page
    # YouTube stores captions data in a "captionTracks" JSON object in the page source
    captions_regex = r'"captionTracks":\s*(\[.+?\])'
    captions_match = re.search(captions_regex, response.text)
    
    if not captions_match:
        raise Exception("Could not find caption tracks in the video page")
    
    captions_data = json.loads(captions_match.group(1))
    
    if not captions_data:
        raise Exception("No caption tracks available")
    
    # Find the caption track with the requested language
    target_caption = None
    for caption in captions_data:
        if caption.get('languageCode') == language:
            target_caption = caption
            break
    
    # If not found, use the first available caption
    if not target_caption and captions_data:
        target_caption = captions_data[0]
        logger.warning(f"Language {language} not found, using {target_caption.get('languageCode')} instead")
    
    if not target_caption:
        raise Exception(f"No caption track found for language {language}")
    
    # Get the caption track URL
    caption_url = target_caption.get('baseUrl')
    if not caption_url:
        raise Exception("Caption URL not found")
    
    # Add parameters to get plain text format
    caption_url += "&fmt=json3"
    
    # Fetch the captions
    caption_response = requests.get(caption_url, headers=headers)
    if caption_response.status_code != 200:
        raise Exception(f"Failed to fetch captions, status code: {caption_response.status_code}")
    
    try:
        caption_data = caption_response.json()
        events = caption_data.get('events', [])
        
        # Extract text from each caption event
        transcript_text = []
        for event in events:
            if 'segs' in event:
                for seg in event['segs']:
                    if 'utf8' in seg:
                        transcript_text.append(seg['utf8'])
        
        return " ".join(transcript_text).strip()
    except Exception as e:
        raise Exception(f"Failed to parse caption data: {str(e)}")

def get_transcript(video_url_or_id: str, language: str = 'en') -> str:
    """
    Get the transcript from a YouTube video URL or ID.
    Returns the full transcript text as a string.
    
    Args:
        video_url_or_id: YouTube URL or video ID
        language: Preferred language code (default: 'en')
        
    Returns:
        str: Transcript text
    """
    try:
        # Check if input is a URL or an ID
        video_id = video_url_or_id
        if "youtube.com" in video_url_or_id or "youtu.be" in video_url_or_id:
            video_id = get_video_id(video_url_or_id)
        
        logger.info(f"Processing video ID: {video_id}")
        
        # Try to get transcript using main API
        try:
            return get_transcript_from_api(video_id, language)
        except Exception as api_error:
            logger.warning(f"Primary API method failed: {str(api_error)}")
            
            # Try listing available transcripts
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                available_languages = []
                
                logger.info("Available transcripts:")
                
                # List manually created transcripts
                for transcript in transcript_list._manually_created_transcripts.values():
                    logger.info(f" - {transcript.language_code} ({transcript.language})")
                    available_languages.append(transcript.language_code)
                    
                # List generated transcripts
                for transcript in transcript_list._generated_transcripts.values():
                    logger.info(f" - {transcript.language_code} ({transcript.language})")
                    available_languages.append(transcript.language_code)
                
                if available_languages:
                    # If requested language is not available but others are, try to use an alternative language
                    if language not in available_languages and available_languages:
                        alt_language = available_languages[0]
                        logger.info(f"Trying alternative language: {alt_language}")
                        return get_transcript_from_api(video_id, alt_language)
                else:
                    logger.info("No transcripts available through primary API")
            except Exception as list_error:
                logger.warning(f"Failed to list transcripts: {str(list_error)}")
            
            # Try alternative method as a fallback
            logger.info("Trying alternative transcript fetching method...")
            try:
                return get_transcript_from_alternative(video_id, language)
            except Exception as alt_error:
                logger.error(f"Alternative method failed: {str(alt_error)}")
                # Re-raise the original error from the main API
                raise api_error
                
    except Exception as e:
        error_msg = str(e)
        # Add more informative message if we know the video has captions
        if "subtitles are disabled" in error_msg.lower():
            env_info = f"Environment: NODE_ENV={os.environ.get('NODE_ENV')}, RENDER={os.environ.get('RENDER')}"
            logger.error(f"Error getting transcript. {env_info}")
        raise Exception(f"Error getting transcript: {error_msg}")

def process_video():
    """
    Process a video following the simplified workflow:
    1. Ask for language preference (Vietnamese or English)
    2. Get the URL and process
    """
    print("\n=== YouTube Transcript Extractor ===\n")
    
    # Step 1: Ask for language preference
    print("Select transcript language:")
    print("1. English (en)")
    print("2. Vietnamese (vi)")
    
    while True:
        lang_choice = input("Enter your choice (1 or 2): ").strip()
        if lang_choice == "1":
            language = "en"
            break
        elif lang_choice == "2":
            language = "vi"
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")
    
    # Step 2: Get the URL and process
    url = input("\nEnter YouTube URL: ").strip()
    
    if not url:
        print("Error: URL cannot be empty")
        return
    
    try:
        # Extract video ID
        video_id = get_video_id(url)
        print(f"\nProcessing video ID: {video_id}")
        
        # Get transcript
        transcript_text = get_transcript(video_id, language)
        print(f"\nTranscript (in {language}):")
        
        print("=" * 50)
        print(transcript_text)
        print("=" * 50)
        print(f"Transcript length: {len(transcript_text)} characters")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    while True:
        process_video()
        
        continue_option = input("\nProcess another video? (y/n): ").strip().lower()
        if continue_option != 'y':
            print("Goodbye!")
            break