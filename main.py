import sys
import os
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
import emoji

class OverVoltBot(InlineUserHandler, AnswererMixin):
    def __init__(self, *args, **kwargs):
        super(OverVoltBot, self).__init__(*args, **kwargs)
        self.count = 0
        read_dev_key = open('DEVELOPER_KEY')
        self.DEVELOPER_KEY = read_dev_key.read().strip()
        read_dev_key.close()
        self.YOUTUBE_API_SERVICE_NAME = "youtube"
        self.YOUTUBE_API_VERSION = "v3"
        read_channel_id = open("CHANNEL_ID")
        self.CHANNEL_ID = read_channel_id.read().strip()
        self.GEARBEST_REFERRAL = "12357131"
        self.BANGGOOD_REFERRAL = "63091629786202015112"
        self.AMAZON_REFERRAL = "overvolt-21"

    def getReferralLink(self, url):
        newUrl = url
        messaggio = '<i>Impossibile applicare il referral</i>'
        success = False
        store = ""
        if "amazon.it" in url:
            length = len(url)
            tagIndex = url.find("tag=")
            while tagIndex > 0:
                nextParameterIndex = url.find("&", tagIndex)
                if nextParameterIndex <0:
                    url = url[:tagIndex-1]
                else:
                    url = url[:tagIndex-1] + url[nextParameterIndex:]
                length = len(url);
                tagIndex =url.find("tag=")
            separator = url.find("?")>0 and  "&" or "?"
            newUrl = url + separator + "tag=" + self.AMAZON_REFERRAL
            print(newUrl)
            messaggio = newUrl
            success = True
            store = "Amazon"
        elif "banggood.com" in url:
            length = len(url)
            indexHtml = url.find(".html")
            indexTag = url.find("p=")
            if indexHtml > 0:
                while indexTag > 0:
                    nextParameterIndex = url[indexTag:].find("&")
                    if (nextParameterIndex+indexTag+1>=length) or (nextParameterIndex <0):
                        url = url[:(indexTag-1)]
                    else:
                        url = url[:(indexTag-1)] + url[(nextParameterIndex+indexTag):]
                    length = len(url)
                    indexTag = url.find("p=")
                separator = url.find("?")>0 and "&" or "?";
                newUrl = url + separator +  "p="+self.BANGGOOD_REFERRAL;
            messaggio = newUrl
            success = True
            store = "Banggood"
        elif "gearbest.com" in url:
            length = len(url)
            indexHtml = url.find(".html")
            indexTag = url.find("lkid=")
            if indexHtml > 0:
                while indexTag > 0:
                    nextParameterIndex = url[indexTag:].find("&")
                    if (nextParameterIndex+indexTag+1>=length) or (nextParameterIndex <0):
                        url = url[:(indexTag-1)]
                    else:
                        url = url[:(indexTag-1)] + url[(nextParameterIndex+indexTag):]
                    length = len(url)
                    indexTag = url.find("lkid=")
                separator = url.find("?")>0 and "&" or "?";
                newUrl = url + separator +  "lkid="+self.GEARBEST_REFERRAL;
            messaggio = newUrl
            success = True
            store = "Gearbest"
        return (success, messaggio, store)

    def searchYoutube(self, query, numResults, random):
        youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, developerKey=self.DEVELOPER_KEY)
        results = []
        if(random):
            search_response = youtube.search().list(
                q="",
                part="id,snippet",
                maxResults=20,
                order="viewCount",
                type="video",
                channelId=self.CHANNEL_ID
            ).execute()
            items = search_response.get("items", [])
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
                channelId=self.CHANNEL_ID
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
            (success, messaggio, store) = self.getReferralLink(telegramQuery)
            if success:
                articles.append({'type': 'article', 'id': id_referral, 'title': "Applica referral su "+store, 'message_text': messaggio})
            articles.extend(self.searchYoutube(telegramQuery, 5, False))
            return articles
        self.answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result', parse_mode = "html")

    async def on_chat_message(self, msg):
        id_referral = uuid4().hex
        splitted = msg["text"].split()
        if splitted[0] == "/referral":
            (status,messaggio,store) = self.getReferralLink(" ".join(splitted[1:]))
            await self.sender.sendMessage(messaggio, parse_mode = "html")
        elif splitted[0] == "/youtube":
            results = self.searchYoutube(" ".join(splitted[1:]), 5, (len(splitted)<=1))
            if len(results)>0:
                messaggio = results[0]["message_text"]
            else:
                messaggio = "Nessun risultato"
            await self.sender.sendMessage(messaggio, parse_mode = "html")
        elif splitted[0] == "/start":
            await self.sender.sendMessage("Comandi disponibili: \n - /referral [link]: applica il referral di OverVolt \n - /youtube [query]: ricerca tra i video di OverVolt", parse_mode = "html")
        elif splitted[0] == "/help":
            await self.sender.sendMessage("Ciao, sono il bot di overVolt :robot:! \n\n Per ora so: \n\n<b>Aggiungere un referral a un link</b>\nMandami un link di <b>Banggood</b> o <b>Gearbest</b> con il comando /referral &lt link &gt e io aggiungerò il referral! \n\n<b>Cercare su YouTube un video di overVolt</b>\nUsa il comando /youtube &lt stringa &gt per cercare su Youtube!", parse_mode = "html")
        elif msg['from']['id'] == msg['chat']['id']:
            await self.sender.sendMessage(emoji.emojize('Non ho capito :pensive_face:\n\n Scrivi /help per sapere come funziono.'), parse_mode = "html")


my_dir = os.path.dirname(os.path.abspath(__file__))
token_file = open(os.path.join(my_dir, "TOKEN"))
TOKEN = token_file.read().strip()
token_file.close()
bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_inline_from_id(), create_open, OverVoltBot, timeout=1),
     pave_event_space()(
         per_chat_id(), create_open, OverVoltBot, timeout=1),
])
loop = asyncio.get_event_loop()

loop.create_task(MessageLoop(bot).run_forever())
loop.run_forever()
