import pyautogui
import time

print("--- MOUSE CALIBRATION TOOL ---")

# Step 1
input("Press ENTER when you are ready to capture the 'Upload file' tab (white box)...")
print("Get ready! Move your mouse over it now.")
for i in range(5, 0, -1):
    print(f"{i}...")
    time.sleep(1)
x1, y1 = pyautogui.position()
print(f"Captured 'Upload file' tab at: X={x1}, Y={y1}\n")

# Step 2
input("Press ENTER when you are ready to capture the purple 'Select a file' button...")
print("Get ready! Move your mouse over it now.")
for i in range(5, 0, -1):
    print(f"{i}...")
    time.sleep(1)
x2, y2 = pyautogui.position()
print(f"Captured 'Select a file' button at: X={x2}, Y={y2}\n")

# Step 3
print("Now, go ahead and manually select an audio file in the app and wait for it to load.")
input("Press ENTER when the file is loaded and you can see the 'Transcribe Now' button on screen...")
print("Get ready! Move your mouse over the 'Transcribe Now' button.")
for i in range(5, 0, -1):
    print(f"{i}...")
    time.sleep(1)
x3, y3 = pyautogui.position()
print(f"Captured 'Transcribe Now' button at: X={x3}, Y={y3}\n")

print("-" * 30)
print("Go to rpa_automate.py and update these variables at the top of the file:")
print(f"UPLOAD_TAB_X, UPLOAD_TAB_Y = {x1}, {y1}")
print(f"SELECT_BUTTON_X, SELECT_BUTTON_Y = {x2}, {y2}")
print(f"TRANSCRIBE_BUTTON_X, TRANSCRIBE_BUTTON_Y = {x3}, {y3}")
