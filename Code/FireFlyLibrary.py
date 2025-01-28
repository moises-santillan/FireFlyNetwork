import cv2
import numpy as np
from scipy.signal import find_peaks

def threshold(x, thr):
    res = (x*0).astype(int)
    idx = np.where(x > thr)[0]
    res[idx] = 1
    return res


def find_led_coordinates(video_path, n_leds):
    video = cv2.VideoCapture(video_path)

    # Initialize variables
    frame_count = 0
    average_frame = None

    # Process the first 100 frames
    while frame_count < 120:
        # Read the next frame
        ret, frame = video.read()

        if not ret:
            break

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to isolate the brightest spots
        _, thresholded = cv2.threshold(gray.astype(np.uint8), 250, 255, cv2.THRESH_BINARY)


        # Accumulate the frames
        if average_frame is None:
            average_frame = np.zeros_like(thresholded, dtype=np.float32)

        average_frame += thresholded.astype(np.float32)
        frame_count += 1

    # Calculate the average frame
    #average_frame /= frame_count

    # Apply thresholding to isolate the brightest spots
    _, thresholded = cv2.threshold(average_frame.astype(np.uint8), 1, 255, cv2.THRESH_BINARY)
    

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the two largest contours (assuming they correspond to the LEDs)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:n_leds]

    # Initialize LED coordinates
    led_coordinates = []

    # Process each contour
    for contour in contours:
        # Find the centroid of the contour
        moments = cv2.moments(contour)
        cX = int(moments["m10"] / moments["m00"])
        cY = int(moments["m01"] / moments["m00"])
        # Store the coordinates of the LEDs
        led_coordinates.append((cY, cX))

    # Release the video capture
    video.release()
    
    led_coordinates = sorted(led_coordinates, key=lambda coord: (coord[1], coord[0]))

    return led_coordinates

def get_time_series(video_path, led_coordinates):
    n_leds = len(led_coordinates)
    cap = cv2.VideoCapture(video_path)
    led_state = []
    timestamps = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        #Image = frame[:, :, 2]  # Extract the red channel
        Image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
        gato = [None] * n_leds
        for i in range(n_leds):
            gato[i] = Image[led_coordinates[i]]/255
        led_state.append(gato)
        timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
    cap.release()
    led_state = np.array(led_state)
    for i in range(n_leds):
        sgnl = led_state[:, i]
        peaks = sgnl[find_peaks(sgnl)[0]]
        thr = np.mean(peaks)
        led_state[:, i] = threshold(sgnl, thr)

    return timestamps, led_state
    
    
    def phase_response(timeseries):
    # Extract kicks and state changes
    kicks = timeseries[np.where(np.diff(timeseries[:, 1]) == 1)[0] + 1, 0] + 0.0874
    state_changes = timeseries[np.where(np.diff(timeseries[:, 2]) != 0)[0] + 1, 0]

    on_intervals = []
    off_intervals = []

    for i in range(1, len(state_changes) - 1):
        if not np.any((kicks > state_changes[i]) & (kicks < state_changes[i + 1])):
            duration = state_changes[i + 1] - state_changes[i]
            if timeseries[np.where(np.diff(timeseries[:, 2]) != 0)[0] + 1, 2][i] == 0:
                off_intervals.append(duration)
            else:
                on_intervals.append(duration)

    mean_ON = np.mean(on_intervals) if on_intervals else 0
    mean_OFF = np.mean(off_intervals) if off_intervals else 0
    
    old_phase = []
    new_phase = []

    for i in range(1, len(state_changes) - 2):
        if np.any((kicks > state_changes[i]) & (kicks < state_changes[i + 1])):
            kick_time = kicks[np.where((kicks > state_changes[i]) & (kicks < state_changes[i + 1]))[0][0]]
            if timeseries[np.where(np.diff(timeseries[:, 2]) != 0)[0] + 1, 2][i] == 1:
                old_phase_value = 0.5 + (kick_time - state_changes[i]) / (mean_ON * 2)
                new_phase_value = old_phase_value - ((state_changes[i + 1] - state_changes[i]) / mean_ON - 1) / 2
            else:
                old_phase_value = (kick_time - state_changes[i]) / (mean_OFF * 2)
                new_phase_value = old_phase_value - ((state_changes[i + 1] - state_changes[i]) / mean_OFF - 1) / 2
            
            old_phase.append(old_phase_value)
            new_phase.append(new_phase_value)

    return np.array(old_phase), np.array(new_phase)
