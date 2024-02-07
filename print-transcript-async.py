
import os
import asyncio
import signal
import time

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

    async def run(self):
        self.__client.join(
            os.getenv('DAILY_ROOM_URL'),
            meeting_token=os.getenv('DAILY_OWNER_TOKEN'),
            completion=self.on_joined
        )

    def on_joined(self, data, error):
        print("joined")
        if error:
            print(f"join meeting error: {error}")

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
            print(f"start transcription error: {e}")

    def transcription_started_completion(self, data, error):
        print("---> tsc", data, error)

    def on_transcription_started(self, data):
        print("ots", data)

    def on_transcription_message(self, message):
        print("otm")
        print(message)

    def leave(self):
        self.__client.leave()

    def on_participant_joined(self, participant):
        print(f"participant joined: {participant['id']}")

    def on_error(self, error):
        print(f"daily-python error handler: {error}")


def main():
    Daily.init()
    app = PrintTranscriptApp()

    loop = asyncio.get_event_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            s, lambda s=s: shutdown(loop, signal=s, dailyApp=app))
    try:
        loop.create_task(app.run())
        loop.run_forever()
    finally:
        loop.close()


def shutdown(loop, signal=None, dailyApp=None):
    if dailyApp:
        dailyApp.leave()
        time.sleep(0.1)
    loop.stop()


if __name__ == '__main__':
    main()
