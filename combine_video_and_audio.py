import ffmpeg

"""
This function provides a simple utility to combine a video file and an audio file into a single output video with synchronized audio using the `ffmpeg` library.

### Key Function:
1. `combine_video_audio(video_file, audio_file, output_file)`:
   - Takes in a video file and an audio file as input.
   - Uses `ffmpeg` to merge the audio into the video, ensuring both video and audio are synchronized.
   - Outputs the result to the specified output file path.

### How to Use:
1. Install the `ffmpeg` library using the following command:
   ```bash
   pip install ffmpeg-python
"""

def combine_video_audio(video_file, audio_file, output_file):
    input_video = ffmpeg.input(video_file)
    input_audio = ffmpeg.input(audio_file)
    ffmpeg.concat(input_video, input_audio, v=1, a=1).output(output_file).run()

# Paths to your video and audio files
video_file = "./video/video_input.mp4"
audio_file = "./audio/audio_input.wav"
output_file = "combined.mp4"

# Combine video and audio
combine_video_audio(video_file, audio_file, output_file)