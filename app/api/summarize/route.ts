import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { videoUrl, language = 'en' } = await request.json();
    
    if (!videoUrl) {
      return NextResponse.json(
        { error: 'Video URL is required' },
        { status: 400 }
      );
    }

    // Call your Render API endpoint
    const apiUrl = process.env.PYTHON_API_URL || 'https://video-summify-api.onrender.com/summarize';
    console.log(`Calling API at: ${apiUrl}`);
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.API_SECRET_KEY || ''}`
      },
      body: JSON.stringify({ videoUrl, language }),
    });

    const data = await response.json();
    
    if (!response.ok) {
      console.error('API error response:', data);
      return NextResponse.json(
        { error: data.error || 'Failed to process video' },
        { status: response.status }
      );
    }
    
    return NextResponse.json({ summary: data.summary });
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
} 