import os

from bot.event_bot import EventBot

def main():
    token = os.environ.get("TOKEN")
    bot = EventBot(token=token)
    bot.run()

if __name__ == "__main__":
    main()
