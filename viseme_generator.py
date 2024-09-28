import azure.cognitiveservices.speech as speechsdk
import json
from video_generator import VideoMaker
import argparse
import os


"""
This script integrates Azure Cognitive Services' Text-to-Speech (TTS) API with a custom video generation system to produce lip-synced videos using viseme (mouth shape) data. It allows for dynamic voice selection and video creation based on different modes (e.g., "beff-mode", "jigar-mode"). The `GenerateVideoAndAudio` class is the core component that handles both audio generation (from text) and video creation, synchronizing them using viseme data.

### Key Components:

1. **Azure Cognitive Services TTS Integration**:
   - The script uses Azure's Text-to-Speech service to convert input text into speech and generate viseme data, which maps phonemes (speech sounds) to mouth shapes.
   - The viseme data is saved in a JSON file (`metadata/text_to_viseme.json`) and is used to create a synchronized video of mouth movements.

2. **`GenerateVideoAndAudio` Class**:
   - Handles the generation of both audio and video. It takes a callback function and a mode as parameters to control behavior dynamically.
   - The class configures the Azure TTS engine, generates audio from text using SSML (Speech Synthesis Markup Language), and captures the viseme data during speech synthesis.
   - Different modes like "beff-mode", "jigar-mode", and "mickey-mode" change the voice actor and style used in speech synthesis.

3. **Video Generation**:
   - After generating audio and viseme data, the script uses the `VideoMaker` class (from the `video_generator` module) to produce a video based on the viseme images and timing.
   - The video can be combined with the generated audio to create a complete lip-synced video.

### Key Functions in the `GenerateVideoAndAudio` Class:

1. **`__init__(self, callback, mode)`**:
   - Initializes the class with a callback function (e.g., for playing videos) and sets the mode for voice generation.

2. **`generateViseme(self, text)`**:
   - Converts the input text to speech using Azure's TTS API and captures viseme data (mouth movements).
   - The speech is synthesized according to the selected mode (which controls voice and style).
   - After generating the viseme data, it calls `generateVideo()` to create the video.

3. **`generateVideo(self)`**:
   - Uses the `VideoMaker` class to generate a video based on the viseme data.
   - The video is created by displaying the appropriate viseme image (mouth shape) for the corresponding duration, synchronized with the audio.

4. **`set_mode(self, new_mode)`**:
   - Updates the mode used for generating the voice and video, allowing the behavior of the class to be changed dynamically.

### How to Use:

1. **Set Up the Required Libraries**:
   Ensure you have the required Python libraries installed:
   ```bash
   pip install azure-cognitiveservices-speech moviepy opencv-python argparse
"""


class GenerateVideoAndAudio:
    def __init__(self, callback, mode):
        self.callback = callback
        self.mode = mode

    speech_key = "YOUR-SPEECH-KEY"
    service_region = "westus2"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = "en-US-BrianNeural"

    duration = 95
    fps = 1 / (duration / 1000)

    def set_mode(self, new_mode):
        self.mode = new_mode


    speech_config_text = """
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="{}">
                <mstts:viseme type="redlips_front"/>
                <mstts:express-as style="{}">
                    {}
                </mstts:express-as>
            </voice>
        </speak>"""

    def generateViseme(self, text):
        print("Viseme Generate():")
        print(self.mode)
        # ssml = self.speech_config_txt
        voice_actor = "en-US-EmmaNeural"
        style = "default"
        rate = ""
        # text = "Hi, I'm your default virtual assistant"

        if self.mode == "beff-mode":
            voice_actor = "en-US-BrianNeural"
            # text = "Hey There, I'll be your new Virtual Assistant!"

        elif self.mode == "jigar-mode":
            voice_actor = "en-US-BrandonNeural"
            # text = "Hi, my name is Jigar, I'll be your custom Virtual Assistant"

        elif self.mode == "sarayu-mode":
            voice_actor = "en-US-SaraNeural"
            # text = "Hi, my name is Sarayu, I'll be your Virtual Assistant"
            style = "cheerful"

        elif self.mode == "mickey-mode":
            voice_actor = "en-US-DavisNeural"
            # text = """I AM HULK, Hulk SMASH,<break time="1500ms"/> Hulk is strongest there is"""
            style = "shouting"
            rate = """ "rate="slow" pitch="-20%" """
            #regular
        # text = """<prosody volume="x-loud">Why does Waldo always wear stripes?<break time="1500ms"/><mark name="punchline"/>Because he doesn&apos;t want to be spotted.</prosody>"""
        ssml = self.speech_config_text.format(voice_actor, style, text)

        print("\n")
        print(text)
        print("\n")

        file_name = "audio/text_to_audio.wav"
        file_config = speechsdk.audio.AudioOutputConfig(filename=file_name)

        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=file_config)

        viseme_data = []

        def viseme_callback(event):
            print(event)
            viseme_data.append({"offset": event.audio_offset / 10000, "id": event.viseme_id})


        speech_synthesizer.viseme_received.connect(viseme_callback)

        result = speech_synthesizer.speak_ssml_async(ssml=ssml).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            with open("metadata/text_to_viseme.json", "w") as f:
                json.dump(viseme_data, f, indent=4)
            
            self.generateVideo()
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))


    def generateVideo(self):
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
        viseme_video_maker = VideoMaker(args.im_dir, args.metadata_dir, args.audio_dir, args.out_dir, args.fps, args.map, self.callback, self.mode)

        for in_file in os.listdir(args.metadata_dir):
            if ".json" not in in_file:
                continue
            else:
                viseme_video_maker.generate_video(in_file)
                print(f"Generated video from {in_file}.")
                if viseme_video_maker.mode == "regular-mode":
                    if args.no_audio is not True:
                        viseme_video_maker.add_audio(f'audio/text_to_audio.wav', viseme_video_maker.out_path)