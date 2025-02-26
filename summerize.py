import os
import sys
import argparse
from typing import Optional, Dict, Any
import google.generativeai as genai
from transcript import get_video_id, get_transcript

# Default settings
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.7

def setup_api_keys() -> None:
    """
    Set up API keys from .env file.
    """
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    try:
                        key, value = line.strip().split("=", 1)
                        os.environ[key] = value
                    except ValueError:
                        # Skip lines that don't have the format KEY=VALUE
                        continue
    
    # Configure Gemini API
    if os.environ.get("GOOGLE_API_KEY"):
        genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    else:
        print("Warning: GOOGLE_API_KEY not found in environment variables")

def summarize_text(
    text: str, 
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
) -> str:
    """
    Summarize text using Google's Gemini Flash model.
    """
    # Create the prompt
    prompt = f"""
You are a helpful assistant that summarizes video content. Please provide a concise summary of the following video transcript. Focus on the main points, key insights, and important details. Make the summary clear, informative, and well-structured. Do not change the language of the text , the summary must have the same languague with the input text
You need to summary following this OUTPUT format:

OUTPUT :
/ Heading of the Text/
/ Short Introduction/
/Key Features & Innovations/
/Final Conclusion/

EXAMPLE: 
INPUT : yesterday anthropic finally released Claude 3.7 Sona the highly anticipated large language model that's most loved and most feared by programmers their announcement video has everybody freaking out and the top comment on that video is people waiting for this video and let me just say I'm humbled and honored that you put so much faith into my half-ass AI reviews I've already burned through millions of tokens testing it and the tldr is that Claud 3.7 is straight gas hits different matte heat highkey goated on God no cap for real for real the new base model beat itself to become even better at programming while adding a new thinking mode to copy the success of deep seek R1 in the open AO models but the craziest thing they released is something called Claude code a CLI tool that allows you to build test and execute code in any project thus creating an infinite feedback loop that in theory should replace all programmers all the code influencers are telling us we're cooked and in today's video we'll find out if they're right it is February 25th 2025 and you're watching the code report a few weeks ago anthropic released a paper that studied how AI affects the labor force and what they found is that despite only making up 3.4% of the workforce over 37% of the prompts are related to math and coding and although it hasn't taken any human programmer jobs yet it has taken stack overflows job now there's a lot of AI slot word out there and it's hard to keep track of it all but for web development one of the better indicators is web dev Arena and Claude 3.5 the previous version is already sitting on top of that leaderboard but it was roughly tied with all of the other state-of-the-art models when it comes to the software engineering Benchmark which is human verif ified and based on real GitHub issues what's crazy though is that the new 3.7 model absolutely crushed all the other models including open AI O3 mini high and deep seek and is now capable of solving 70.3% of GitHub issues that is if we're to believe the Benchmark and after trying out the CLA code CLI I might actually believe it it's in research preview currently but you can install the CLA CLI with npm disclaimer though it uses the anthropic API directly and CLA is not cheap costing over 10 times more than models like Gemini Flash and deepsea $15 per million output tokens cost more than my entire personality once installed you'll have access to the CLA command in the terminal and that gives it the full context of existing code in your project one thing I noticed immediately though is that their text decoration in the CLI looks almost identical to SST an open source tool we've covered on this channel before that could be a coincidence but it appears the clo logo might also be plagiarized based on this drawing of a butthole by one of my favorite authors Kurt vonet now there's nothing wrong with designing your logo after a sphincter plenty of companies do it but I think CLA is just a little too on the nose here but now that I have CLA installed I can run the in command which will scan the project and create a markdown file with some initial context and instructions that's cool but now we have an open session and one thing you might want to do is see how much money you've lost by prompting so far with the cost command I can see that creating that AIT file cost about 8 cents now the first actual job I gave it was pretty easy and that was to create a random name generator in Dino after you enter a prompt it will figure out what to do and then have you confirm it with a yes or no like in this case here it wants to generate a new file it'll go ahead and write that file to the file system and then it also creates a dedicated testing file as well that's important because using a strongly typed language along with test driven development are ways for the AI to validate that the code it writes is actually valid if that test fails it can use the feedback to rewrite the business logic and continue going back and forth until it gets it right and in this example it wrote what I would consider perfect code but now let's do something more challenging and have it build an actual visual front end UI but instead of react we'll use spelt when I generated the config you'll notice that it understands the text stack is using typescript and tailwind and then I'll prompt it for a moderately complex front-end UI an application that can access my microphone and visualize the waveform after this initial prompt I had to confirm like 20 different things and as you can see it wrote a bunch of new components to my project it took a lot longer than just prompting claw in the web UI but the end result was worth the wait here in the application I can click through a waveform frequency and circular graphic that visualizes the sound of my voice as a control I had open aai 03 mini High generate the same thing and at first I got an error which was easy to fix but the end result looked like this an embarrassing piece of crap compared to Claude but upon closer inspection there were a lot of problems in claude's code like for one it didn't use typescript or Tailwind at all even though it should know that they're in our Tex stack it also failed to use the new spell 5 Rune syntax and the entire session cost me about 65 cents which would have been better spent on an egg or a banana but now I have one final test recently Apple had to discontinue ending and encryption in the UK because the government wanted a back door and apple refused to build one if you've been affected by this one thing you can do is build your own and an encrypted app I've been trying to do that myself in JavaScript but every single large language model that I've tried fails let's see if Claud code can fix this chat GPT garbage code it took quite a while and changed a lot of the code but for whatever reason it still fails to run and unfortunately because I become so dependent on AI I have no idea how to fix an error message like this and all I can really do is wait for the next best model to come out throughout the video we've seen how good CLA is at front end Dev but the other half to your application is the back end and if you like building apps fast you need to try out convex the sponsor of today's video it's an open- Source reactive database that provides typesafe queries scheduled jobs server functions real-time data sync like Firebase just to name a few of its features best of all though database queries are written in pure typescript giving us this beautiful IDE autocomplete across the entire stack but that also creates another side effect making convex really good at autonomous Vibe coding with AI models like Claude can more easily understand comvex code write it with fewer errors and thus be more productive with it if you know how to build a front-end app you're already halfway there now use the link on the screen to create a free convex project to build the other half this has been the code report thanks for watching and I will see you in the next one
OUTPUT : 

**Claude 3.7 Sonar: A Breakthrough in AI-Driven Programming**  

Anthropic's release of **Claude 3.7 Sonar**, a large language model (LLM), has sparked excitement and concern among programmers. The model claims to outperform predecessors and rivals in coding tasks, particularly solving **70.3% of real GitHub issues** in benchmarks, surpassing OpenAI's GPT-3.5 and DeepSeek's models.

### Key Features :

1. **Claude Code CLI Tool**:
    
    - A command-line interface that scans projects, writes/testes code, and iterates via feedback loops.
        
    - Integrates with existing codebases, using test-driven development (TDD) to validate and refine code.
        
    - Costs **$15 per million output tokens**, significantly pricier than competitors like Gemini Flash.
        
2. **Performance Highlights**:
    
    - **Front-End Development**: Successfully built a voice-visualization UI with Svelte, though it ignored TypeScript/Tailwind guidelines.
        
    - **Back-End Potential**: Demonstrates promise for autonomous coding with tools like **Convex** (sponsor), a reactive database that pairs well with AI-generated TypeScript.
        
    - **Shortcomings**: Struggled with complex tasks like building an encrypted app, highlighting lingering limitations.
        
3. **Comparison with Competitors**:
    
    - Outperformed GPT-3.5 in generating functional, clean code but faced challenges with syntax adherence.
        
    - Criticized for high costs and occasional inconsistencies, despite superior results in visual and logic-based tasks.

**Final Take**: Claude 3.7 Sonar represents a leap in AI-driven coding, excelling in front-end tasks and iterative problem-solving. However, its high cost and occasional oversights underscore that human oversight remains essential. For developers, it's a transformative tool—not yet a replacement.

TRANSCIPT THIS TEXT : 
{text}
SUMMARY":
"""

    try:
        # Configure the model with the correct name
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generate the summary
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
            )
        )
        
        # Extract and return the summary
        return response.text.strip()
    
    except Exception as e:
        print(f"Error during summarization: {str(e)}")
        return f"Failed to generate summary: {str(e)}"

def process_video_and_summarize():
    """
    Process a video and summarize its transcript.
    """
    print("\n=== YouTube Video Summarizer ===\n")
    
    # Step 1: Ask for language preference
    print("Select transcript language:")
    print("1. English (en)")
    print("2. Vietnamese (vi)")
    
    while True:
        lang_choice = input("Enter your choice (1 or 2): ").strip()
        if lang_choice == "1":
            language = "en"
            break
        elif lang_choice == "2":
            language = "vi"
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")
    
    # Step 2: Get the URL and process
    url = input("\nEnter YouTube URL: ").strip()
    
    if not url:
        print("Error: URL cannot be empty")
        return
    
    try:
        # Extract video ID
        video_id = get_video_id(url)
        print(f"\nProcessing video ID: {video_id}")
        
        # Get transcript
        transcript_text = get_transcript(video_id, language)
        print(f"\nTranscript retrieved in {language}")
        
        # Generate summary
        print("\nGenerating summary using Gemini 2.0 Flash...")
        summary = summarize_text(transcript_text)
        
        # Print summary
        print("\nSummary:")
        print("=" * 50)
        print(summary)
        print("=" * 50)
        
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    # Set up API keys
    setup_api_keys()
    
    # Process videos in a loop
    while True:
        process_video_and_summarize()
        
        continue_option = input("\nSummarize another video? (y/n): ").strip().lower()
        if continue_option != 'y':
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()
