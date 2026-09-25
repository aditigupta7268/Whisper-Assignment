import json
from processing import MeetingPipeline

def main():
    print("Initializing pipeline...")
    try:
        pipeline = MeetingPipeline()
        print("Processing audio file...")
        result = pipeline.process(r"C:\Users\intel\Desktop\Transcript code\downloaded_audio\1.mp3")
        
        # Save output to a file so we can view it easily
        output_file = "test_result.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
            
        print(f"Processing complete! Results saved to {output_file}")
    except Exception as e:
        print(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()
