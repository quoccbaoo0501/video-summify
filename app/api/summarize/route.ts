import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  // Create this variable outside the try block so it's accessible in catch
  let timeoutId: NodeJS.Timeout | undefined;
  
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
    // After your baseUrl setup, add this
    const useMockEndpoint = false; // Use the real API

    // Modify your API URL
    const apiUrl = baseUrl.includes('/summarize') ? baseUrl : `${baseUrl}/summarize`;
    console.log(`Calling API at: ${apiUrl}`);
    
    const controller = new AbortController();
    timeoutId = setTimeout(() => controller.abort(), 120000); // 120 second timeout

    // First test basic connectivity with ping
    const pingUrl = baseUrl.replace('/summarize', '/ping');
    console.log(`Testing API connectivity at: ${pingUrl}`);
    const pingResponse = await fetch(pingUrl, { 
      method: 'GET',
      signal: controller.signal,
      cache: 'no-store'
    }).catch(err => {
      console.log(`Ping failed with error: ${err.message}`);
      return { ok: false, text: async () => err.message };
    });
    
    if (!pingResponse.ok) {
      console.error('API ping failed, but continuing with main request');
    } else {
      console.log('API ping successful');
      // Longer warm-up delay for free tier
      await new Promise(resolve => setTimeout(resolve, 5000));
    }

    console.log(`Starting API request at ${new Date().toISOString()}`);

    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
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
      
      // Check for transcript-specific errors
      if (data.error && data.error.includes("doesn't have subtitles/transcripts available")) {
        return NextResponse.json(
          { 
            error: data.error,
            details: data.details || "The video must have subtitles available to generate a summary.",
            suggestion: data.suggestion || "Please try a different video.",
          },
          { status: response.status }
        );
      }
      
      return NextResponse.json(
        { error: data.error || 'Failed to process video' },
        { status: response.status }
      );
    }
    
    return NextResponse.json({ summary: data.summary });
  } catch (error) {
    console.error('API error with full details:', error);
    // Now timeoutId is accessible here
    if (timeoutId) clearTimeout(timeoutId);
    
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
} 