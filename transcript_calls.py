"""
Transcribe the first 5 call recordings listed in Q-degree_Data_with_recording.xlsx
using OpenAI's Whisper model, in the original (native) language of each call.

Each recording is saved as <S.N.>.txt in the output folder, where S.N. is the
unique row identifier column in the sheet.

--------------------------------------------------------------------------
SETUP (run once)
--------------------------------------------------------------------------
1. Install ffmpeg (Whisper needs it to decode audio):
     - Windows (with choco):  choco install ffmpeg
     - Mac:                   brew install ffmpeg
     - Linux (Debian/Ubuntu): sudo apt install ffmpeg

2. Install the Python packages:
     pip install openai-whisper pandas openpyxl requests

--------------------------------------------------------------------------
USAGE
     python transcribe_calls.py
--------------------------------------------------------------------------
"""

import os
import requests
import pandas as pd
import whisper
import hashlib

# Monkey patch whisper._download to avoid OSError: [Errno 22] on Windows for >2GB files
original_download = whisper._download

def patched_download(url, root, in_memory):
    import os
    expected_sha256 = url.split("/")[-2]
    download_target = os.path.join(root, os.path.basename(url))
    if os.path.exists(download_target) and not os.path.isfile(download_target):
        raise RuntimeError(f"{download_target} exists and is not a regular file")
    
    if os.path.isfile(download_target):
        # Read in chunks to avoid OSError 22
        sha256 = hashlib.sha256()
        with open(download_target, "rb") as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        if sha256.hexdigest() == expected_sha256:
            return download_target
        else:
            print(f"{download_target} exists, but the SHA256 checksum does not match; re-downloading...")
            
    return original_download(url, root, in_memory)

whisper._download = patched_download

# ------------------------- CONFIG -------------------------
EXCEL_PATH = "Q-degree Data with recording.xlsx"   # path to your input Excel file
UNIQUE_COL = "S.N."                                # unique identifier column
RECORDING_COL = "Recording"                        # column with the recording URL
NUM_ROWS = 5                                        # how many rows (calls) to process

AUDIO_DIR = "downloaded_audio"                      # temp folder for downloaded audio
TRANSCRIPT_DIR = "transcripts"                      # output folder for .txt transcripts

WHISPER_MODEL_SIZE = "large-v3"                       # tiny / base / small / medium / large / large-v3
# Larger models are more accurate (especially for non-English audio) but slower.
# -------------------------------------------------------------


def download_recording(url: str, dest_path_no_ext: str) -> str:
    """
    Download the audio file from `url` and save it to disk.
    Tries to infer the correct file extension from the response headers;
    falls back to .mp3 if it can't be determined.
    Returns the full path (with extension) of the saved file.
    """
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "").lower()
    if "wav" in content_type:
        ext = ".wav"
    elif "mpeg" in content_type or "mp3" in content_type:
        ext = ".mp3"
    elif "ogg" in content_type:
        ext = ".ogg"
    elif "m4a" in content_type or "mp4" in content_type:
        ext = ".m4a"
    else:
        # Fall back to sniffing the URL, else default to mp3
        lower_url = url.lower()
        if lower_url.endswith((".wav", ".mp3", ".ogg", ".m4a")):
            ext = os.path.splitext(lower_url)[1]
        else:
            ext = ".mp3"

    full_path = dest_path_no_ext + ext
    with open(full_path, "wb") as f:
        f.write(resp.content)
    return full_path


def main():
    os.makedirs(AUDIO_DIR, exist_ok=True)
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

    # 1. Load the sheet
    df = pd.read_excel(EXCEL_PATH)
    df_subset = df.head(NUM_ROWS)

    # 2. Load Whisper once (reused for every file)
    print(f"Loading Whisper model '{WHISPER_MODEL_SIZE}' ...")
    model = whisper.load_model(WHISPER_MODEL_SIZE)

    for _, row in df_subset.iterrows():
        call_id = str(row[UNIQUE_COL]).strip()
        url = str(row[RECORDING_COL]).strip()

        print(f"\n[{call_id}] Checking recording ...")
        # Find if file already exists
        existing_files = [f for f in os.listdir(AUDIO_DIR) if f.startswith(f"{call_id}.")]
        if existing_files:
            audio_path = os.path.join(AUDIO_DIR, existing_files[0])
            print(f"[{call_id}] File already exists at {audio_path}, skipping download.")
        else:
            print(f"[{call_id}] Downloading recording ...")
            try:
                audio_path = download_recording(url, os.path.join(AUDIO_DIR, call_id))
            except Exception as e:
                print(f"[{call_id}] FAILED to download: {e}")
                continue

        print(f"[{call_id}] Transcribing (auto-detecting language) ...")
        try:
            # task="transcribe" (default) keeps the output in the SAME language
            # as the audio. language=None lets Whisper auto-detect it.
            result = model.transcribe(audio_path, task="transcribe", language=None)
        except Exception as e:
            print(f"[{call_id}] FAILED to transcribe: {e}")
            continue

        detected_lang = result.get("language", "unknown")
        transcript_text = result["text"].strip()

        out_path = os.path.join(TRANSCRIPT_DIR, f"{call_id}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(transcript_text)

        print(f"[{call_id}] Detected language: {detected_lang}")
        print(f"[{call_id}] Saved transcript -> {out_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()