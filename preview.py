from moviepy.editor import VideoFileClip

# Replace 'path_to_video.mp4' with the path to your video file
video_path = 'video/2.mp4'

# Load the video file
clip = VideoFileClip(video_path)

# Play the video file
clip.preview()