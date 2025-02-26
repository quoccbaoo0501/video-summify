from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
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

# Create FastAPI app
app = FastAPI(title="Video Summify API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define request models
class SummarizeRequest(BaseModel):
    videoUrl: str
    language: str = "en"

@app.get("/")
async def health_check():
    """API health check endpoint"""
    try:
        return {"status": "ok", "message": "API is running"}
    except Exception as e:
        print(f"Error in health check: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )

@app.post("/summarize")
async def summarize(request: SummarizeRequest):
    """Summarize a YouTube video"""
    try:
        # Debug information
        print("Received request to /summarize endpoint")
        print(f"Received data: {request}")
        
        video_url = request.videoUrl
        language = request.language
        
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

            except Exception as transcript_error:
                error_msg = str(transcript_error)
                print(f"Detailed transcript error: {error_msg}")
                # Provide a user-friendly error message for missing transcripts
                if "Could not retrieve a transcript" in error_msg:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "error": "This video doesn't have subtitles/transcripts available",
                            "details": "To summarize a video, it must have subtitles or closed captions enabled.",
                            "suggestion": "Try a different video that has subtitles available.",
                            "example_videos": [
                                "https://www.youtube.com/watch?v=LXb3EKWsInQ",  # NASA Mars 2020 Perseverance Rover Mission
                                "https://www.youtube.com/watch?v=W0LHTWG-UmQ",  # Google I/O keynote (usually has good transcripts)
                                "https://www.youtube.com/watch?v=fKopy74weus"    # TED Talk with good captioning
                            ]
                        }
                    )
                else:
                    return JSONResponse(
                        status_code=500,
                        content={"error": f"Failed to get transcript: {error_msg}"}
                    )
                    
        except Exception as video_id_error:
            error_msg = str(video_id_error)
            print(f"Error getting video ID: {error_msg}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to get video ID: {error_msg}"}
            )
        
        # Generate summary
        try:
            print("Generating summary...")
            summary = summarize_text(transcript)
            print(f"Summary generated, length: {len(summary)} characters")
        except Exception as summary_error:
            print(f"Error during summarization: {str(summary_error)}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Summarization failed: {str(summary_error)}"}
            )
        
        # Return the summary
        return {"summary": summary}
        
    except Exception as e:
        print(f"ERROR in /summarize endpoint: {str(e)}")
        traceback.print_exc()  # Print the full stack trace for debugging
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/ping")
async def ping():
    """Simple ping endpoint to check API availability"""
    try:
        return {"message": "pong"}
    except Exception as e:
        logging.error(f"Error in ping endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/debug")
async def debug_info():
    """Return debug information about the environment"""
    # Define a completely new dictionary with only selected information
    filtered_environment = {}
    
    # Manually add only specific, safe environment variables
    if os.environ.get("GOOGLE_API_KEY"):
        filtered_environment["GOOGLE_API_KEY"] = f"{os.environ['GOOGLE_API_KEY'][:5]}...redacted"
    
    if os.environ.get("PORT"):
        filtered_environment["PORT"] = os.environ.get("PORT")
        
    if os.environ.get("PYTHON_VERSION"):
        filtered_environment["PYTHON_VERSION"] = os.environ.get("PYTHON_VERSION")
        
    if os.environ.get("NODE_ENV"):
        filtered_environment["NODE_ENV"] = os.environ.get("NODE_ENV")
        
    if os.environ.get("RENDER_SERVICE_NAME"):
        filtered_environment["RENDER_SERVICE_NAME"] = os.environ.get("RENDER_SERVICE_NAME")
        
    if os.environ.get("RENDER_EXTERNAL_HOSTNAME"):
        filtered_environment["RENDER_EXTERNAL_HOSTNAME"] = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    
    # Return a new dictionary with only the necessary information
    return {
        "python_version": sys.version,
        "app_info": {
            "fastapi_version": "0.104.1",
            "debug_mode": True,
            "api_configured": bool(os.environ.get("GOOGLE_API_KEY"))
        },
        "safe_environment": filtered_environment
    }

@app.get("/test")
async def test_endpoint():
    """Simple endpoint to test API connectivity"""
    return {
        "status": "ok",
        "message": "API test endpoint is working"
    }

# Replace this Flask-specific code with this FastAPI-compatible exception handler:
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Unhandled exception: {str(exc)}")
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "details": str(exc)}
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting FastAPI app on port {port}")
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True) 