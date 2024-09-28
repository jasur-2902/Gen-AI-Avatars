import cv2
import json
from moviepy.editor import VideoFileClip, AudioFileClip


"""
This script combines images (representing visemes) and an audio file to generate a synchronized video. It reads a JSON file that contains information about the timing and sequence of visemes, creates a video sequence of these viseme images, and then merges the audio into the video using `moviepy`.

### Key Steps:

1. **Loading JSON Data**:
   - The script loads a JSON file that defines the timing (`offset`) and IDs of visemes (mouth positions). 
   - Each viseme ID corresponds to a specific image file, which is used to create the video frames.

2. **Generating the Video**:
   - The video is created frame-by-frame by combining images (one per viseme) with specific durations.
   - The duration for each viseme is calculated based on the difference between the current viseme's `offset` and the next one.
   - Frames per second (FPS) is set at 25, and each image is resized to match the video dimensions.

3. **Merging Audio and Video**:
   - Once the video is created from the viseme images, the script adds the audio file using `moviepy`. 
   - The final video is saved with both audio and video tracks.

### Key Functionality:
- **Video Writing with OpenCV**: 
  - The video frames are written using the `cv2.VideoWriter` method, which handles each viseme image as a frame.

- **Audio-Video Merging with moviepy**: 
  - After generating the silent video, the audio is added using `moviepy` to create a synchronized final output.

### How to Use:
1. Ensure you have the required libraries installed:
   ```bash
   pip install opencv-python moviepy
"""


# Replace these paths with your actual file paths
json_file_path = 'metadata/24.json'
audio_file_path = 'audio/24.wav'
viseme_image_dir = 'image/mouth/'
output_video_path = 'video/output_video.mp4'

# Load JSON data
with open(json_file_path, 'r') as f:
    data = json.load(f)

# Assuming your JSON structure contains a list of visemes with id and offset
# Example: [{"visemeId": 1, "offset": 1000}, {"visemeId": 2, "offset": 2000}]
# and you have the duration of each viseme to calculate the time it should be displayed

# Settings for the video
fps = 25  # Frames per second
frame_duration = 1000 / fps  # Duration of each frame in milliseconds

# Prepare the video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
height, width = 901,859  # Set the height and width according to your viseme images
video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

for viseme in data:
    viseme_id = viseme["id"]
    start_offset = viseme["offset"]
    # Assuming you have a way to calculate the end of each viseme, perhaps the start of the next one
    # For the last viseme, you might need to estimate or define a fixed duration
    if viseme != data[-1]:
        end_offset = data[data.index(viseme) + 1]["offset"]
    else:
        end_offset = start_offset + 1000  # Example fixed duration of 1 second for the last viseme
    duration = end_offset - start_offset
    
    # Calculate how many frames to generate for this viseme
    frame_count = int(duration / frame_duration)
    
    # Load the viseme image
    viseme_image_path = f'{viseme_image_dir}viseme-id-{viseme_id}.jpg'
    viseme_image = cv2.imread(viseme_image_path)
    viseme_image = cv2.resize(viseme_image, (width, height))  # Ensure image fits video dimensions
    
    # Write the image frames to the video
    for _ in range(frame_count):
        video_writer.write(viseme_image)

# Release the video writer
video_writer.release()

# Add audio to the video
video_clip = VideoFileClip(output_video_path)
audio_clip = AudioFileClip(audio_file_path)
final_clip = video_clip.set_audio(audio_clip)
final_clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac")