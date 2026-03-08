import subprocess
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os


class BotReloader(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_bot()

    def start_bot(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        print("♡ Starting Joy bot...")
        self.process = subprocess.Popen([sys.executable, "dawn.py"])

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"♡ Detected changes in {os.path.basename(event.src_path)}")
            self.start_bot()


def main():
    reloader = BotReloader()
    observer = Observer()
    observer.schedule(reloader, path='.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n♡ Stopping Joy bot...")
        if reloader.process:
            reloader.process.terminate()
            reloader.process.wait()
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
