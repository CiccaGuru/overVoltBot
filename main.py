import telepot
from telepot.loop import MessageLoop
from pprint import pprint

bot = telepot.Bot('420659811:AAFF2rKdrUXxXuHQW0KPZt8SUxwRf-CRBE8')

def handle(msg):
    pprint(msg)

MessageLoop(bot, handle).run_as_thread()
