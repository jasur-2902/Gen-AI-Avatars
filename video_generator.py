import sys
import os
import json
import cv2
from moviepy.editor import VideoFileClip, AudioFileClip
import argparse
import numpy as np
from lipsync_jeff import LipSync
from play_video import VideoPlayer
from PyQt5 import QtWidgets

duration = 95
fps = 60


"""
This script generates a lip-sync video by combining viseme images (mouth shapes) with corresponding audio, creating a synchronized video. It uses viseme data from a JSON file to determine the timing of each viseme image and overlays the audio on the generated video. The `VideoMaker` class is the core component that handles video generation and audio synchronization. The script supports multiple modes (e.g., "beff-mode", "Hulk-mode") and allows for dynamic video creation based on the mode selected.

### Key Components:

1. **`VideoMaker` Class**:
   - This class handles the video generation from viseme images and metadata, and then combines the video with audio to create a final synchronized lip-sync video.
   - The class reads viseme metadata (timing and ID) from a JSON file and maps these visemes to corresponding images stored in a directory.
   - The video is generated frame-by-frame based on the viseme timings, and the audio is added afterward.

2. **LipSync Mode**:
   - The script allows for different "modes" such as "beff-mode" and "Hulk-mode", which use the `LipSync` class to generate a video with different characteristics.
   - Depending on the mode selected, the script can either use predefined lip-sync behavior or generate a regular video using the provided viseme metadata and images.

3. **Audio and Video Synchronization**:
   - After the video is generated from viseme images, the script uses `moviepy` to merge the corresponding audio.
   - If the audio is longer than the video, it is clipped to match the video duration, ensuring synchronization between the audio and video.

### Key Functions in the `VideoMaker` Class:

1. **`__init__(self, images_dir, visemes_dir, audio_dir, out_dir, fps, map_file, callback, mode)`**:
   - Initializes the class with directories for viseme images, metadata, audio files, output video, and other configurations such as FPS (frames per second) and mode.

2. **`generate_video(self, in_file)`**:
   - Generates a video from viseme images and metadata stored in JSON files.
   - It reads viseme timings from the JSON file and creates the video by displaying the corresponding viseme images for each time interval.

3. **`add_audio(self, audio_file, video_file)`**:
   - Adds an audio track to the generated video using `moviepy`.
   - The audio is synchronized with the video, and the script clips either the audio or video to ensure they match in duration.

4. **`make_frame(self, id)`**:
   - Loads and processes the viseme image corresponding to the given ID. This image is resized and rotated before being added to the video.

### How to Use:

1. **Set Up the Required Libraries**:
   Ensure you have the required Python libraries installed:
   ```bash
   pip install opencv-python moviepy numpy PyQt5
"""

class VideoMaker:
    def __init__(self, images_dir, visemes_dir, audio_dir, out_dir, fps, map_file, callback, mode):
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.height, self.width = self.get_im_dims(images_dir)
        self.im_dir = images_dir
        self.metadata_dir = visemes_dir
        self.audio_dir = audio_dir
        self.out_dir = out_dir
        self.fps = 60
        self.duration = 0
        self.callback = callback
        self.mode = mode
        print("Init VideoMaker")

    def load_json(self, file):
        with open(file, "r") as opened_file:
            return json.load(opened_file)

    def get_im_dims(self, im_dir):  # should first check the file is an image
        for image in os.listdir(im_dir):
            try:
                frame = cv2.imread(os.path.join(im_dir, image))
                height, width, channels = frame.shape
                return height, width
            except Exception as e:
                print(f"Error: {e}")
                continue

    def get_out(self, out_path):
        return cv2.VideoWriter(out_path, self.fourcc, self.fps, (self.width, self.height))

    def read_chunk_data(self, chunk):
        return chunk["id"], chunk["offset"]

    def make_frame(self, id):
        print(f"Generating frame for viseme id {id}.")
        frame = cv2.imread(os.path.join(self.im_dir, f"viseme-id-{id}.jpg"))
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        return cv2.resize(frame, (self.width, self.height))

    def frame_to_video(self, output, frame, dur):
        for i in range(int(np.round(dur / 1000 * self.fps, 0))):
            output.write(frame)

    def generate_video(self, in_file):
        if(self.mode == "beff-mode"):
            print("\n Beff Mode \n")
            lipSync = LipSync("beff")
            lipSync.generateVideo()
            return
        elif(self.mode == "Hulk-mode"):
            print("\n Hulk Mode \n")
            lipSync = LipSync("hulk")
            lipSync.generateVideo()
            return

        in_path = os.path.join(self.metadata_dir, in_file)
        self.out_path = os.path.join(self.out_dir, f'{in_file.strip(".json")}_{self.fps}.mp4')
        print(f"Generating video from {self.out_path}.")
        output = self.get_out(self.out_path)
        data = self.load_json("metadata/text_to_viseme.json")
        print(len(data))

        total_time = 0
        viseme_dur = 0
        for chunk in data:
            mapped, dur = self.read_chunk_data(chunk)
            dur = dur - total_time
            print(f"Viseme id {mapped} has duration {dur} milliseconds.")
            total_time += dur
            frame = self.make_frame(mapped)
            self.frame_to_video(output, frame, dur)
            viseme_dur += dur
        output.release()
        cv2.destroyAllWindows()
        print(f"Generated video of {viseme_dur} milliseconds from viseme images.")

    def add_audio(self, audio_file, video_file):
        video_clip = VideoFileClip(video_file)
        audio_clip = AudioFileClip(audio_file)
        print("Audio File: "  + audio_file)
        print(f"Adding audio stream of {audio_clip.end} milliseconds.")
        if video_clip.end < audio_clip.end:
            audio_clip = audio_clip.subclip(0, video_clip.end)
            print(f"Clipped audio file to {video_clip.end} milliseconds.")
        elif audio_clip.end < video_clip.end:
            video_clip = video_clip.subclip(0, audio_clip.end)
            print(f"Clipped video file to {audio_clip.end} milliseconds.")

        final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile(f'video/temp.mp4', codec="libx264", audio_codec="aac")

        final_video = video_clip.set_audio(audio_clip)
        print(f"Successfully generated video of {final_video.end} milliseconds from video and audio streams.")
        video_out_path = f'video/2{os.path.basename(self.im_dir)}_with_audio_{video_file.strip(".json").strip("video/")}'
        # final_video.write_videofile(video_out_path, fps=self.fps)
        final_video.write_videofile(video_out_path, fps=self.fps, audio_codec="aac")

        print(f"Video successfully saved to {video_out_path}.")

        self.callback()


def main():
    parser = argparse.ArgumentParser(
        description="Specify metadata, audio, image and output directories, and viseme mapping file."
    )
    parser.add_argument("--im_dir", type=str, default="image/mouth", help="Directory with viseme images.")
    parser.add_argument(
        "--metadata_dir", type=str, default="metadata", help="Directory containing viseme metadata .json files."
    )
    parser.add_argument("--audio_dir", type=str, default="audio", help="Directory containing .wav audio files.")
    parser.add_argument("--out_dir", type=str, default="video", help="Directory to save generated video.")
    parser.add_argument("--fps", type=int, default=60, help="Frame rate (in frames per second) to generate video.")
    parser.add_argument("--map", type=str, default="map/viseme_map.json", help="Path to viseme mapping file.")
    parser.add_argument("--no_audio", action="store_true", help="Generated video without audio.")
    args = parser.parse_args()
    viseme_video_maker = VideoMaker(args.im_dir, args.metadata_dir, args.audio_dir, args.out_dir, args.fps, args.map, None)

    for in_file in os.listdir(args.metadata_dir):
        if ".json" not in in_file:
            continue
        else:
            viseme_video_maker.generate_video(in_file)
            print(f"Generated video from {in_file}.")
            if (viseme_video_maker.mode != "beff-mode"):
                if args.no_audio is not True:
                    viseme_video_maker.add_audio(f'audio/text_to_audio.wav', viseme_video_maker.out_path)
                    # combine_audio_video(audio_file_path_new, video_file_path_new, output_file_path_new)


def combine_audio_video(audio_file_path, video_file_path, output_file_path):
    audio_clip = AudioFileClip(audio_file_path)
    video_clip = VideoFileClip(video_file_path)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_file_path, codec="libx264", audio_codec="aac")
    print("Done")

# Update these paths according to your files' locations
audio_file_path_new = '/audio/text_to_audio.wav'  
video_file_path_new = '/video/video.mp4'
output_file_path_new = '/video/output_video.mp4'

if __name__ == "__main__":
    main()