import sys
import asyncio
import telepot
from telepot.aio.loop import MessageLoop
from telepot.aio.helper import InlineUserHandler, AnswererMixin
from telepot.aio.delegate import per_inline_from_id, create_open, pave_event_space, per_chat_id
from uuid import uuid4
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from random import randint

def p(text):
    print(text)
    sys.stdout.flush()

DEVELOPER_KEY = "AIzaSyDauAadm_7YeM9vW_8LSFm9KnUydhRynqY"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
CHANNEL_ID = ""
class OverVoltBot(InlineUserHandler, AnswererMixin):
    def __init__(self, *args, **kwargs):
        super(OverVoltBot, self).__init__(*args, **kwargs)
        self.count = 0

    def getReferralLink(self, url):
        newUrl = url
        messaggio = "</i>Impossibile applicare il referral</i>"
        success = False
        store = ""
        if "amazon.it" in url:
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
            separator = url.find("?")>0 and  "&" or "?"
            newUrl = url + separator + "tag=overVolt-21"
            messaggio = newUrl
            success = True
            store = "Amazon"
        elif "banggood.com" in url:
            index = url.find(".html");
            if not (".html?p=63091629786202015112" in url) and index > 0:
                newUrl = url[0:index] +  ".html?p=63091629786202015112"
            messaggio = newUrl
            success = True
            store = "Amazon"
        return (success, messaggio, store)

    def searchYoutube(self, query, numResults, random):
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY)
        results = []
        p(random)
        if(random):
            search_response = youtube.search().list(
                q="",
                part="id,snippet",
                maxResults=20,
                order="viewCount",
                type="video",
                channelId="UCw6ekhAtFahKr7gImCIoYwg"
            ).execute()
            items = search_response.get("items", [])
            p(items)
            rand = randint(0, len(items)-1)
            search_result = items[rand]
            id_articolo = uuid4().hex
            if search_result["id"]["kind"] == "youtube#video":
                results.append({'type': 'video',
                                 'id': id_articolo,
                                 'video_url': "www.youtube.it/watch?v=%s" % search_result["id"]["videoId"],
                                 "mime_type": "text/html",
                                 'title': search_result["snippet"]["title"],
                                 'description': search_result["snippet"]["description"],
                                 "thumb_url":   search_result["snippet"]["thumbnails"]["default"]["url"],
                                 "message_text": "www.youtube.it/watch?v=%s" % search_result["id"]["videoId"]})
        else:
            search_response = youtube.search().list(
                q=query,
                part="id,snippet",
                maxResults=numResults,
                order="relevance",
                type="video",
                channelId="UCw6ekhAtFahKr7gImCIoYwg"
            ).execute()
            for search_result in search_response.get("items", []):
                id_articolo = uuid4().hex
                if search_result["id"]["kind"] == "youtube#video":
                    results.append({'type': 'video',
                                     'id': id_articolo,
                                     'video_url': "www.youtube.it/watch?v=%s" % search_result["id"]["videoId"],
                                     "mime_type": "text/html",
                                     'title': search_result["snippet"]["title"],
                                     'description': search_result["snippet"]["description"],
                                     "thumb_url":   search_result["snippet"]["thumbnails"]["default"]["url"],
                                     "message_text": "www.youtube.it/watch?v=%s" % search_result["id"]["videoId"]})
        return results
                        
    def on_inline_query(self, msg):
        def compute_answer():
            query_id, from_id, telegramQuery = telepot.glance(msg, flavor='inline_query')
            id_referral = uuid4().hex
            url = telegramQuery
            articles = []
            (success, messaggio, store) = getReferralLink(telegramQuery)
            if success:
                articles.append({'type': 'article', 'id': id_referral, 'title': "Applica referral su "+store, 'message_text': messaggio})
            articles.extend(self.searchYoutube(telegramQuery, 5))
            return articles
        self.answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        p("CIAO");
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
        p(str(self.id) + ':' + 'Chosen Inline Result:' + " "+ str(result_id) + " "+ str(from_id) + " "+ str(query_string))

    async def on_chat_message(self, msg):
        id_referral = uuid4().hex
        splitted = msg["text"].split()
        if splitted[0] == "/referral":
            (status,messaggio,store) = self.getReferralLink(" ".join(splitted[1:]))
            await self.sender.sendMessage(messaggio)
        elif splitted[0] == "/youtube":
            results = self.searchYoutube(" ".join(splitted[1:]), 5, (len(splitted)<=1))
            if len(results)>0:
                messaggio = results[0]["message_text"]
            else:
                messaggio = "<i>Nessun risultato</i>"
            await self.sender.sendMessage(messaggio, parse_mode = "html")
        elif splitted[0] == "/start":
            await self.sender.sendMessage("Comandi disponibili: \n - /referral [link]: applica il referral di OverVolt \n - /youtube [query]: ricerca tra i video di OverVolt", parse_mode = "html")

#TOKEN = "420659811:AAFF2rKdrUXxXuHQW0KPZt8SUxwRf-CRBE8"   ##PRODUCTION
#TOKEN = "371830775:AAEZld4C0qyuvxStk10ojImvBoKo5CNDsYY"  ##TEST
TOKEN = "235898396:AAHCcT94w-aCZS2THya8ho2SIc2xLDvVkQ0" #MARCO
bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_inline_from_id(), create_open, OverVoltBot, timeout=1),
     pave_event_space()(
         per_chat_id(), create_open, OverVoltBot, timeout=1),
])
loop = asyncio.get_event_loop()

loop.create_task(MessageLoop(bot).run_forever())
p('Listening ...')
loop.run_forever()


