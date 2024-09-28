# LipSync Video Generation Project

## Overview

This project is a comprehensive system that uses Azure's Text-to-Speech (TTS) API and viseme data to generate synchronized lip-sync videos. The system takes input text, converts it into speech, extracts viseme data (mouth shapes corresponding to the phonemes in the speech), and generates a video of lip movements that sync with the audio. The project supports multiple modes for generating custom videos with different virtual assistants and styles.

This is a cool project to start to build your AI assistant. All you need is 1 image, 1 minute voice recording and connect to any LLM. This will respond with lip-syncing and with the same voice. For lip-syncing you can use WAV2LIP and for viseme generation you can use Azure, and for audio generation same, you can use Azure Voice Studios. Good luck :) 

## Disclaimer
This project is provided "as-is" without any warranty of any kind. The author assumes no responsibility for any outcomes, losses, or damages that may arise from the use of this project. Any similarities to real persons, living or dead, or actual events are purely coincidental. The virtual assistant characters and styles in this project are fictional and should not be interpreted as imitating any real individuals or copyrighted characters.

### Key Features
- **Speech Synthesis**: Converts input text to speech using Azure TTS, generating viseme data for lip-sync animation.
- **Viseme Data Handling**: Uses viseme images and JSON metadata to create videos synchronized with the audio.
- **Multiple Modes**: Supports different virtual assistant styles ("beff-mode", "Hulk-mode", etc.) with customizable voice and visual settings.
- **Audio-Video Merging**: Combines audio and video to create a final output using `moviepy`.
- **PyQt5 Video Player**: Allows for video playback in a GUI using PyQt5 for real-time viewing.

---

## Requirements

To run this project, you need to install the following Python libraries:

```bash
pip install azure-cognitiveservices-speech moviepy opencv-python numpy argparse PyQt5
```

Additionally, you need to set up your **Azure Speech API key** and **service region** for text-to-speech synthesis.
Check this out for more info: https://learn.microsoft.com/en-us/answers/questions/1182640/visemes-to-control-the-movement-of-2d-and-3d-chara

---

## Project Structure

### Classes

#### 1. `GenerateVideoAndAudio`

This class handles text-to-speech conversion, viseme generation, and video creation.

- **Constructor**: Takes a `callback` function and a `mode` that determines the virtual assistant's style and behavior.
- **Key Methods**:
  - `generateViseme(text)`: Converts input text to speech using Azure's TTS API, generates viseme data (mouth movements), and stores the data in JSON format.
  - `generateVideo()`: Uses the generated viseme data to create a video by syncing viseme images with the audio.
  - `set_mode(new_mode)`: Updates the mode, changing the voice and style for the virtual assistant.

#### 2. `VideoMaker`

This class is responsible for creating the video from viseme data and combining it with audio.

- **Constructor**: Initializes with directories for images, viseme metadata, audio, and the output folder. It also sets the frame rate (FPS) and mode.
- **Key Methods**:
  - `generate_video(in_file)`: Generates a video by loading viseme data and corresponding images, arranging them based on timing, and creating frames.
  - `add_audio(audio_file, video_file)`: Combines the generated video with audio to create a synchronized lip-sync video.
  - `make_frame(id)`: Loads, rotates, and resizes the viseme image corresponding to a given ID.

#### 3. `LipSync`

A helper class for custom video modes like "beff-mode" or "Hulk-mode." It generates videos for specific virtual assistant characters.

- **Constructor**: Takes the character name as input.
- **generateVideo()**: Generates the video for the given character using pre-configured settings.

#### 4. `VideoApplication`

A PyQt5 application class for video playback in a GUI environment.

- **Key Method**:
  - `play_video(path)`: Plays a video at the given path, allowing for real-time playback in the GUI.

---

## Modes

The project supports multiple modes that change the virtual assistant's behavior:

- **beff-mode**: Uses a custom virtual assistant with a predefined voice and style (e.g., `en-US-BrianNeural`).
- **Hulk-mode**: Features a custom "Hulk" virtual assistant, with the `en-US-DavisNeural` voice and a "shouting" style.
- **jigar-mode**: Another custom assistant using `en-US-BrandonNeural`.
- **sarayu-mode**: A cheerful assistant using `en-US-SaraNeural`.

Each mode alters the voice, text style, and video generation process. You can switch between modes dynamically using the `set_mode()` method.

---

## How to Use the Project

### 1. **Azure Setup**

- Sign up for Azure and get your **Speech API Key** and **Service Region** from the Azure portal.
- Replace `"YOUR-SPEECH-KEY"` in the code with your actual API key.
- Set the correct **service region** in the `GenerateVideoAndAudio` class.

### 2. **Prepare Input Files**

- **Viseme Images**: Place viseme images (e.g., `viseme-id-1.jpg`, `viseme-id-2.jpg`) in the `image/mouth` directory.
- **Audio File**: Place the audio file (e.g., `text_to_audio.wav`) in the `audio` directory.
- **Viseme Metadata**: Place the viseme metadata JSON file in the `metadata` directory (generated by Azure TTS).

### 3. **Run the Script**

You can run the script with the following command:

```bash
python script.py --im_dir image/mouth --metadata_dir metadata --audio_dir audio --out_dir video --fps 60
```

This will:

- Generate a video using the viseme data and images.
- Combine the video with the corresponding audio to create a synchronized lip-sync video.

### 4. **Switching Modes**

To change the virtual assistant mode, update the mode by calling `set_mode(new_mode)` in the `GenerateVideoAndAudio` class. Available modes are:

- `"beff-mode"` aka El-Jeffe Mode
- `"Hulk-mode"`
- `"jigar-mode"`
- `"sarayu-mode"`

Example usage:

```python
generate_video_and_audio = GenerateVideoAndAudio(callback_function, "beff-mode")
generate_video_and_audio.generateViseme("Hello, I am your virtual assistant.")
```

### 5. **Combining Audio and Video**

The script automatically combines audio and video, but if you need to do this manually, you can use the `combine_audio_video()` function:

```python
combine_audio_video('/audio/text_to_audio.wav', '/video/video.mp4', '/video/output_video.mp4')
```

---

## Example Commands

### Generate a Video

```bash
python script.py --im_dir image/mouth --metadata_dir metadata --audio_dir audio --out_dir video --fps 60
```

### Custom Mode

```python
generate_video_and_audio = GenerateVideoAndAudio(callback_function, "beff-mode")
generate_video_and_audio.generateViseme("This is a custom virtual assistant.")
```

### Generate Video without Audio

```bash
python script.py --im_dir image/mouth --metadata_dir metadata --audio_dir audio --out_dir video --fps 60 --no_audio
```

---

## Future Extensions

- **Real-time Lip Sync**: Implement real-time audio and viseme generation for live video creation.
- **Additional Modes**: Add more custom modes for different virtual assistant personalities and voices.
- **Advanced GUI**: Enhance the PyQt5 video player for more interactive control over video playback and lip-sync testing.

---

## Conclusion

This project provides a flexible and powerful system for generating lip-sync videos from input text using Azure TTS. It supports customizable virtual assistants, real-time video playback, and dynamic mode switching. By integrating audio and video seamlessly, it delivers highly synchronized lip-sync content. You can further extend this project by adding more modes, improving the GUI, or integrating more advanced video processing features.
```