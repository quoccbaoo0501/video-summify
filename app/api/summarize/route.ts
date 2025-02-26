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

    // Call your Render API endpoint with the correct URL
    const baseUrl = process.env.PYTHON_API_URL || 'https://video-summify.onrender.com';
    // Don't append /summarize if it's already in the baseUrl
    const apiUrl = baseUrl.includes('/summarize') ? baseUrl : `${baseUrl}/summarize`;
    console.log(`Calling API at: ${apiUrl}`);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000); // 60 second timeout

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ videoUrl, language }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId); // Clear the timeout if the request completes

    // Check if response is JSON
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      const responseText = await response.text();
      console.error('Non-JSON response:', responseText);
      return NextResponse.json(
        { 
          error: 'API returned non-JSON response. The service might be down or misconfigured.',
          details: responseText.substring(0, 200) + (responseText.length > 200 ? '...' : '')
        },
        { status: 500 }
      );
    }

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
    clearTimeout(timeoutId); // Clear the timeout on error
    console.error('API error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
} 