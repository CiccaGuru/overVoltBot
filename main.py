import os, asyncio, telepot, emoji, re, json, urllib.request, time
from telepot.aio.loop import MessageLoop
from telepot.aio.helper import InlineUserHandler, AnswererMixin, Editor
from telepot.aio.delegate import per_inline_from_id, create_open, pave_event_space, per_chat_id
from uuid import uuid4
from apiclient.discovery import build
from random import randint
import requests


class OverVoltBot(InlineUserHandler, AnswererMixin):

    def __init__(self, *args, **kwargs):
        super(OverVoltBot, self).__init__(*args, **kwargs)
        self.count = 0

        my_dir = os.path.dirname(os.path.abspath(__file__))
        read_dev_key = open(os.path.join(my_dir, "DEVELOPER_KEY"))
        self.DEVELOPER_KEY = read_dev_key.read().strip()
        read_dev_key.close()

        self.YOUTUBE_API_SERVICE_NAME = "youtube"
        self.YOUTUBE_API_VERSION = "v3"
        read_channel_id = open(os.path.join(my_dir, "CHANNEL_ID"))
        self.CHANNEL_ID = read_channel_id.read().strip()

        self.GEARBEST_REFERRAL = "12357131"
        self.BANGGOOD_REFERRAL = "63091629786202015112&utm_campaign=overVolt&utm_content=liuyuwen"
        self.AMAZON_REFERRAL = "overvolt-21"
        self.ALLOWED_REFS = ["overvolt-21", "offervolt-21", "offervolt_f-21", "offervolt_n-21",
                                "offervolt_s-21", "offervolt_k-21", "overvoltfr-21",
                                "overvoltes-21", "overvoltde-21", "63091629786202015112",
                                "12357131"]
        self.botAdmins = [50967453, 368894926, 77080264]


    def searchYoutube(self, query, numResults, random):
        youtube = build(self.YOUTUBE_API_SERVICE_NAME, self.YOUTUBE_API_VERSION, developerKey=self.DEVELOPER_KEY)
        results = []

        if random:
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


    @staticmethod
    def get_link(msg):
        """Extract the link from a message"""
        links = []
        if "entities" in msg:
            raw_links = [x for x in msg["entities"] if x["type"] == "url"]
            for link in raw_links:
                links.append(msg["text"][link["offset"]:(link["offset"]+link["length"])].strip())
        return links


    @staticmethod
    def removeTag(url, tag):
        """Remove affiliation tags from urls"""
        length = len(url)
        tag_index = url.find(tag + "=")

        while tag_index > 0:
            next_parameter_index = url[tag_index:].find("&")
            if (next_parameter_index + tag_index + 1 >= length) \
                    or (next_parameter_index < 0):
                url = url[:(tag_index - 1)]
            else:
                if url[tag_index - 1] != "&":
                    url = url[:tag_index] + \
                        url[(next_parameter_index + tag_index + 1):]
                else:
                    url = url[:(tag_index - 1)] + \
                        url[(next_parameter_index + tag_index):]
            length = len(url)
            tag_index = url.find(tag + "=")
        return url


    @staticmethod
    def short(long_url):
        """Shorten urls"""
        import json
        import urllib.request
        import urllib.parse

        if "https://" not in long_url and "http://" not in long_url:
            escaped = "http://" + long_url
        else:
            escaped = long_url

        escaped = urllib.parse.quote(escaped, safe="")
        bitly_api = r"https://api-ssl.bitly.com/v3/shorten" \
            r"?access_token=e8de1a5482420f3dbd0790fdffa93ba6e415d7f9&longUrl" \
            r"={}".format(escaped)

        try:
            with urllib.request.urlopen(bitly_api) as request:
                data = json.loads(request.read().decode())
                data = data['data']['url']
                data = data.replace("https://", "").replace("http://", "")
        except (KeyError, TypeError):
            data = long_url
        return data


    def getReferralLink(self, url):
        messaggio = '<i>Impossibile applicare il referral</i> su ' + url
        success = False
        store = ""

        if "amazon.it" in url:
            url = self.removeTag(url, "ref")
            url = self.removeTag(url, "linkId")
            url = self.removeTag(url, "tag")
            separator = url.find("?")>0 and  "&" or "?"
            messaggio = self.short("{0}{1}tag={2}".format(url, separator, self.AMAZON_REFERRAL))
            success = True
            store = "Amazon"

        elif "banggood.com" in url:
            url = self.removeTag(url, "p")
            url = self.removeTag(url, "utm_campaign")
            url = self.removeTag(url, "utm_content")
            separator = url.find("?")>0 and  "&" or "?"
            messaggio = self.short("{0}{1}p={2}".format(url, separator, self.BANGGOOD_REFERRAL))
            success = True
            store = "Banggood"

        elif "gearbest.com" in url:
            url = self.removeTag(url, "lkid")
            url = self.removeTag(url, "eo")
            separator = url.find("?")>0 and  "&" or "?"
            messaggio = self.short("{0}{1}lkid={2}".format(url, separator, self.GEARBEST_REFERRAL))
            success = True
            store = "Gearbest"

        return success, messaggio, store


    async def check_referral(self, url):
        new_url = url

        if "https://" not in new_url and "http://" not in new_url:
            new_url = "http://" + new_url
        new_url = new_url.replace("it.gearbest","gearbest")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "it,en","Accept-Encoding": "gzip, deflate"}
        new_url = requests.Session().head(new_url, timeout=10, headers=headers).url

        if any(x in new_url for x in ["amazon", "banggood", "gearbest"]) and not any(x in new_url for x in self.ALLOWED_REFS):
            new_url.replace("//gearbest", "//it.gearbest")
            return self.short(self.getReferralLink(new_url)[1])
        return False


    async def handle_referral(self, msg):
        urls = self.get_link(msg)
        testo = msg["text"]
        found = False
        for url in urls:
            new_url = await self.check_referral(url)
            if new_url:
                found = True
                testo = testo.replace(url, new_url)
        return testo, found


    def on_inline_query(self, msg):
        def compute_answer():
            query_id, from_id, telegramQuery = telepot.glance(msg, flavor='inline_query')
            id_referral = uuid4().hex
            articles = []
            (success, messaggio, store) = self.getReferralLink(telegramQuery)

            if success:
                articles.append({'type': 'article', 'id': id_referral, 'title': "Applica referral su "+store, 'message_text': messaggio})
            articles.extend(self.searchYoutube(telegramQuery, 5, False))

            return articles
        self.answerer.answer(msg, compute_answer)


    @staticmethod
    def on_chosen_inline_result(msg):
        telepot.glance(msg, flavor='chosen_inline_result')


    async def on_chat_message(self, msg):
        if "text" in msg:
            splitted = msg["text"].split()
        else:
            return

        if splitted[0] == "/referral":
            answer, found = await self.handle_referral(msg)
            answer = answer.replace("/referral ", "")
            await self.sender.sendMessage(answer, parse_mode = "html")

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
            messaggio = await self.handle_referral(msg)
            await self.sender.sendMessage(messaggio, parse_mode="html")

        if msg['chat']['id']<0:
            testo = msg["text"]
            userId = msg["from"]["id"]

            if "reply_to_message" in msg.keys():
                reply_id = msg["reply_to_message"]["message_id"]
            else:
                reply_id = None

            editor = Editor(self.bot, telepot.message_identifier(msg))

            if testo.split()[0] == "/parla":
                if userId in self.botAdmins:
                    await self.sender.sendMessage(testo.replace("/parla", ""), reply_to_message_id=reply_id)
                await editor.deleteMessage()

            else:
                testo, found = await self.handle_referral(msg)
                if found:
                    nome = msg["from"]["first_name"]
                    try:
                        nome += " " + msg["from"]["last_name"]
                    except Exception as e:
                        pass
                    await self.sender.sendMessage("<b>[Inviato da</b> <a href='tg://user?id={0}'>{1}</a><b>]</b>\n\n{2}".format(userId, nome, testo), parse_mode="HTML", reply_to_message_id=reply_id)
                    await editor.deleteMessage()


    def on_close(self, ex):
        """Close bot after timeout"""
        pass

my_dir = os.path.dirname(os.path.abspath(__file__))
token_file = open(os.path.join(my_dir, "TOKEN_TEST"))
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
