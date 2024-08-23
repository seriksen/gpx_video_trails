import moviepy.editor as mp
import ipywidgets as widgets
from IPython.display import display

# Load the MP4 file
video = mp.VideoFileClip("GX010400/example.mp4")

# Create sliders for start and end times
start_slider = widgets.FloatSlider(min=0, max=video.duration, step=0.1, description='Start Time')
end_slider = widgets.FloatSlider(min=0, max=video.duration, step=0.1, description='End Time')

# Function to update the end slider's minimum value based on the start slider's value
def update_end_slider(*args):
    end_slider.min = start_slider.value

start_slider.observe(update_end_slider, 'value')

# Display the sliders
display(start_slider, end_slider)

# Button to crop and save the video
save_button = widgets.Button(description="Save Cropped Video")

# Function to crop and save the video
def save_cropped_video(b):
    start_time = start_slider.value
    end_time = end_slider.value
    cropped_video = video.subclip(start_time, end_time)
    cropped_video.write_videofile(
        "cropped_output.mp4",
        codec="libx264",
        fps=video.fps,
        preset="ultrafast",  # Optional: Adjust encoding speed/quality tradeoff
        ffmpeg_params=["-vf", f"scale={video.size[0]}:{video.size[1]}"]  # Preserve resolution
    )
    print(f"Cropped video length: {end_time - start_time} seconds")

save_button.on_click(save_cropped_video)

# Display the save button
display(save_button)