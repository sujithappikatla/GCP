import pyaudio
import websocket
import threading
import ssl

from google.oauth2 import service_account
from google.auth.transport.requests import Request

target_audience = 'https://speech-to-text-server-with-auth-305533803718.asia-south2.run.app'

creds = service_account.IDTokenCredentials.from_service_account_file(
        './sa.json',
        target_audience=target_audience)

creds.refresh(Request())
token = creds.token
print(creds.token)

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# WebSocket configuration
# WS_URL = "ws://localhost:8765"
WS_URL = "wss://speech-to-text-server-with-auth-305533803718.asia-south2.run.app"

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
    headers = {"Authorization": f"Bearer {token}"}
    ws = websocket.WebSocketApp(WS_URL,
                                header=headers,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    # ws.run_forever()s
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})