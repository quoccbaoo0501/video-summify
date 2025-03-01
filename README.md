# Video Summify

A web application that summarizes YouTube videos using AI.

## Features

- Extract transcripts from YouTube videos
- Generate concise summaries using Google's Gemini AI
- Support for multiple languages (English and Vietnamese)
- Dark/light mode toggle

## Tech Stack

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS (deployed on Vercel)
- **Backend**: FastAPI Python API (deployed on [Render/Railway/Fly.io])
- **AI**: Google Gemini 2.0 Flash

## Architecture

This application uses a decoupled architecture:
- Frontend: Next.js application hosted on Vercel
- Backend: FastAPI Python service hosted on [your hosting service]

## Setup for Development

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   PYTHON_API_URL=http://localhost:8080/summarize (for local development)
   ```
4. Run the development servers:
   ```
   npm run dev     # Frontend
   python wsgi.py  # Backend API
   ```

## Usage

1. Enter a YouTube URL in the input field
2. Select your preferred language
3. Click "Summarize" to generate a summary of the video

## License

MIT
