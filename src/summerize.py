import os
import sys
import argparse
from typing import Optional, Dict, Any
import google.generativeai as genai
from transcript import get_video_id, get_transcript

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
    if os.environ.get("GOOGLE_API_KEY"):
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    else:
        print("Warning: GOOGLE_API_KEY not found in environment variables")

def summarize_text(
    text: str, 
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
) -> str:
    """
    Summarize text using Google's Gemini Flash model.
    """
    # Create the prompt
    prompt = f"""
You are a helpful assistant that summarizes video content. Please provide a concise summary of the following video transcript. Focus on the main points, key insights, and important details. Make the summary clear, informative, and well-structured. Do not change the language of the text, the summary must have the same language as the input text.
You need to summarize following this OUTPUT format:

OUTPUT:

-Heading of the Text
-Short Introduction
-Main Point
-Final Conclusion
or this if the text is Vietnamese:
-Tiêu đề của văn bản
-Giới thiệu ngắn gọn
-Thông tin chính
-Kết luận 

Each section should enter 2 times to the next row like this :

-Heading of the Text


-Short Introduction


-Main Point


-Final Conclusion


TRANSCRIPT:
{text}
"""

    try:
        # Configure the model with the correct name
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generate the summary
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
        )
        
        # Extract and return the summary
        return response.text.strip()
    
    except Exception as e:
        print(f"Error during summarization: {str(e)}")
        return f"Failed to generate summary: {str(e)}"

def process_video_and_summarize():
    """
    Process a video and summarize its transcript.
    """
    print("\n=== YouTube Video Summarizer ===\n")
    
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
        print(f"\nTranscript retrieved in {language}")
        
        # Generate summary
        print("\nGenerating summary using Gemini 2.0 Flash...")
        summary = summarize_text(transcript_text)
        
        # Print summary
        print("\nSummary:")
        print("=" * 50)
        print(summary)
        print("=" * 50)
        
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    # Set up API keys
    setup_api_keys()
    
    # Process videos in a loop
    while True:
        process_video_and_summarize()
        
        continue_option = input("\nSummarize another video? (y/n): ").strip().lower()
        if continue_option != 'y':
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()
