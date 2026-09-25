# Voice-Based Minutes of Meeting Pipeline

This project provides a robust, open-source pipeline to generate structured Minutes of Meeting from audio/video recordings. It handles multilingual conversations (English, Hindi, Odia), speaker diarization (identifying who spoke when), and generates a concise summary with key points and action items.

## Core Technologies Used
* **Speech-to-Text (Transcription):** `whisper` (OpenAI's open-source model). Chosen for its excellent multilingual support (including Odia and Hindi) and code-switching capabilities without relying on external paid APIs.
* **Speaker Diarization:** `pyannote.audio`. Chosen as the state-of-the-art open-source diarization model for identifying distinct speakers and generating timestamps.
* **Summarization (NLP):** `transformers` (`facebook/bart-large-cnn`). Used to generate the meeting summary entirely locally.
* **Backend API:** `FastAPI`. Used for asynchronous processing and easy API interaction.

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
     * **Windows:** `set HF_TOKEN=your_huggingface_token`
     * **Linux/Mac:** `export HF_TOKEN=your_huggingface_token`

## Running the Pipeline

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

## Output Structure
The result JSON contains:
* `language`: The primary language detected by Whisper.
* `segments`: The full transcript, broken down chronologically with `start` time, `end` time, `speaker` ID, and the spoken `text`.
* `statistics`: Total speaking time and percentage per speaker.
* `summary`: A concise NLP-generated summary of the meeting.

## Known Limitations
* Processing is extremely CPU-intensive. On standard hardware without a dedicated GPU, processing a 5-minute audio file can take 15+ minutes.
* Whisper's Odia support (`or`) is functional but may have higher Word Error Rates (WER) compared to English or Hindi due to smaller training datasets in the base/small models. Use the `large-v3` model by modifying `processing.py` if greater Odia accuracy is required and VRAM permits.
