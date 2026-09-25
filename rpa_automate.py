import pyautogui
import time
import os

# NOTE: Before running this script, you MUST install pyautogui:
# pip install pyautogui

def automate_whisper_transcribe(audio_file_path):
    print("Starting RPA automation in 5 seconds. Please ensure the WhisperTranscribe window is visible on your screen!")
    time.sleep(5)
    
    # --- IMPORTANT: UPDATE THESE COORDINATES USING get_coords.py ---
    UPLOAD_TAB_X, UPLOAD_TAB_Y = 130, 380
    SELECT_BUTTON_X, SELECT_BUTTON_Y = 275, 615
    TRANSCRIBE_BUTTON_X, TRANSCRIBE_BUTTON_Y = 418, 885
    
    # 1. Click "Upload file" tab
    print("Clicking 'Upload file' tab...")
    pyautogui.click(x=UPLOAD_TAB_X, y=UPLOAD_TAB_Y)
    time.sleep(1)

    # 2. Click "Select a file" purple button
    print("Clicking 'Select a file' button...")
    pyautogui.click(x=SELECT_BUTTON_X, y=SELECT_BUTTON_Y)
    time.sleep(2)
    
    # 3. Type the path of the audio file in the Windows file explorer window
    print(f"Typing file path: {audio_file_path}")
    pyautogui.write(audio_file_path)
    time.sleep(1)
    
    # 4. Press Enter to select the file
    pyautogui.press('enter')
    
    # Wait for the file to load in the UI (User reported it takes 20 seconds)
    print("Waiting 25 seconds for the file to finish loading into the app...")
    time.sleep(25)
    
    # 5. Click the "Transcribe Now" button
    print("Clicking 'Transcribe Now'...")
    pyautogui.click(x=TRANSCRIBE_BUTTON_X, y=TRANSCRIBE_BUTTON_Y)
    
    print("Automation script complete! The app should now be transcribing.")

if __name__ == "__main__":
    test_audio = r"C:\Users\intel\Desktop\Transcript code\downloaded_audio\1.mp3"
    if os.path.exists(test_audio):
        automate_whisper_transcribe(test_audio)
    else:
        print(f"Could not find audio file: {test_audio}")
