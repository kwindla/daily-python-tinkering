
import os
import time
import threading
from daily import *


class PrintTranscriptApp(EventHandler):
    def __init__(self):
        self.__client = CallClient(event_handler=self)

        self.__client.update_subscription_profiles({
            "base": {
                "camera": "unsubscribed",
                "microphone": "unsubscribed"
            }
        })

        self.__app_quit = False
        self.__app_error = None

        self.__start_event = threading.Event()
        self.__thread = threading.Thread(target=self.print_something)
        self.__thread.start()

    def run(self):
        self.__client.join(
            os.getenv('DAILY_ROOM_URL'),
            meeting_token=os.getenv('DAILY_OWNER_TOKEN'),
            completion=self.on_joined
        )
        self.__thread.join()

    def on_joined(self, data, error):
        print("joined")
        if error:
            print(f"Unable to join meeting: {error}")

        self.__app_error = error
        self.__start_event.set()

        try:
            self.__client.stop_transcription()
        except Exception as e:
            print(f"Unable to stop transcription: {e}")

        try:
            self.__client.start_transcription(
                settings={
                    "extra": {
                        #    "keywords": "Kwindla:5"
                    }
                },
                # supplying a completion seems to hang daily-python
                # completion=self.transcription_started_completion
            )
        except Exception as e:
            print(f"Unable to start transcription: {e}")

    def transcription_started_completion(self, data, error):
        print("---> tsc", data, error)

    def on_transcription_started(self, data):
        print("ots", data)

    def on_transcription_message(self, message):
        print("otm")
        print(message)

    def leave(self):
        self.__client.leave()

    def print_something(self):
        print("top of print_something")
        self.__start_event.wait()

        if self.__app_error:
            print(f"Unable to print anything")
            return

        while not self.__app_quit:
            time.sleep(1)
            print("loop")

    def on_participant_joined(self, participant):
        print(f"participant joined: {participant['id']}")

    def on_error(self, error):
        print(f"daily-python error handler: {error}")


def main():
    Daily.init()
    app = PrintTranscriptApp()

    try:
        app.run()
    except KeyboardInterrupt:
        print("Ctrl-C detected. Exiting!")
    finally:
        app.leave()


if __name__ == '__main__':
    main()
