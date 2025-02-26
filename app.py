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
else:
    print("Warning: GOOGLE_API_KEY not found in environment variables")

app = Flask(__name__)

@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.json
        
        if not data or 'videoUrl' not in data:
            return jsonify({"error": "Video URL is required"}), 400
        
        video_url = data['videoUrl']
        language = data.get('language', 'en')
        
        # Get video ID
        video_id = get_video_id(video_url)
        
        # Get transcript
        transcript = get_transcript(video_id, language)
        
        # Generate summary
        summary = summarize_text(transcript)
        
        return jsonify({"summary": summary})
        
    except Exception as e:
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
    return jsonify({"status": "healthy", "message": "Video Summify API is running"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port) 