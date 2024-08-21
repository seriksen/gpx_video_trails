from dash import dcc, html, Dash
from dash.dependencies import Input, Output, State
import pandas as pd
import gpxpy
import gpxpy.gpx

# Load and parse the GPX file
with open('example.gpx', 'r') as gpx_file:
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
                'speed': point.speed  # Speed might need to be calculated manually
            })

df = pd.DataFrame(points)

# Set up Dash
app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='map', style={'height': '500px'}),
    dcc.Input(id='duration', type='number', placeholder='Duration in minutes', value=5),
    dcc.Slider(
        id='time-slider',
        min=0,
        max=len(df) - 1,
        value=0,
        step=1,
        updatemode='drag'  # Update continuously while dragging
    ),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0),  # Update every second
    html.Button('Save GPX', id='save-gpx-button', n_clicks=0)
])


@app.callback(
    Output('time-slider', 'max'),
    Output('time-slider', 'value'),
    [Input('duration', 'value')]
)
def update_slider(duration):
    return len(df) - 1, 0


@app.callback(
    Output('map', 'figure'),
    [Input('time-slider', 'value'),
     Input('duration', 'value')]
)
def update_map(start_idx, duration):
    if duration is None or duration <= 0:
        duration = (df['time'].iloc[-1] - df['time'].iloc[0]).total_seconds() / 60  # Full duration in minutes

    end_time = df['time'].iloc[start_idx] + pd.Timedelta(minutes=duration)
    end_idx = df.index[df['time'] <= end_time].tolist()[-1]
    filtered_df = df.iloc[start_idx:end_idx]

    # Handle empty DataFrame case
    if filtered_df.empty:
        return {
            'data': [],
            'layout': {
                'mapbox': {'style': "open-street-map"},
                'margin': {'r': 0, 't': 0, 'l': 0, 'b': 0}
            }
        }

    start_point = filtered_df.iloc[0]
    end_point = filtered_df.iloc[-1]

    markers = [
        {
            'type': 'scattermapbox',
            'lat': [start_point['latitude']],
            'lon': [start_point['longitude']],
            'mode': 'markers',
            'marker': {'size': 10, 'color': 'green'},
            'text': ['Start Point']
        },
        {
            'type': 'scattermapbox',
            'lat': [end_point['latitude']],
            'lon': [end_point['longitude']],
            'mode': 'markers',
            'marker': {'size': 10, 'color': 'red'},
            'text': ['End Point']
        },
        {
            'type': 'scattermapbox',
            'lat': filtered_df['latitude'].tolist(),
            'lon': filtered_df['longitude'].tolist(),
            'mode': 'lines',
            'line': {'color': 'blue'}
        }
    ]

    # Calculate the bounding box
    min_lat = filtered_df['latitude'].min()
    max_lat = filtered_df['latitude'].max()
    min_lon = filtered_df['longitude'].min()
    max_lon = filtered_df['longitude'].max()

    return {
        'data': markers,
        'layout': {
            'mapbox': {
                'style': "open-street-map",
                'center': {
                    'lat': (min_lat + max_lat) / 2,
                    'lon': (min_lon + max_lon) / 2
                },
                'zoom': 13,
                'bounds': [[min_lat, min_lon], [max_lat, max_lon]]
            },
            'margin': {'r': 0, 't': 0, 'l': 0, 'b': 0}
        }
    }


@app.callback(
    Output('save-gpx-button', 'children'),
    [Input('save-gpx-button', 'n_clicks')],
    [State('time-slider', 'value'),
     State('duration', 'value')]
)
def save_gpx(n_clicks, start_idx, duration):
    if n_clicks > 0:
        if duration is None or duration <= 0:
            duration = (df['time'].iloc[-1] - df['time'].iloc[0]).total_seconds() / 60  # Full duration in minutes

        end_time = df['time'].iloc[start_idx] + pd.Timedelta(minutes=duration)
        end_idx = df.index[df['time'] <= end_time].tolist()[-1]
        filtered_df = df.iloc[start_idx:end_idx]

        # Create a new GPX file
        new_gpx = gpxpy.gpx.GPX()
        new_track = gpxpy.gpx.GPXTrack()
        new_gpx.tracks.append(new_track)
        new_segment = gpxpy.gpx.GPXTrackSegment()
        new_track.segments.append(new_segment)

        for _, row in filtered_df.iterrows():
            new_point = gpxpy.gpx.GPXTrackPoint(
                latitude=row['latitude'],
                longitude=row['longitude'],
                elevation=row['elevation'],
                time=row['time']
            )
            new_segment.points.append(new_point)

        with open('subsection.gpx', 'w') as f:
            f.write(new_gpx.to_xml())

        return 'GPX Saved!'
    return 'Save GPX'


if __name__ == '__main__':
    app.run_server(debug=True)