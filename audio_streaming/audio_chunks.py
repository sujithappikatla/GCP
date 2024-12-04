import pyaudio
import numpy as np

# Audio configuration
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1               # Mono audio
RATE = 16000               # Sample rate
CHUNK = int(RATE / 10)  # 100ms

# Initialize PyAudio
p = pyaudio.PyAudio()

# Define the callback function
def callback(in_data, frame_count, time_info, status):
    # Process the incoming audio data (in_data)
    audio_data = np.frombuffer(in_data, dtype=np.int16)
    
    # Here you can process the audio_data as needed
    print("Received audio data:", audio_data)

    return (in_data, pyaudio.paContinue)  # Return the data and continue the stream

# Open the stream with the callback function
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                stream_callback=callback)

print("Recording...")

try:
    # Keep the stream active for a specified duration or until interrupted
    while True:
        pass  # You can add any other logic here if needed
except KeyboardInterrupt:
    print("Stopped recording.")

# Stop and close the stream
stream.stop_stream()
stream.close()
p.terminate()