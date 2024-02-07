#
# minimal daily-python command-line client using asyncio
#

import os
import asyncio
import signal
import time

from daily import *


class DailyApp(EventHandler):
    def __init__(self):
        self.__client = CallClient(event_handler=self)

    async def run(self):
        self.__client.join(
            os.getenv('DAILY_ROOM_URL'),
            meeting_token=os.getenv('DAILY_OWNER_TOKEN')
        )
        print("joined")

    def on_participant_joined(self, participant):
        print(f"participant joined: {participant['id']}")

    def on_error(self, error):
        print(f"daily-python error handler: {error}")

    def leave(self):
        self.__client.leave()


def main():
    Daily.init()
    app = DailyApp()

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
