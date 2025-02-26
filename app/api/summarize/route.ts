import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

const execPromise = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const { videoUrl, language = 'en' } = await request.json();
    
    if (!videoUrl) {
      return NextResponse.json(
        { error: 'Video URL is required' },
        { status: 400 }
      );
    }

    // Path to Python script
    const scriptPath = path.join(process.cwd(), 'src', 'summarize_api.py');
    
    // Execute Python script with parameters and set encoding to UTF-8
    const { stdout, stderr } = await execPromise(
      `python "${scriptPath}" "${videoUrl}" "${language}"`,
      { env: { ...process.env, PYTHONIOENCODING: 'utf-8' } }
    );

    if (stderr && !stderr.includes('WARNING:') && !stderr.includes('grpc_wait_for_shutdown_with_timeout')) {
      console.error('Python script error:', stderr);
      return NextResponse.json(
        { error: 'Failed to process video' },
        { status: 500 }
      );
    }

    // Check if output is JSON error
    if (stdout.trim().startsWith('{') && stdout.includes('"error"')) {
      try {
        const errorData = JSON.parse(stdout.trim());
        return NextResponse.json(
          { error: errorData.error },
          { status: 500 }
        );
      } catch (e) {
        // If parsing fails, continue with normal processing
      }
    }

    // Parse the output from Python script
    const summary = stdout.trim();
    
    return NextResponse.json({ summary });
  } catch (error) {
    console.error('API error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
} 