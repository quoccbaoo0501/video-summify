from flask import Flask, request, jsonify
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing functions with correct paths
from src.transcript import get_video_id, get_transcript
from src.summerize import setup_api_keys, summarize_text

# Load environment variables
load_dotenv()

# Configure Gemini API
if os.environ.get("GOOGLE_API_KEY"):
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    print(f"Configured Gemini API with key: {os.environ.get('GOOGLE_API_KEY')[:5]}...")
else:
    print("Warning: GOOGLE_API_KEY not found in environment variables")

app = Flask(__name__)

# Try to enable CORS if available
try:
    from flask_cors import CORS
    CORS(app)  # Enable CORS for all routes
    print("CORS enabled successfully")
except ImportError:
    print("Warning: flask_cors not installed, CORS headers will be added manually")
    # We'll handle CORS headers manually

@app.route('/summarize', methods=['POST'])
def summarize():
    """Handle POST requests to /summarize"""
    try:
        print("Received POST request to /summarize")
        data = request.json
        print(f"Request data: {data}")
        
        if not data or 'videoUrl' not in data:
            print("Error: Missing videoUrl in request")
            return jsonify({"error": "Video URL is required"}), 400
        
        video_url = data['videoUrl']
        language = data.get('language', 'en')
        print(f"Processing video: {video_url}, language: {language}")
        
        # Get video ID
        video_id = get_video_id(video_url)
        print(f"Video ID: {video_id}")
        
        # Get transcript
        print("Getting transcript...")
        transcript = get_transcript(video_id, language)
        print(f"Transcript length: {len(transcript)} characters")
        
        # Generate summary
        print("Generating summary...")
        summary = summarize_text(transcript)
        print(f"Summary generated: {len(summary)} characters")
        
        print("Returning response")
        return jsonify({"summary": summary})
        
    except Exception as e:
        print(f"Error in /summarize: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/summarize', methods=['OPTIONS'])
def handle_options():
    return '', 204

# Add CORS headers
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/', methods=['GET'])
def health_check():
    """Handle GET requests to root endpoint"""
    print("Health check endpoint called")
    return jsonify({"status": "healthy", "message": "Video Summify API is running"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port) 