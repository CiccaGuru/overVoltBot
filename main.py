import sys, os, asyncio, telepot, emoji, re, json, urllib.request
from telepot.aio.loop import MessageLoop
from telepot.aio.helper import InlineUserHandler, AnswererMixin, Editor
from telepot.aio.delegate import per_inline_from_id, create_open, pave_event_space, per_chat_id
from uuid import uuid4
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
from random import randint


class OverVoltBot(InlineUserHandler, AnswererMixin):

    URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
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
        self.BANGGOOD_REFERRAL = "63091629786202015112"
        self.AMAZON_REFERRAL = "overvolt-21"

    def removeTag(self, url, tag):
        length = len(url)
        tagIndex = url.find(tag+"=")
        while tagIndex > 0:
            nextParameterIndex = url[tagIndex:].find("&")
            if (nextParameterIndex+tagIndex+1>=length) or (nextParameterIndex <0):
                url = url[:(tagIndex-1)]
            else:
                if url[tagIndex-1] != "&":
                    url = url[:(tagIndex)]  + url[(nextParameterIndex+tagIndex+1):]
                else:
                    url = url[:(tagIndex-1)] + url[(nextParameterIndex+tagIndex):]
            length = len(url)
            tagIndex = url.find(tag+"=")
        return url

    def getReferralLink(self, url):
        newUrl = url
        messaggio = '<i>Impossibile applicare il referral</i>'
        success = False
        store = ""
        if "amazon.it" in url:
            length = len(url)
            url = self.removeTag(self.removeTag(self.removeTag(url, "ref"), "linkId"), "tag")
            separator = url.find("?")>0 and  "&" or "?"
            newUrl = url + separator + "tag=" + self.AMAZON_REFERRAL
            messaggio = newUrl
            success = True
            store = "Amazon"
        elif "banggood.com" in url:
            length = len(url)
            indexHtml = url.find(".html")
            indexTag = url.find("p=")
            if indexHtml > 0:
                url = self.removeTag(url, "p")
                newUrl = url + separator +  "p="+self.BANGGOOD_REFERRAL;
            messaggio = newUrl
            success = True
            store = "Banggood"
        elif "gearbest.com" in url:
            length = len(url)
            indexHtml = url.find(".html")
            indexTag = url.find("lkid=")
            if indexHtml > 0:
                url = self.removeTag(url, "lkid")
                separator = url.find("?")>0 and "&" or "?";
                newUrl = url + separator +  "lkid="+self.GEARBEST_REFERRAL;
            messaggio = newUrl
            success = True
            store = "Gearbest"
        return (success, messaggio, store)

    def short(self, long_url):
        long_url = long_url.replace("&", "%26")
        bitlyApi = 'https://api-ssl.bitly.com/v3/shorten?access_token=e8de1a5482420f3dbd0790fdffa93ba6e415d7f9&longUrl=%s' % long_url
        try:
            with urllib.request.urlopen(bitlyApi) as r:
                data = r.read().decode()
                data = json.loads(data)
                data = data['data']
                data = data['url']
                data = data.replace("https://", "")
                data = data.replace("http://", "")
        except Exception:
            print(data)
            data = long_url
        return data


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


    async def check_referral(self, urls, msg):
        new_urls = []
        for url in urls:
            if "amzn.to" in url or "bit.ly" in url or "goo.gl" in url:
                richiesta = urllib.request.urlopen(url)
                url = richiesta.geturl()
            if ("amazon" in url and "tag" in url and ("overvolt-21" not in url or "offervolt-21" not in url)) or ("banggood" in url and "p=" in url and self.BANGGOOD_REFERRAL not in url) or ("gearbest" in url and "lkid" in url and self.GEARBEST_REFERRAL not in url):
                await self.sender.sendMessage("Cattivo bambino, non si usano i referral non di marco! Te li correggo io ")
            if "amazon" in url or "banggood" in url or "gearbest" in url:
                new_urls.append(self.short(self.getReferralLink(url)[1]))
        return new_urls


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
        if msg['chat']['id']<0:
            testo = msg["text"]
            userId = msg["from"]["id"]
            urls = re.findall(self.URL_REGEX, testo)
            editor = Editor(self.bot, telepot.message_identifier(msg))
            if testo.split()[0] == "/parla":
                if userId in [50967453, 368894926, 77080264]:
                    await self.sender.sendMessage(testo.replace("/parla", ""))
                await editor.deleteMessage()
            else:
                if len(urls)>0:
                    new_urls = await self.check_referral(urls, msg)
                    print(new_urls)
                    if len(new_urls) > 0:
                        for i in range(0,len(new_urls)):
                            testo = testo.replace(urls[i], new_urls[i])
                            try:
                                nome = msg["from"]["first_name"] +" "+ msg["from"]["last_name"]
                            except:
                                nome = msg["from"]["first_name"]
                        await self.sender.sendMessage("[<b>Inviato da "+nome+"] </b>\n\n" + testo, parse_mode="html")
                        await editor.deleteMessage()

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
