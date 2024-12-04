import os
os.environ['GRPC_PYTHON_LOG_LEVEL'] = '5'  # Add this line before other imports
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./stt-service-account.json"


import pyaudio
from google.cloud import speech
import queue

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# Create a queue to communicate between the audio callback and main thread
audio_queue = queue.Queue()

def audio_callback(in_data, frame_count, time_info, status_flags):
    """Callback function to capture audio from the microphone."""
    audio_queue.put(in_data)
    return (None, pyaudio.paContinue)

def get_streaming_audio():
    """Generator that yields audio chunks from the queue."""
    while True:
        data = audio_queue.get()
        if data is None:
            break
        yield data

def main():
    # Initialize the Speech client
    client = speech.SpeechClient()

    # Configure recognition parameters
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="en-US",
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,  # To get results as you speak
    )

    # Start the audio stream
    audio_interface = pyaudio.PyAudio()
    audio_stream = audio_interface.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        stream_callback=audio_callback,
    )

    print("Listening... Speak into your microphone.")

    try:
        audio_stream.start_stream()

        audio_generator = get_streaming_audio()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=chunk)
            for chunk in audio_generator
        )

        responses = client.streaming_recognize(config=streaming_config, requests=requests)

        # Process the responses
        for response in responses:
            if not response.results:
                continue

            # Only show the first result, as we are interested in real-time output
            result = response.results[0]
            if result.is_final:
                print(f"Final: {result.alternatives[0].transcript}")
            else:
                print(f"Interim: {result.alternatives[0].transcript}", end="\r")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Stop and close the audio stream
        audio_stream.stop_stream()
        audio_stream.close()
        audio_interface.terminate()

if __name__ == "__main__":
    main()