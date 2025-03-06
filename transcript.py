from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

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
        
        # Try to get transcript in preferred language
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            return " ".join([entry["text"] for entry in transcript])
                
        except Exception as e:
            # If preferred language not available, show available languages
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available_languages = []
            
            print("\nTranscript not available in selected language.")
            print("Available languages:")
            
            # List manually created transcripts
            for transcript in transcript_list._manually_created_transcripts.values():
                print(f" - {transcript.language_code} ({transcript.language})")
                available_languages.append(transcript.language_code)
                
            # List generated transcripts
            for transcript in transcript_list._generated_transcripts.values():
                print(f" - {transcript.language_code} ({transcript.language})")
                available_languages.append(transcript.language_code)
            
            if available_languages:
                raise Exception(f"Please try one of the available language codes listed above.")
            else:
                raise Exception(f"No transcripts available for this video")
                
    except Exception as e:
        raise Exception(f"Error getting transcript: {str(e)}")

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