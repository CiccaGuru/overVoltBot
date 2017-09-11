import sys
import asyncio
import telepot
from telepot.aio.loop import MessageLoop
from telepot.aio.helper import InlineUserHandler, AnswererMixin
from telepot.aio.delegate import per_inline_from_id, create_open, pave_event_space
from pprint import pprint
from uuid import uuid4
def p(text):
    print(text)
    sys.stdout.flush()
class InlineHandler(InlineUserHandler, AnswererMixin):
    def __init__(self, *args, **kwargs):
        super(InlineHandler, self).__init__(*args, **kwargs)

    def on_inline_query(self, msg):
        def compute_answer():
            query_id, from_id, url = telepot.glance(msg, flavor='inline_query')
            id_referral = uuid4().hex
            newUrl = url;
            splitted = url.split("/")
            counter = 0
            if splitted[2] == "www.amazon.it":
                length = len(url);
                tagIndex = url.find("tag=")
                while tagIndex > 0:
                    nextParameterIndex = url.find("&", tagIndex)
                    if nextParameterIndex+tagIndex+1>=length or nextParameterIndex <0:
                        url = url[:tagIndex];
                    else:
                        url = url[:tagIndex] + url.slice[nextParameterIndex + tagIndex:]
                    length = url.length;
                    tagIndex =url.find("tag=")
                    counter+=1
                separator = url.find("?")>0 and  "&" or "?"
                newUrl = url + separator + "tag=overVolt-21"
            elif splitted[2] == "www.banggood.com":
                index = url.find(".html");
                if not (".html?p=63091629786202015112" in url) and index > 0:
                    newUrl = url[0:index] +  ".html?p=63091629786202015112"

            articles = [{'type': 'article', 'id': id_referral, 'title': "Applica referral", 'message_text': newUrl}] 
            return articles
        self.answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        p("CIAO");
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        p(str(self.id) + ':' + 'Chosen Inline Result:' + " "+ str(result_id) + " "+ str(from_id) + " "+ str(query_string))


TOKEN = "420659811:AAFF2rKdrUXxXuHQW0KPZt8SUxwRf-CRBE8"

bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_inline_from_id(), create_open, InlineHandler, timeout=10),
])
loop = asyncio.get_event_loop()

loop.create_task(MessageLoop(bot).run_forever())
p('Listening ...')

loop.run_forever()
