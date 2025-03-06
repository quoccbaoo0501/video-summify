import os
import sys
import json
import google.generativeai as genai
from typing import List, Dict, Any

class Flashcard:
    def __init__(self, front: str, back: str):
        self.front = front
        self.back = back

    def to_dict(self) -> Dict[str, str]:
        return {
            "front": self.front,
            "back": self.back
        }

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
        raise ValueError("GOOGLE_API_KEY not found in environment variables")

def generate_flashcards(summary: str, num_cards: int = 10) -> List[Dict[str, str]]:
    """
    Generate flashcards based on a summary using Gemini API.
    
    Args:
        summary: The text summary
        num_cards: Number of flashcards to generate (default: 10)
        
    Returns:
        A list of flashcard dictionaries
    """
    # Create the prompt
    prompt = f"""
You are a study aid creator that makes effective flashcards to help users remember key concepts.
Based on the following summary, create {num_cards} flashcards.

For each flashcard:
1. The front should contain a specific question, concept name, or term from the summary
2. The back should contain a concise but comprehensive answer or explanation
3. Focus on the most important concepts, facts, definitions, and relationships
4. Each card should cover a single, distinct concept
5. The cards should help with active recall and spaced repetition

Return the flashcards in the following JSON format:
[
  {{
    "front": "What is [concept]?",
    "back": "Clear explanation of the concept"
  }},
  {{
    "front": "Define [term]:",
    "back": "Definition of the term"
  }},
  // more flashcards...
]

SUMMARY:
{summary}

Output only the JSON array without any additional text or explanations.
"""

    try:
        # Configure the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate the flashcards
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.2,  # Lower temperature for more focused cards
            )
        )
        
        # Extract the JSON from the response
        response_text = response.text.strip()
        
        # Find the JSON array in the response
        json_start = response_text.find('[')
        json_end = response_text.rfind(']') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            cards_data = json.loads(json_str)
            
            # Validate and filter flashcards
            flashcards = []
            for i, card_data in enumerate(cards_data):
                if len(flashcards) >= num_cards:
                    break
                    
                if "front" in card_data and "back" in card_data:
                    flashcards.append(card_data)
            
            return flashcards
        else:
            print("Error: Could not extract JSON from response")
            return []
    
    except Exception as e:
        print(f"Error generating flashcards: {str(e)}")
        return []

def process_api_request(input_file: str, output_file: str) -> None:
    """
    Process an API request from input file and write result to output file.
    
    Args:
        input_file: Path to JSON file with input data
        output_file: Path to write output JSON data
    """
    try:
        # Read input data
        with open(input_file, 'r') as f:
            input_data = json.load(f)
        
        summary = input_data.get('summary')
        num_cards = input_data.get('num_cards', 10)
        
        if not summary:
            raise ValueError("Summary is required")
        
        # Generate flashcards
        flashcards = generate_flashcards(summary, num_cards)
        
        # Prepare output data
        output_data = {
            'flashcards': flashcards
        }
        
        # Write output data
        with open(output_file, 'w') as f:
            json.dump(output_data, f)
            
    except Exception as e:
        # Write error to output file
        with open(output_file, 'w') as f:
            json.dump({
                'error': str(e)
            }, f)
        raise

def study_flashcards_in_terminal(flashcards):
    """
    Example placeholder or real implementation of
    the "study_flashcards_in_terminal" function.
    """
    for i, card in enumerate(flashcards, start=1):
        front = card.get("front", "")
        back = card.get("back", "")
        print(f"Card {i}: Front: {front}")
        input("Press Enter to view the back...")
        print(f"Back: {back}")
        input("Press Enter to continue to the next card...")

def export_flashcards_to_json(flashcards, filename: str) -> None:
    """
    Export flashcards to a JSON file.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"flashcards": flashcards}, f, ensure_ascii=False, indent=2)

def export_to_anki_format(flashcards, filename: str) -> None:
    """
    Export flashcards in a simple Anki-compatible text format.
    Each line contains 'front\tback'.
    """
    with open(filename, "w", encoding="utf-8") as f:
        for card in flashcards:
            front = card.get("front", "").replace("\t", "    ")
            back = card.get("back", "").replace("\t", "    ")
            f.write(f"{front}\t{back}\n")

def main():
    """
    Main function to handle API requests.
    """
    if len(sys.argv) != 3:
        print("Usage: python flashcards_api.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Set up API keys
    setup_api_keys()
    
    # Process the request
    process_api_request(input_file, output_file)

if __name__ == "__main__":
    main() 