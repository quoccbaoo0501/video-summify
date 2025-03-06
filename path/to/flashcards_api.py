import sys
import json
from typing import List, Dict
import genai

def generate_flashcards(summary: str, num_cards: int = 10) -> List[Dict[str, str]]:
    """
    Generate a list of flashcards (front/back) from the provided summary.
    """

    # Define a prompt instructing the model to return a JSON list of objects with 'front' and 'back'.
    prompt = f"""
    Create a JSON array of {num_cards} flashcards based on the following summary:
    \"\"\"{summary}\"\"\"
    Each object must have a 'front' and 'back'. Output only valid JSON:
    [
      {{ "front": "...", "back": "..." }},
      ...
    ]
    """

    # existing code...
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

        # Parse the model response text instead of the response object
        flashcards = json.loads(response.text.strip())
        return flashcards

    except Exception as e:
        # Remove or comment out references to output_file if not passed in
        # error_data = {"error": f"Failure in generate_flashcards: {str(e)}"}
        # with open(output_file, 'w') as f:
        #     json.dump(error_data, f)
        raise

def main(input_file, output_file):
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        summary = data.get('summary', '')
        num_cards = data.get('num_cards', 10)

        # Generate flashcards here...
        flashcards = generate_flashcards(summary, num_cards)

        with open(output_file, 'w') as f:
            json.dump({"flashcards": flashcards}, f)

    except Exception as e:
        error_data = {"error": f"Failure in flashcards_api: {str(e)}"}
        with open(output_file, 'w') as f:
            json.dump(error_data, f)
        raise

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python flashcards_api.py <input_json> <output_json>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2]) 