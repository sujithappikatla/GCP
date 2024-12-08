import pyaudio
import websocket
import threading
import ssl

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# WebSocket configuration
WS_URL = "ws://localhost:8765"
# WS_URL = "wss://speech-to-text-server-305533803718.us-west1.run.app"

def on_message(ws, message):
    print("Received message: ", message)

def on_error(ws, error):
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_open(ws):
    print("WebSocket connection opened")

    def audio_stream():
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("Starting audio stream...")

        try:
            while True:
                audio_data = stream.read(CHUNK)
                ws.send(audio_data, opcode=websocket.ABNF.OPCODE_BINARY)
        except KeyboardInterrupt:
            print("Stopping audio stream...")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            ws.close()

    audio_thread = threading.Thread(target=audio_stream)
    audio_thread.start()

if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(WS_URL,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever()
    # ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})