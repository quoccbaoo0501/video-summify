from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import sys
import traceback
from dotenv import load_dotenv
import google.generativeai as genai
import logging

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing functions with correct paths
from src.transcript import get_video_id, get_transcript
from src.summerize import setup_api_keys, summarize_text

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.environ.get("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    print(f"Configured Gemini API with key: {api_key[:5]}...")
else:
    print("WARNING: GOOGLE_API_KEY not found in environment variables")

app = Flask(__name__)
# Configure CORS with the Flask-CORS extension more explicitly
CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}})

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def health_check():
    try:
        return jsonify({"status": "ok", "message": "API is running"})
    except Exception as e:
        print(f"Error in health check: {str(e)}")
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        # Debug information
        print("Received request to /summarize endpoint")
        
        # Ensure we're getting JSON data
        if not request.is_json:
            print("Request does not contain JSON data")
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json()
        print(f"Received data: {data}")
        
        if not data or 'videoUrl' not in data:
            return jsonify({"error": "Video URL is required"}), 400
        
        video_url = data['videoUrl']
        language = data.get('language', 'en')
        
        print(f"Processing video URL: {video_url}, language: {language}")
        
        # Set up API keys
        setup_api_keys()
        
        # Get video ID
        video_id = get_video_id(video_url)
        print(f"Extracted video ID: {video_id}")
        
        # Get transcript
        transcript = get_transcript(video_id, language)
        print(f"Got transcript, length: {len(transcript)} characters")
        
        # Add specific timeout error handling
        try:
            # Generate summary with explicit timeout handling
            print("Generating summary...")
            summary = summarize_text(transcript)
            print(f"Summary generated, length: {len(summary)} characters")
        except Exception as summary_error:
            print(f"Error during summarization: {str(summary_error)}")
            return jsonify({"error": f"Summarization failed: {str(summary_error)}"}), 500
        
        # Ensure the response is properly formatted JSON
        response = make_response(jsonify({"summary": summary}))
        response.headers['Content-Type'] = 'application/json'
        return response
        
    except Exception as e:
        print(f"ERROR in /summarize endpoint: {str(e)}")
        traceback.print_exc()  # Print the full stack trace for debugging
        return jsonify({"error": str(e)}), 500

@app.route('/ping', methods=['GET'])
def ping():
    try:
        # Basic response - no dependencies
        return jsonify({"message": "pong"})
    except Exception as e:
        logging.error(f"Error in ping endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/debug', methods=['GET'])
def debug_info():
    """Return debug information about the environment."""
    env_info = {k: v for k, v in os.environ.items() if not k.startswith('_')}
    # Remove sensitive information
    if 'GOOGLE_API_KEY' in env_info:
        env_info['GOOGLE_API_KEY'] = f"{env_info['GOOGLE_API_KEY'][:5]}...redacted"
        
    return jsonify({
        "python_version": sys.version,
        "environment": env_info,
        "flask_version": Flask.__version__,
        "debug_mode": app.debug,
        "api_configured": bool(os.environ.get("GOOGLE_API_KEY"))
    })

# Make sure the server always returns a response
@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Unhandled exception: {str(e)}")
    traceback.print_exc()
    return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True) 