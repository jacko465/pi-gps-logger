import threading
import signal

# context manager class to handle running as service and graceful shutdown
class ShutdownManager:
    def __init__(self):
        self.shutdown_event = threading.Event()

    def __enter__(self):
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        return self.shutdown_event
    
    def __exit__(self, exc_type, exc_value, traceback):
        print("Shutting down service...")
        self.shutdown_event.set()

    def handle_signal(self, signal, frame):
        print(f"Received signal {signal}")
        self.shutdown_event.set()