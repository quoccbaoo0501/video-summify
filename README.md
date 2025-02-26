# Video Summify

A web application that summarizes YouTube videos using AI.

## Features

- Extract transcripts from YouTube videos
- Generate concise summaries using Google's Gemini AI
- Support for multiple languages (English and Vietnamese)
- Dark/light mode toggle

## Tech Stack

- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Backend**: Next.js API routes, Python
- **AI**: Google Gemini 2.0 Flash

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   pip install youtube_transcript_api google-generativeai
   ```
3. Create a `.env` file with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```
4. Run the development server:
   ```
   npm run dev
   ```

## Usage

1. Enter a YouTube URL in the input field
2. Select your preferred language
3. Click "Summarize" to generate a summary of the video

## License

MIT
