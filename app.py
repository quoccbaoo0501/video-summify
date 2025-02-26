from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import sys
import traceback
from dotenv import load_dotenv
import google.generativeai as genai
import logging
from youtube_transcript_api import YouTubeTranscriptApi

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
CORS(app, resources={r"/*": {
    "origins": "*", 
    "allow_headers": ["Content-Type", "Authorization", "Accept"], 
    "expose_headers": ["Content-Type", "X-Requested-With"],
    "methods": ["GET", "POST", "OPTIONS"]
}})

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
        
        try:
            # Get video ID
            video_id = get_video_id(video_url)
            print(f"Extracted video ID: {video_id}")
            
            # Get transcript with more detailed error handling
            try:
                print(f"Using youtube_transcript_api version: {YouTubeTranscriptApi.__version__}")
                # Try direct API call to see if it's an environment issue
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                available_langs = [t.language_code for t in transcript_list._manually_created_transcripts.values()]
                available_langs += [t.language_code for t in transcript_list._generated_transcripts.values()]
                print(f"Available transcript languages: {available_langs}")
                
                # Now try to get the transcript as normal
                transcript = get_transcript(video_id, language)
                print(f"Got transcript, length: {len(transcript)} characters")
            except Exception as transcript_error:
                error_msg = str(transcript_error)
                print(f"Detailed transcript error: {error_msg}")
                # Provide a user-friendly error message for missing transcripts
                if "Could not retrieve a transcript" in error_msg:
                    return jsonify({
                        "error": "This video doesn't have subtitles/transcripts available",
                        "details": "To summarize a video, it must have subtitles or closed captions enabled.",
                        "suggestion": "Try a different video that has subtitles available.",
                        "example_videos": [
                            "https://www.youtube.com/watch?v=LXb3EKWsInQ",  # NASA Mars 2020 Perseverance Rover Mission
                            "https://www.youtube.com/watch?v=W0LHTWG-UmQ",  # Google I/O keynote (usually has good transcripts)
                            "https://www.youtube.com/watch?v=fKopy74weus"    # TED Talk with good captioning
                        ]
                    }), 400
                else:
                    return jsonify({"error": f"Failed to get transcript: {error_msg}"}), 500
        except Exception as video_id_error:
            error_msg = str(video_id_error)
            print(f"Error getting video ID: {error_msg}")
            return jsonify({"error": f"Failed to get video ID: {error_msg}"}), 500
        
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

@app.route('/summarize', methods=['OPTIONS'])
def handle_options():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,Accept")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    return response

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

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Simple endpoint to test API connectivity."""
    return jsonify({
        "status": "ok",
        "message": "API test endpoint is working"
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