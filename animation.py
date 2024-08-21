import pandas as pd
import plotly.express as px
import gpxpy
import numpy as np
import plotly.io as pio

# Load and parse the GPX file
with open('subsection.gpx', 'r') as gpx_file:
    gpx = gpxpy.parse(gpx_file)

# Extract data from GPX
points = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            points.append({
                'latitude': point.latitude,
                'longitude': point.longitude,
                'elevation': point.elevation,
                'time': point.time,
                'speed': point.speed if point.speed is not None else 0  # Handle missing speed
            })

df = pd.DataFrame(points)

# Ensure 'speed' is numeric
df['speed'] = pd.to_numeric(df['speed'], errors='coerce').fillna(0)

# Interpolate points for smooth animation
def interpolate_points(df, num_interpolated_points=10):
    interpolated_points = []
    for i in range(len(df) - 1):
        start_point = df.iloc[i]
        end_point = df.iloc[i + 1]
        for j in range(num_interpolated_points):
            fraction = j / num_interpolated_points
            interpolated_points.append({
                'latitude': start_point['latitude'] + fraction * (end_point['latitude'] - start_point['latitude']),
                'longitude': start_point['longitude'] + fraction * (end_point['longitude'] - start_point['longitude']),
                'elevation': start_point['elevation'] + fraction * (end_point['elevation'] - start_point['elevation']),
                'time': start_point['time'] + fraction * (end_point['time'] - start_point['time']),
                'speed': start_point['speed'] + fraction * (end_point['speed'] - start_point['speed'])
            })
    interpolated_points.append(df.iloc[-1].to_dict())  # Add the last point
    return pd.DataFrame(interpolated_points)

# Interpolate the points
df_interpolated = interpolate_points(df)

# Add an index column for animation frame
df_interpolated['frame'] = df_interpolated.index

# Calculate total duration in seconds
total_duration = (df_interpolated['time'].max() - df_interpolated['time'].min()).total_seconds()

# Calculate frame duration in milliseconds
frame_duration = total_duration / len(df_interpolated) * 1000

# Print DataFrame for debugging
print(df_interpolated.head())
print(f"Total Duration: {total_duration} seconds")
print(f"Frame Duration: {frame_duration} milliseconds")

# Create animated layer for the frame-by-frame animation
fig = px.scatter_mapbox(
    df_interpolated,
    lat='latitude',
    lon='longitude',
    color_discrete_sequence=['black'],  # Use black color for the animated layer
    size_max=10,
    animation_frame='frame',
    mapbox_style="open-street-map",
    center={'lat': df_interpolated['latitude'].mean(), 'lon': df_interpolated['longitude'].mean()},
    zoom=13
)

# Update layout for smooth animation
fig.update_traces(mode='lines+markers', line={'width': 4})  # Connect the points with wider lines
fig.update_layout(
    updatemenus=[{
        'buttons': [
            {
                'args': [None, {'frame': {'duration': frame_duration, 'redraw': True}, 'fromcurrent': True}],
                'label': 'Play',
                'method': 'animate'
            },
            {
                'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate', 'transition': {'duration': 0}}],
                'label': 'Pause',
                'method': 'animate'
            }
        ],
        'direction': 'left',
        'pad': {'r': 10, 't': 87},
        'showactive': False,
        'type': 'buttons',
        'x': 0.1,
        'xanchor': 'right',
        'y': 0,
        'yanchor': 'top'
    }]
)

# Save the animation as an HTML file
pio.write_html(fig, file='gpx_animation.html', auto_open=True)

# Save the animation as an MP4 file
pio.write_image(fig, file='gpx_animation.mp4', format='mp4')