import os
import json
import cv2
from moviepy.editor import VideoFileClip, AudioFileClip
import argparse
import numpy as np
import azure.cognitiveservices.speech as speechsdk

duration = 95
fps = 1 / (duration / 1000)

"""
This script generates a lip-sync video using Azure's Text-to-Speech service and viseme data (mouth movements) synchronized with the audio. It reads viseme data from a JSON file, generates a video by mapping viseme images to the audio, and finally combines the audio and video into a single output file. The `VideoMaker` class handles video generation and audio merging.

### Key Components:

1. **Azure Text-to-Speech (TTS) Synthesis**:
   - The script uses Azure TTS to generate audio and viseme data (mapping between speech sounds and mouth movements).
   - The viseme data is saved in a JSON file (`metadata/24.json`), which stores the timing (`offset`) and the corresponding viseme ID.

2. **`VideoMaker` Class**:
   - Initializes the video output, loads the necessary viseme images, and generates a video where each viseme is displayed for the corresponding duration from the JSON file.
   - The generated video is synchronized with the viseme data, ensuring the video matches the spoken audio.

3. **Audio and Video Combination**:
   - After the video is generated from viseme images, the audio is added to the video using `moviepy` to create a final lip-sync video.
   - If the audio duration exceeds the video duration, the audio is clipped to fit the video length.

### Key Functions in the `VideoMaker` Class:

1. **`__init__(self, images_dir, visemes_dir, audio_dir, out_dir, fps, map_file)`**:
   - Initializes the `VideoMaker` class with directories for viseme images, metadata (viseme data), audio files, and the output video.
   - It also sets the frame rate (`fps`) for the video.

2. **`generate_video(self, in_file)`**:
   - Generates a video from viseme images based on the viseme data in a JSON file. The video frames are created by mapping viseme IDs to images, which are displayed for a duration specified in the viseme data.

3. **`add_audio(self, audio_file, video_file)`**:
   - Adds an audio file to the generated video. It adjusts the duration of the audio or video as needed to ensure they match and then outputs the final video with synchronized audio and visuals.

4. **`viseme_callback(event)`**:
   - A callback function that is triggered when visemes are received during audio synthesis. It collects viseme data (ID and offset) to be used for video generation.

### How to Use:

1. **Set Up the Required Libraries**:
   Ensure the following Python libraries are installed:
   ```bash
   pip install azure-cognitiveservices-speech moviepy opencv-python numpy argparse
"""

class VideoMaker:
    def __init__(self, images_dir, visemes_dir, audio_dir, out_dir, fps, map_file):
        self.fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.height, self.width = self.get_im_dims(images_dir)
        self.im_dir = images_dir
        self.metadata_dir = visemes_dir
        self.audio_dir = audio_dir
        self.out_dir = out_dir
        self.fps = 1 / (duration / 1000)
        self.duration = 0
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
        return chunk["id"], duration

    def make_frame(self, id):
        print(f"Generating frame for viseme id {id}.")
        frame = cv2.imread(os.path.join(self.im_dir, f"viseme-id-{id}.jpg"))
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        return cv2.resize(frame, (self.width, self.height))

    def frame_to_video(self, output, frame, dur):
        for i in range(int(np.round(dur / 1000 * self.fps, 0))):
            output.write(frame)

    def generate_video(self, in_file):
        in_path = os.path.join(self.metadata_dir, in_file)
        self.out_path = os.path.join(self.out_dir, f'{in_file.strip(".json")}_{self.fps}.mp4')
        print(f"Generating video from {self.out_path}.")
        output = self.get_out(self.out_path)
        data = self.load_json("metadata/24.json")
        print(len(data))
        viseme_dur = 0
        for chunk in data:
            mapped, dur = self.read_chunk_data(chunk)
            print(f"Viseme id {mapped} has duration {dur} milliseconds.")
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
        final_clip.write_videofile(f'video/2.mp4', codec="libx264", audio_codec="aac")

        final_video = video_clip.set_audio(audio_clip)
        print(f"Successfully generated video of {final_video.end} milliseconds from video and audio streams.")
        video_out_path = f'video/2{os.path.basename(self.im_dir)}_with_audio_{video_file.strip(".json").strip("video/")}'
        # final_video.write_videofile(video_out_path, fps=self.fps)
        final_video.write_videofile(video_out_path, fps=self.fps, audio_codec="aac")

        print(f"Video successfully saved to {video_out_path}.")


def generate():
    parser = argparse.ArgumentParser(
        description="Specify metadata, audio, image and output directories, and viseme mapping file."
    )
    parser.add_argument("--im_dir", type=str, default="image/mouth", help="Directory with viseme images.")
    parser.add_argument(
        "--metadata_dir", type=str, default="metadata", help="Directory containing viseme metadata .json files."
    )
    parser.add_argument("--audio_dir", type=str, default="audio", help="Directory containing .wav audio files.")
    parser.add_argument("--out_dir", type=str, default="video", help="Directory to save generated video.")
    parser.add_argument("--fps", type=int, default=50, help="Frame rate (in frames per second) to generate video.")
    parser.add_argument("--map", type=str, default="map/viseme_map.json", help="Path to viseme mapping file.")
    parser.add_argument("--no_audio", action="store_true", help="Generated video without audio.")
    args = parser.parse_args()
    viseme_video_maker = VideoMaker(args.im_dir, args.metadata_dir, args.audio_dir, args.out_dir, args.fps, args.map)

    for in_file in os.listdir(args.metadata_dir):
        if ".json" not in in_file:
            continue
        else:
            viseme_video_maker.generate_video(in_file)
            print(f"Generated video from {in_file}.")
            if args.no_audio is not True:
                viseme_video_maker.add_audio(f'audio/24.wav', viseme_video_maker.out_path)
                # combine_audio_video(audio_file_path_new, video_file_path_new, output_file_path_new)


def combine_audio_video(audio_file_path, video_file_path, output_file_path):
    audio_clip = AudioFileClip(audio_file_path)
    video_clip = VideoFileClip(video_file_path)
    final_clip = video_clip.set_audio(audio_clip)
    final_clip.write_videofile(output_file_path, codec="libx264", audio_codec="aac")
    print("Done")

# Update these paths according to your files' locations
audio_file_path_new = '/audio/24.wav'  # e.g., 'C:/Users/user/Music/myaudio.wav'
video_file_path_new = '/video/video.mp4'  # e.g., 'C:/Users/user/Videos/myvideo.mp4'
output_file_path_new = '/video/output_video.mp4'  # e.g., 'C:/Users/user/Desktop/MyVideos/output_video.mp4'

speech_key = "YOUR-KEY-HERE"
service_region = "westus2"

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"

input_text = input("")

speech_config_text = """
    <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
        <voice name="en-US-EmmaNeural">
            <mstts:viseme type="redlips_front"/>
            <mstts:express-as style="excited">
            <prosody rate="-8%">
                {}
            </prosody>
            </mstts:express-as>
        </voice>
    </speak>"""

ssml = speech_config_text.format(input_text)


file_name = "audio/24.wav"
file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)

viseme_data = []


def viseme_callback(event):
    print(event)
    viseme_data.append({"offset": event.audio_offset / 10000, "id": event.viseme_id})


speech_synthesizer.viseme_received.connect(viseme_callback)

result = speech_synthesizer.speak_ssml_async(ssml=ssml).get()

if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    with open("metadata/24.json", "w") as f:
        json.dump(viseme_data, f, indent=4)
        print("Done generating Viseme")
       
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print("Error details: {}".format(cancellation_details.error_details))

generate()