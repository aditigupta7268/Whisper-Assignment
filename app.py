from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import tempfile
import os
import shutil
import uuid

# Import the processing pipeline
from processing import MeetingPipeline

app = FastAPI(title="Voice-Based Minutes of Meeting Pipeline")

# Initialize pipeline (this loads the models, which takes time and memory)
try:
    pipeline = MeetingPipeline()
except Exception as e:
    print(f"Failed to initialize pipeline: {e}")
    pipeline = None

# Store results in memory for simplicity (in a real app, use a database)
results_db = {}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Voice-Based Minutes of Meeting API"}

@app.post("/upload")
async def upload_audio(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not pipeline:
        raise HTTPException(status_code=500, detail="Pipeline not initialized. Check server logs.")
        
    if not file.filename.endswith(('.wav', '.mp3', '.m4a', '.mp4', '.avi', '.mkv')):
        raise HTTPException(status_code=400, detail="Unsupported file format.")

    # Generate a unique task ID
    task_id = str(uuid.uuid4())
    
    # Save uploaded file to a temporary location
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Initialize task status
    results_db[task_id] = {"status": "processing", "result": None}

    # Run processing in the background so the API returns immediately
    background_tasks.add_task(process_audio_task, task_id, file_path, temp_dir)

    return {"task_id": task_id, "message": "File uploaded successfully. Processing started in the background."}


def process_audio_task(task_id: str, file_path: str, temp_dir: str):
    """Background task to process the audio file."""
    try:
        # Run the full pipeline
        result = pipeline.process(file_path)
        results_db[task_id] = {"status": "completed", "result": result}
    except Exception as e:
        print(f"Error processing task {task_id}: {e}")
        results_db[task_id] = {"status": "failed", "error": str(e)}
    finally:
        # Clean up temporary files
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


@app.get("/results/{task_id}")
def get_results(task_id: str):
    """Retrieve the results of a processed meeting."""
    if task_id not in results_db:
        raise HTTPException(status_code=404, detail="Task ID not found")
        
    task_info = results_db[task_id]
    
    if task_info["status"] == "processing":
        return {"status": "processing", "message": "The file is still being processed."}
    elif task_info["status"] == "failed":
        return {"status": "failed", "error": task_info["error"]}
    else:
        return {"status": "completed", "data": task_info["result"]}

if __name__ == "__main__":
    import uvicorn
    # Run the API server
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
