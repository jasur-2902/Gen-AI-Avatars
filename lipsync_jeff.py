import os
import requests
import json
import moviepy.editor as mpy

"""
This class, `LipSync`, provides functionality for generating a lip-sync video by uploading an image and an audio file to a remote service, handling API keys securely, and post-processing the video (such as rotating it). The class uses the `moviepy` library to manipulate video files and `requests` for API communication.

### Key Functions:

1. **`__init__(self, person)`**:
   - Initializes the `LipSync` object with the name of the person (used to find the input image file).
   
2. **`save_int(value)` and `load_int()`**:
   - Save and load an integer value from a file (`secret_key.txt`). These methods are used to switch between two secret keys (`sk_1` and `sk_2`) for API authentication.

3. **`load_images()`**:
   - Loads the necessary image and audio files (hardcoded to `24.wav` for audio and `{person}.jpg` for the image) into the `files` list, which will be sent with the API request.

4. **`rotate()`**:
   - Rotates the downloaded video using `moviepy` (currently set up to save the video without rotating, but can be adjusted to rotate by degrees, e.g., 90 degrees).
   - Saves the rotated (or non-rotated) video to `'video/2.mp4'`.

5. **`generateVideo()`**:
   - Uploads the image and audio files to the API to generate a lip-sync video.
   - Switches between two secret API keys for authentication and saves the current key usage to `secret_key.txt`.
   - Once the API response is received, it downloads the generated video and saves it to `'video/lipsync.mp4'`.
   - Optionally rotates the downloaded video using the `rotate()` method.

### How to Use:

1. **Set Up the Required Libraries**:
   Ensure the following Python libraries are installed:
   ```bash
   pip install requests moviepy
"""

class LipSync:
    def __init__(self, person):
        self.person = person

    def save_int(self, value):
        with open('secret_key.txt', 'w') as f:
            f.write(str(value))

    def load_int(self):
        with open('secret_key.txt', 'r') as f:
            return int(f.read())

    files = []
    
    def load_images(self): 
        self.files = [
            ("input_face", open(f"{self.person}.jpg", "rb")),
            ("input_audio", open("audio/24.wav", "rb")),
        ]
    payload = {}

    sk_1 = "sk-"
    sk_2 = "sk-"

    def rotate(self):
        # Load the video
        clip = mpy.VideoFileClip('video/lipsync.mp4')

        # Rotate the video (adjust the rotation degree as needed)
        # rotated_clip = clip.rotate(90)  

        # Save the rotated video
        clip.write_videofile('video/2.mp4')

    def generateVideo(self):
        self.load_images()
        secret_key = self.sk_1 
        which_key = self.load_int()
        if which_key == 1:
            secret_key = self.sk_2
            self.save_int(2)
            print("which key: 1")
        else: 
            self.save_int(1)
            print("which key: 2")

        response = requests.post(
            "https://api.gooey.ai/v2/Lipsync/form/",
            headers={
                "Authorization": "Bearer " + secret_key,
            },
            files = self.files,
            data={"json": json.dumps(self.payload)},
        )

        # assert response.ok, response.content

        result = response.json()
        print(response.status_code, result)
        # Parse the JSON string into a Python dictionary

        # Access the output_video URL from the parsed JSON
        if response.status_code == 200:
            data = result
            video_url = data['output']['output_video']
            video_download_request = requests.get(video_url)
            if video_download_request.status_code == 200:
                # Save the video to a file
                with open('video/lipsync.mp4', 'wb') as file:
                    file.write(video_download_request.content)
                self.rotate() # <- This is optional for my use case I needed it :)
                print("Download successful!")
                
        else:
            print("Failed to download the video. Status code:", response.status_code)
