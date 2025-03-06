# Video Summify

A comprehensive video summarization and learning tool that helps users understand and retain information from YouTube videos.

## Features

- **Video Summarization**: Generate concise summaries of YouTube videos using Google's Gemini API
- **Interactive Quizzes**: Test your understanding with AI-generated multiple-choice questions
- **Study Flashcards**: Reinforce your learning with automatically generated flashcards
- **Modern UI**: Clean, responsive interface built with Next.js and Tailwind CSS

## Prerequisites

- Node.js 18 or higher
- Python 3.8 or higher
- Google Gemini API key

### Installing Python and Node.js
If you don't have Python or Node.js installed:

- **Python**: Visit [python.org/downloads](https://www.python.org/downloads/) or use a package manager (e.g. Homebrew on macOS or apt-get on Linux) to install Python 3.8 or higher.
- **Node.js**: Go to [nodejs.org](https://nodejs.org/) and download the LTS release (or install via a package manager).

## Quick Start

If you just want to get started quickly, follow these steps:

```bash
git clone https://github.com/quoccbaoo0501/video-summify.git
cd video-summify
npm install
pip install google-generativeai youtube-transcript-api
npm run dev
```

You can visit [http://localhost:3000](http://localhost:3000) to see the application. If you get stuck, see the full installation instructions below.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/quoccbaoo0501/video-summify.git
cd video-summify
```

### 2. Install frontend dependencies

```bash
npm install
```

### 3. Install Python dependencies

```bash
pip install google-generativeai youtube-transcript-api
```

### 4. Set up environment variables

Create or edit the `.env` file in the root directory:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

## Running the Application

### Development Mode

Start the Next.js development server:

```bash
npm run dev
```

This will start the application on [http://localhost:3000](http://localhost:3000).

## How It Works

### Backend Architecture

1. **API Routes**:
   - `/api/summarize` - Processes YouTube videos and generates summaries
   - `/api/generate-quiz` - Creates quiz questions from summaries
   - `/api/generate-flashcards` - Produces study flashcards from summaries

2. **Python API Handlers**:
   - `summarize_api.py` - Handles video transcript extraction and summarization
   - `quiz_api.py` - Generates quiz questions using Gemini API
   - `flashcards_api.py` - Creates flashcards using Gemini API

### Frontend Components

1. **Video Summarizer** - Main component for inputting YouTube URLs
2. **Video Summary** - Displays the generated summary
3. **Quiz** - Interactive quiz component
4. **Flashcards** - Flashcard study component

## Command-Line Usage

You can also use the Python scripts directly from the command line:

### Generate a Summary

```bash
python summerize.py
```

### Generate Quiz Questions

```bash
python quiz.py
```

### Generate Flashcards

```bash
python flashcards.py
```

## Technologies Used

- **Frontend**: Next.js, React, Tailwind CSS, shadcn/ui
- **Backend**: Next.js API Routes, Python
- **AI**: Google Gemini API for natural language processing
- **Data Processing**: youtube-transcript-api for transcript extraction

## License

[MIT](LICENSE) 