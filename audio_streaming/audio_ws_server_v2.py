import asyncio
import websockets
import json
import google.cloud.speech_v2 as speech_v2
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.oauth2 import service_account
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudioTranscriptionServer:
    def __init__(self, service_account_path: str, project_id: str):
        """
        Initialize the Audio Transcription Server
        
        Args:
            service_account_path: Path to service account JSON file
            project_id: Google Cloud project ID
        """
        self.credentials = service_account.Credentials.from_service_account_file(
            service_account_path
        )
        self.project_id = project_id
        self.speech_client = SpeechClient(credentials=self.credentials)
        
    async def process_audio_stream(self, websocket):
        """
        Process incoming audio stream from a WebSocket client
        """
        try:
            config = cloud_speech.RecognitionConfig(
                explicit_decoding_config=cloud_speech.ExplicitDecodingConfig(
                    encoding="LINEAR16",
                    sample_rate_hertz=16000,
                    audio_channel_count=1,
                ),
                language_codes=["en-US"],
                model="latest_long",
                adaptation=None,
            )
            
            streaming_config = cloud_speech.StreamingRecognitionConfig(
                config=config,
                streaming_features=cloud_speech.StreamingRecognitionFeatures(
                    interim_results=True
                )
            )

            # Create a queue for audio chunks
            audio_queue = asyncio.Queue()
            
            # Create a simple class to hold shared state
            class StreamState:
                def __init__(self):
                    self.is_active = True
            
            state = StreamState()

            # Synchronous generator for gRPC
            def request_generator():
                # Yield the initial config request
                yield cloud_speech.StreamingRecognizeRequest(
                    recognizer=f"projects/{self.project_id}/locations/global/recognizers/_",
                    streaming_config=streaming_config
                )
                
                # Keep yielding audio requests
                while state.is_active:
                    try:
                        # Get audio chunk from queue (non-blocking)
                        audio_chunk = audio_queue.get_nowait()
                        yield cloud_speech.StreamingRecognizeRequest(audio=audio_chunk)
                    except asyncio.QueueEmpty:
                        # If queue is empty, sleep briefly
                        time.sleep(0.01)
                    except Exception as e:
                        logger.error(f"Error in request generator: {str(e)}")
                        break

            # Background task to receive audio
            async def receive_audio():
                try:
                    while state.is_active:
                        audio_chunk = await websocket.recv()
                        await audio_queue.put(audio_chunk)
                except websockets.exceptions.ConnectionClosed:
                    logger.info("Client disconnected")
                    state.is_active = False
                except Exception as e:
                    logger.error(f"Error receiving audio: {str(e)}")
                    state.is_active = False

            # Background task to process responses
            async def process_responses(responses):
                try:
                    for response in responses:
                        if not state.is_active:
                            break
                        if response.results:
                            for result in response.results:
                                transcript = result.alternatives[0].transcript
                                is_final = result.is_final
                                
                                await websocket.send(json.dumps({
                                    "transcript": transcript,
                                    "is_final": is_final
                                }))
                except Exception as e:
                    logger.error(f"Error processing responses: {str(e)}")
                finally:
                    state.is_active = False

            # Start receiving audio in background
            receive_task = asyncio.create_task(receive_audio())
            
            # Start the streaming recognize call
            responses = self.speech_client.streaming_recognize(requests=request_generator())
            
            # Process responses
            await process_responses(responses)
            
            # Clean up
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass

        except Exception as e:
            logger.error(f"Error in process_audio_stream: {str(e)}")
        finally:
            await websocket.close()

    async def start_server(self, host: str = "localhost", port: int = 8765):
        """Start the WebSocket server"""
        try:
            async with websockets.serve(self.process_audio_stream, host, port):
                logger.info(f"WebSocket server started on ws://{host}:{port}")
                await asyncio.Future()  # run forever
        except Exception as e:
            logger.error(f"Error starting server: {str(e)}")

def main():
    # Configuration
    SERVICE_ACCOUNT_PATH = "./service-account.json"
    PROJECT_ID = "cloud-learning-443407"
    HOST = "0.0.0.0"
    PORT = 8765
    
    # Create and start the server
    server = AudioTranscriptionServer(SERVICE_ACCOUNT_PATH, PROJECT_ID)
    
    try:
        asyncio.run(server.start_server(HOST, PORT))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")

if __name__ == "__main__":
    main()
