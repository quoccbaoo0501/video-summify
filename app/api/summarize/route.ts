import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execPromise = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const { url, language = 'en' } = await request.json();
    
    if (!url) {
      return NextResponse.json(
        { error: 'YouTube URL is required' },
        { status: 400 }
      );
    }

    // Create a temporary file to store input and output
    const inputFile = path.join(process.cwd(), 'temp_input.json');
    const outputFile = path.join(process.cwd(), 'temp_output.json');
    
    // Prepare input data for the Python script
    const inputData = {
      url,
      language
    };
    
    // Write input data to file
    fs.writeFileSync(inputFile, JSON.stringify(inputData));
    
    // 1. Choose which Python command to run
    const pythonCommand = process.env.PYTHON_PATH || 'python3';
    try {
      // 2. Attempt to run the Python script
      //    Wrap all paths in quotes to avoid issues with spaces
      const scriptPath = path.join(process.cwd(), 'summarize_api.py');
      const command = `${pythonCommand} "${scriptPath}" "${inputFile}" "${outputFile}"`;
      console.log('Running command:', command);
      const { stdout, stderr } = await execPromise(command);
      console.log('summarize_api.py STDOUT:', stdout);
      console.error('summarize_api.py STDERR:', stderr);
      if (stderr && !stderr.includes('WARNING')) {
        console.error('Python script error:', stderr);
        return NextResponse.json(
          { error: 'Failed to summarize video' },
          { status: 500 }
        );
      }
    } catch (execError) {
      // 3. Handle cases where Python isn't found or the script crashed
      console.error('Failed to run Python script:', execError);
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
      fs.unlinkSync(inputFile);
      fs.unlinkSync(outputFile);
      
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