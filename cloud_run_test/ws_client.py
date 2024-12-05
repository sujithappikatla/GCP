import websocket
import threading
import ssl
import time


# WebSocket configuration
# WS_URL = "ws://localhost:8080"
WS_URL = "wss://long-run-server-305533803718.us-west1.run.app"

def on_message(ws, message):
    print(message)

def on_error(ws, error):    
    print("Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_open(ws):
    print("WebSocket connection opened")

    def send_message():
        seconds_elapsed = 0
        try:
            while True:
                ws.send("Hello from client")
                time.sleep(1)
                seconds_elapsed += 1
                print(f"Seconds elapsed: {seconds_elapsed}")

        except Exception as e:
            print(e)

   
    messenger_thread = threading.Thread(target=send_message)
    messenger_thread.start()

if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp(WS_URL,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    # ws.run_forever()
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})