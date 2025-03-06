import os
import sys
import argparse
from typing import Optional, Dict, Any
import google.generativeai as genai
from transcript import get_video_id, get_transcript
# Import the quiz functionality
# from quiz import generate_quiz_questions, run_quiz_in_terminal, export_quiz_to_json
from quiz_api import generate_quiz_questions  # adjust if run_quiz_in_terminal, export_quiz_to_json also exist in quiz_api
# Import the flashcards functionality
from flashcards_api import generate_flashcards, export_flashcards_to_json, export_to_anki_format
import re

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
        print("Warning: GEMINI_API_KEY not found in environment variables")

def summarize_text(
    text: str, 
    max_tokens: int = 260,  # Just an example
    temperature: float = 0.5,  # Match these with summarize_api.py
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
        model = genai.GenerativeModel("gemini-2.0-flash")  # Must match the endpoint
        
        # Generate the summary
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
        )
        
        # Extract and return the summary
        summary = response.text.strip()
        
        # Fix: Insert a blank line before each dash
        # Warning: This is a naive approach, it will insert newlines before *all* dashes.
        summary = re.sub(r'(^|\n)-', r'\1\n-', summary)
        
        return summary
    
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
        
        # Ask what learning tools to generate
        while True:
            print("\nWhat learning tools would you like to generate?")
            print("1. Generate quiz questions")
            print("2. Generate flashcards")
            print("3. Continue without generating learning tools")
            
            tool_choice = input("Enter your choice (1-3): ").strip()
            
            if tool_choice == "1":
                # Generate quiz questions
                print("\nGenerating quiz questions based on the summary...")
                
                # Ask for number of questions
                num_questions = 5
                try:
                    num_input = input("How many quiz questions to generate? (default: 5): ").strip()
                    if num_input:
                        num_questions = int(num_input)
                except ValueError:
                    print("Invalid input. Using default of 5 questions.")
                
                # Generate quiz questions
                questions = generate_quiz_questions(summary, num_questions)
                
                if not questions:
                    print("Failed to generate quiz questions.")
                    break
                
                print(f"Successfully generated {len(questions)} questions.")
                
                # Ask what to do with the quiz
                while True:
                    print("\nWhat would you like to do with the quiz?")
                    print("1. Take the quiz in terminal")
                    print("2. Export questions to JSON file")
                    print("3. Skip quiz")
                    
                    quiz_choice = input("Enter your choice (1-3): ").strip()
                    
                    if quiz_choice == "1":
                        run_quiz_in_terminal(questions)
                        break
                    elif quiz_choice == "2":
                        filename = input("Enter filename (default: quiz_questions.json): ").strip()
                        if not filename:
                            filename = "quiz_questions.json"
                        export_quiz_to_json(questions, filename)
                        break
                    elif quiz_choice == "3":
                        print("Skipping quiz.")
                        break
                    else:
                        print("Invalid choice. Please enter 1, 2, or 3.")
                
                break
                
            elif tool_choice == "2":
                # Generate flashcards
                print("\nGenerating flashcards based on the summary...")
                
                # Ask for number of flashcards
                num_cards = 10
                try:
                    num_input = input("How many flashcards to generate? (default: 10): ").strip()
                    if num_input:
                        num_cards = int(num_input)
                except ValueError:
                    print("Invalid input. Using default of 10 flashcards.")
                
                # Generate flashcards
                flashcards = generate_flashcards(summary, num_cards)
                
                if not flashcards:
                    print("Failed to generate flashcards.")
                    break
                
                print(f"Successfully generated {len(flashcards)} flashcards.")
                
                # Ask what to do with the flashcards
                while True:
                    print("\nWhat would you like to do with the flashcards?")
                    print("1. Study flashcards in terminal")
                    print("2. Export flashcards to JSON file")
                    print("3. Export flashcards in Anki-compatible format")
                    print("4. Skip flashcards")
                    
                    fc_choice = input("Enter your choice (1-4): ").strip()
                    
                    if fc_choice == "1":
                        study_flashcards_in_terminal(flashcards)
                        break
                    elif fc_choice == "2":
                        filename = input("Enter filename (default: flashcards.json): ").strip()
                        if not filename:
                            filename = "flashcards.json"
                        export_flashcards_to_json(flashcards, filename)
                        break
                    elif fc_choice == "3":
                        filename = input("Enter filename (default: anki_flashcards.txt): ").strip()
                        if not filename:
                            filename = "anki_flashcards.txt"
                        export_to_anki_format(flashcards, filename)
                        break
                    elif fc_choice == "4":
                        print("Skipping flashcards.")
                        break
                    else:
                        print("Invalid choice. Please enter 1, 2, 3, or 4.")
                
                break
                
            elif tool_choice == "3":
                print("Continuing without generating learning tools.")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
        
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