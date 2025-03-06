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
    const { summary, numQuestions = 5 } = await request.json();
    
    if (!summary) {
      return NextResponse.json(
        { error: 'Summary is required' },
        { status: 400 }
      );
    }
    
    // Determine base directory based on environment
    const baseDir = isRunningInDocker() ? '/app' : process.cwd();
    
    // Create unique temporary files to store input and output
    const uniqueId = `${Date.now()}-${Math.floor(Math.random() * 1e7)}`;
    const inputFile = path.join(baseDir, `temp_quiz_input_${uniqueId}.json`);
    const outputFile = path.join(baseDir, `temp_quiz_output_${uniqueId}.json`);
    
    // Prepare input data for the Python script
    const inputData = {
      summary,
      num_questions: numQuestions
    };
    
    // Write input data to file
    fs.writeFileSync(inputFile, JSON.stringify(inputData));
    
    // Get the appropriate Python command for this platform
    const pythonCommand = getPythonCommand();
    console.log(`Using Python command: ${pythonCommand}`);
    
    try {
      // Attempt to run the Python script with full path resolution
      const scriptPath = path.join(baseDir, 'quiz_api.py');
      const command = `${pythonCommand} "${scriptPath}" "${inputFile}" "${outputFile}"`;
      console.log('Running command:', command);
      
      // Execute the Python script with input file path as argument
      const { stdout, stderr } = await execPromise(command);
      
      // Log script output for debugging
      console.log('Quiz script STDOUT:', stdout);
      console.error('Quiz script STDERR:', stderr);
      
      if (stderr && !stderr.includes('WARNING')) {
        console.error('Python script error:', stderr);
        return NextResponse.json(
          { error: 'Failed to generate quiz questions' },
          { status: 500 }
        );
      }
    } catch (execError) {
      console.error('Failed to run Python script:', execError);
      return NextResponse.json(
        { error: `Unable to run quiz script: ${execError}` },
        { status: 500 }
      );
    }
    
    // Read the output file
    if (fs.existsSync(outputFile)) {
      const outputData = JSON.parse(fs.readFileSync(outputFile, 'utf-8'));
      
      // Clean up temporary files
      try {
        fs.unlinkSync(inputFile);
        fs.unlinkSync(outputFile);
      } catch (e) {
        console.error('Error cleaning up temporary files:', e);
        // Continue execution even if cleanup fails
      }
      
      return NextResponse.json({
        questions: outputData.questions
      });
    } else {
      return NextResponse.json(
        { error: 'Failed to generate quiz output' },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('Error processing request:', error);
    return NextResponse.json(
      { error: (error as Error).message || 'Internal server error' },
      { status: 500 }
    );
  }
} 