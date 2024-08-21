import gpxpy
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.interpolate import CubicSpline
from tqdm import tqdm
from datetime import datetime
import sys

# Load the GPX file
with open('subsection.gpx', 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)

# Extract coordinates and times
points = [(point.latitude, point.longitude, point.time) for track in gpx.tracks for segment in track.segments for point
          in segment.points]
latitudes, longitudes, times = zip(*points)

# Convert times to seconds since epoch
times = [datetime.fromisoformat(t.isoformat()).timestamp() for t in times]
total_duration = times[-1] - times[0]

# Define frame rate (frames per second)
fps = 30

# Optionally interpolate/smooth the data
if len(latitudes) > 2:
    # Cubic Spline interpolation for smoother path
    cs_lat = CubicSpline(np.arange(len(latitudes)), latitudes)
    cs_lon = CubicSpline(np.arange(len(longitudes)), longitudes)

    new_indices = np.linspace(0, len(latitudes) - 1, num=int(total_duration * fps))  # Adjust factor as needed
    latitudes = cs_lat(new_indices)
    longitudes = cs_lon(new_indices)
else:
    # Handle very few points gracefully
    new_indices = np.arange(len(latitudes))
    latitudes, longitudes = np.array(latitudes), np.array(longitudes)

# Calculate number of frames and interval
num_frames = int(fps * total_duration)
interval = 1000 / fps  # Interval in milliseconds

# Create a Matplotlib figure with high resolution
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)  # Adjust size and DPI for higher resolution
fig.patch.set_alpha(0)  # Make the figure background transparent
ax.patch.set_alpha(0)  # Make the axis background transparent
ax.plot(longitudes, latitudes, color='lightgray')  # Plot the full path in light gray

black_line, = ax.plot([], [], color='black')  # Initialize the black line

# Hide axes
ax.axis('off')


# Animation update function
def update(num):
    black_line.set_data(longitudes[:num], latitudes[:num])
    return black_line,

frames = tqdm(range(num_frames), desc='Rendering Frames')

anim = animation.FuncAnimation(fig, update, frames=frames, interval=interval, blit=True)

# Save the animation as MP4 with transparent background
writer = animation.FFMpegWriter(fps=fps, metadata=dict(artist='Me'),
                                extra_args=['-vf', 'format=rgba'])  # Use '-vf format=rgba' for transparency
anim.save('gpx_animation.mp4', writer=writer, savefig_kwargs={'transparent': True})