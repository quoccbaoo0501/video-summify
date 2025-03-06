import os
import sys
import json
import google.generativeai as genai
from typing import List, Dict, Any

class QuizQuestion:
    def __init__(self, question: str, options: List[str], correct_answer: int):
        self.question = question
        self.options = options
        self.correct_answer = correct_answer

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "options": self.options,
            "correctAnswer": self.correct_answer
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
    if os.environ.get("GEMINI_API_KEY"):
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    else:
        raise ValueError("GEMINI_API_KEY not found in environment variables")

def generate_quiz_questions(summary: str, num_questions: int = 5) -> List[Dict[str, Any]]:
    """
    Generate a list of quiz questions from the provided summary.
    """

    # Define a prompt instructing the model to return a valid JSON array of quiz questions.
    prompt = f"""
Create a JSON array of {num_questions} quiz questions about the following summary:
\"\"\"{summary}\"\"\"
Each question object should look like:
{{
  "question": "The question text",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correctAnswer": 0  # integer index of the correct option
}}
Output only valid JSON:
[
  {{ "question": "...", "options": ["...","...","...","..."], "correctAnswer": 0 }},
  ...
]
"""

    try:
        # Configure the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Generate the questions
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
            )
        )
        
        response_text = response.text.strip()
        # Debug: Print out the raw text from the model (remove later if desired)
        print("Quiz response text:\n", response_text)
        
        json_start = response_text.find('[')
        json_end = response_text.rfind(']') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            questions_data = json.loads(json_str)
            
            questions = []
            for i, q_data in enumerate(questions_data):
                if len(questions) >= num_questions:
                    break
                    
                # Validate the question format
                if (
                    "question" in q_data and 
                    "options" in q_data and 
                    "correctAnswer" in q_data and
                    isinstance(q_data["options"], list) and
                    len(q_data["options"]) == 4 and
                    isinstance(q_data["correctAnswer"], int) and
                    0 <= q_data["correctAnswer"] < 4
                ):
                    questions.append(q_data)
            
            return questions
        else:
            print("Error: Could not extract JSON from response")
            return []
    
    except Exception as e:
        print(f"Error generating quiz questions: {str(e)}")
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
        num_questions = input_data.get('num_questions', 5)
        
        if not summary:
            raise ValueError("Summary is required")
        
        # Generate quiz questions
        questions = generate_quiz_questions(summary, num_questions)
        
        # Prepare output data
        output_data = {
            'questions': questions
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

def main():
    """
    Main function to handle API requests.
    """
    if len(sys.argv) != 3:
        print("Usage: python quiz_api.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # Set up API keys
    setup_api_keys()
    
    # Process the request
    process_api_request(input_file, output_file)

if __name__ == "__main__":
    main() 