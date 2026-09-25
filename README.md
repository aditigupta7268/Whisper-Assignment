# Voice-Based Minutes of Meeting Pipeline

## Objective & Problem Statement
This project provides a robust, open-source pipeline to generate structured Minutes of Meeting (MoM) from audio/video recordings. It analyzes recorded meetings and generates a structured transcript with speaker identification, timestamps, speaker-wise conversation statistics, and a final meeting summary. 

It handles multilingual conversations, including English, Hindi, and Odia, as well as code-switching between these languages.

## Architecture & Technology Choices
The core pipeline avoids using any paid or external LLM APIs (like OpenAI API, Gemini, etc.), relying completely on powerful open-source models:

* **Speech-to-Text (Transcription & Multilingual):** `whisper` (OpenAI's open-source model running locally). The `medium` model was chosen for its excellent multilingual support (including Odia and Hindi) and code-switching capabilities.
* **Speaker Diarization:** `pyannote.audio`. Chosen as the state-of-the-art open-source diarization model for distinguishing distinct speakers and generating accurate chronological timestamps.
* **Summarization (NLP):** `transformers` (`facebook/bart-large-cnn`). Used to generate the meeting summary, key points, and action items entirely locally.
* **Backend API:** `FastAPI`. Used for handling asynchronous processing and providing a simple upload/retrieval interface.

## Prerequisites
1. Python 3.8+ installed.
2. `ffmpeg` installed on your system (required for audio preprocessing and PyDub).
3. A Hugging Face account and Access Token (Required for downloading the Pyannote diarization model).

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Accept Pyannote Terms & Get Hugging Face Token:**
   * Go to [pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1) and [pyannote/segmentation-3.0](https://huggingface.co/pyannote/segmentation-3.0) on Hugging Face and accept the user conditions.
   * Create an Access Token in your Hugging Face settings.
   * Set it as an environment variable in your terminal:
     * **Windows PowerShell:** `$env:HF_TOKEN="your_huggingface_token"`
     * **Linux/Mac:** `export HF_TOKEN=your_huggingface_token`

## Execution Instructions

1. **Start the API Server:**
   ```bash
   python app.py
   ```
   The server will start at `http://localhost:8000`.

2. **Upload a Meeting (POST):**
   You can use `curl`, Postman, or the built-in Swagger UI to upload a file:
   * Swagger UI: Go to `http://localhost:8000/docs`
   * Or via curl:
     ```bash
     curl -X 'POST' \
       'http://localhost:8000/upload' \
       -H 'accept: application/json' \
       -H 'Content-Type: multipart/form-data' \
       -F 'file=@your_meeting_audio.wav'
     ```
   The API will return a `task_id` because processing is done asynchronously in the background.

3. **Retrieve Results (GET):**
   * Use the `task_id` returned from the upload to check the status/results.
   * Go to `http://localhost:8000/results/{task_id}`

*(Alternatively, run `python test_run.py` to directly test the pipeline on a local audio file and output to `test_result.json`)*.

## Deliverables & Output Structure
The result JSON (e.g., `test_result.json`) successfully delivers all required data points:
* **Language Detection:** `language` key showing the primary language detected by Whisper.
* **Structured Transcript & Speaker Diarization:** `segments` key breaking down the full transcript chronologically with `start` time, `end` time, `speaker` ID (e.g., SPEAKER_00), and the spoken `text`.
* **Speaker-wise Conversation Statistics:** `statistics` key calculating the total speaking time in seconds and the overall proportion/percentage of time per speaker.
* **Meeting Summary:** `summary` key containing a concise NLP-generated summary of the meeting highlighting the main discussion points.

## Test Results and Known Limitations
* **CPU Intensive Processing:** Processing is heavily CPU-intensive. On standard hardware without a dedicated GPU, processing a 5-minute audio file using the Whisper `medium` model can take significant time.
* **Odia (or) Accuracy:** Whisper's Odia support is functional, but due to smaller training datasets compared to English or Hindi, Word Error Rates (WER) may be slightly higher on heavily accented or overlapping Odia speech.
* **Overlapping Speech:** Pyannote can handle slight interruptions, but heavy overlapping speech may occasionally combine segments. 
