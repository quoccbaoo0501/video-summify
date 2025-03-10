import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';
import os from 'os';

const execPromise = promisify(exec);

// Helper function to determine if we're running in a Docker container
const isRunningInDocker = () => {
  try {
    return fs.existsSync('/.dockerenv');
  } catch {
    return false;
  }
};

// Helper function to determine the Python command to use
const getPythonCommand = () => {
  // First check if there's an environment variable set
  if (process.env.PYTHON_PATH) {
    return process.env.PYTHON_PATH;
  }
  
  // Check the platform
  const platform = os.platform();
  if (platform === 'win32') {
    // On Windows, try 'python' first
    return 'python';
  }
  
  // For other platforms (Linux, macOS), default to python3
  return 'python3';
};

export async function POST(request: NextRequest) {
  try {
    const { url, language = 'en' } = await request.json();
    
    if (!url) {
      return NextResponse.json(
        { error: 'YouTube URL is required' },
        { status: 400 }
      );
    }

    // Determine base directory based on environment
    const baseDir = isRunningInDocker() ? '/app' : process.cwd();

    // Create paths for input and output files
    const inputFile = path.join(baseDir, 'temp_input.json');
    const outputFile = path.join(baseDir, 'temp_output.json');
    
    // Prepare input data for the Python script
    const inputData = {
      url,
      language
    };
    
    // Write input data to file
    fs.writeFileSync(inputFile, JSON.stringify(inputData));
    
    // Get the appropriate Python command for this platform
    const pythonCommand = getPythonCommand();
    console.log(`Using Python command: ${pythonCommand}`);
    
    try {
      // Attempt to run the Python script
      const scriptPath = path.join(baseDir, 'summarize_api.py');
      const command = `${pythonCommand} "${scriptPath}" "${inputFile}" "${outputFile}"`;
      console.log('Running command:', command);
      const { stdout, stderr } = await execPromise(command);
      console.log('summarize_api.py STDOUT:', stdout);
      console.error('summarize_api.py STDERR:', stderr);
      
      // Check if the output includes transcript not available error
      if (stdout && stdout.includes('Subtitles are disabled for this video')) {
        return NextResponse.json(
          { 
            error: 'This video does not have subtitles/captions available. Please try a different video that has captions enabled.',
            details: 'YouTube requires videos to have captions/subtitles for summarization to work.'
          },
          { status: 422 }
        );
      }
      
      if (stderr && !stderr.includes('WARNING')) {
        console.error('Python script error:', stderr);
        return NextResponse.json(
          { error: 'Failed to summarize video' },
          { status: 500 }
        );
      }
    } catch (execError) {
      // Handle cases where Python isn't found or the script crashed
      console.error('Failed to run Python script:', execError);
      
      // Check if the error is about missing transcripts
      const errorOutput = (execError as any).stdout || '';
      if (errorOutput.includes('Subtitles are disabled for this video')) {
        return NextResponse.json(
          { 
            error: 'This video does not have subtitles/captions available. Please try a different video that has captions enabled.',
            details: 'YouTube requires videos to have captions/subtitles for summarization to work.'
          },
          { status: 422 }
        );
      }
      
      return NextResponse.json(
        { error: `Unable to run summarize script: ${execError}` },
        { status: 500 }
      );
    }
    
    // Read the output file
    if (fs.existsSync(outputFile)) {
      const readData = fs.readFileSync(outputFile, 'utf-8');
      const jsonData = JSON.parse(readData);

      // 1. Collapse consecutive newlines down to two:
      jsonData.summary = jsonData.summary.replace(/\n{2,}/g, '\n\n');

      // 2. Then convert the remaining newlines to a single <br/> each:
      jsonData.summary = jsonData.summary.replace(/\n/g, '<br/>');

      // Clean up temporary files
      try {
        fs.unlinkSync(inputFile);
        fs.unlinkSync(outputFile);
      } catch (e) {
        console.error('Error cleaning up temporary files:', e);
        // Continue execution even if cleanup fails
      }
      
      return NextResponse.json(jsonData, { status: 200 });
    } else {
      return NextResponse.json(
        { error: 'Failed to generate summary output' },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Error in POST request:', error);
    return NextResponse.json(
      { error: (error as Error).message || 'Internal server error' },
      { status: 500 }
    );
  }
} 