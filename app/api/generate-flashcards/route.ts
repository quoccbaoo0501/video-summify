import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execPromise = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const { summary, numCards = 10 } = await request.json();
    
    if (!summary) {
      return NextResponse.json(
        { error: 'Summary is required' },
        { status: 400 }
      );
    }
    
    // Create unique temporary files for input and output
    const uniqueId = `${Date.now()}-${Math.floor(Math.random() * 1e7)}`;
    const inputFile = path.join(process.cwd(), `temp_flashcards_input_${uniqueId}.json`);
    const outputFile = path.join(process.cwd(), `temp_flashcards_output_${uniqueId}.json`);
    
    // Prepare input data for the Python script
    const inputData = {
      summary,
      num_cards: numCards
    };
    
    // Write input data to file
    fs.writeFileSync(inputFile, JSON.stringify(inputData));
    
    // Choose which Python command to run
    const pythonCommand = process.env.PYTHON_PATH || 'python';
    
    try {
      // Attempt to run the Python script with full path resolution
      const scriptPath = path.join(process.cwd(), 'flashcards_api.py');
      const command = `${pythonCommand} "${scriptPath}" "${inputFile}" "${outputFile}"`;
      console.log('Running command:', command);
      
      // Execute the Python script with input file path as argument
      const { stdout, stderr } = await execPromise(command);
      
      // Log script output for debugging
      console.log('Flashcards script STDOUT:', stdout);
      console.error('Flashcards script STDERR:', stderr);
      
      if (stderr && !stderr.includes('WARNING')) {
        console.error('Python script error:', stderr);
        return NextResponse.json(
          { error: 'Failed to generate flashcards' },
          { status: 500 }
        );
      }
    } catch (execError) {
      console.error('Failed to run Python script:', execError);
      return NextResponse.json(
        { error: `Unable to run flashcards script: ${execError}` },
        { status: 500 }
      );
    }
    
    // Read the output file
    if (fs.existsSync(outputFile)) {
      const outputData = JSON.parse(fs.readFileSync(outputFile, 'utf-8'));
      
      // Clean up temporary files
      fs.unlinkSync(inputFile);
      fs.unlinkSync(outputFile);
      
      return NextResponse.json({
        flashcards: outputData.flashcards
      });
    } else {
      return NextResponse.json(
        { error: 'Failed to generate flashcards output' },
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