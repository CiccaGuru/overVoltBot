from requests import utils, post, Session
from time import sleep


class ApiHelpers:
    def __init__(self, settings):
        self.settings = settings

    @staticmethod
    def sendLongMessage(bot, chatId, text: str, **kwargs):
        maxMessageLength = 4096
        if len(text) <= maxMessageLength:
            return bot.sendMessage(chatId, text, **kwargs)

        parts = []
        while len(text) > 0:
            if len(text) > maxMessageLength:
                part = text[:maxMessageLength]
                first_lnbr = part.rfind('\n')
                if first_lnbr != -1:
                    parts.append(part[:first_lnbr])
                    text = text[(first_lnbr + 1):]
                else:
                    parts.append(part)
                    text = text[maxMessageLength:]
            else:
                parts.append(text)
                break

        msg = None
        for part in parts:
            msg = bot.sendMessage(chatId, part, **kwargs)
            sleep(0.5)
        return msg

    @staticmethod
    def get_link(msg):
        if "entities" not in msg:
            return []

        links = []
        raw_links = [x for x in msg["entities"] if x["type"] == "url"]
        for link in raw_links:
            text_utf16 = msg["text"].encode('utf-16-le')
            start = link['offset']
            end = start + link['length']
            linkText = text_utf16[start * 2:end * 2].decode('utf-16-le').strip()
            links.append(linkText)

        return links

    @staticmethod
    def remove_tag(url, tag):
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

        if "amazon." in url:
            urlAmazonSplit = url.split("amazon.", 1)
            afterAmazonParts = urlAmazonSplit[1].split("/")
            nat = afterAmazonParts[0]
            urlParts = afterAmazonParts[1:]
            if len(urlParts) > 0:
                while urlParts[0] != "dp" and urlParts[0] != "product":
                    urlParts.pop(0)
                if urlParts[0] == "dp":
                    urlParts.pop(0)

            # Rebuild url
            url = f"https://www.amazon.{nat}/offerVolt/dp/{'/'.join(urlParts)}"

        return url

    def short(self, long_url):
        if "https://" not in long_url and "http://" not in long_url:
            escaped = "http://" + long_url
        else:
            escaped = long_url

        header = {
            "Authorization": self.settings["bitly_token"],
            "Content-Type": "application/json"
        }
        params = {
            "long_url": utils.requote_uri(escaped)
        }
        try:
            response = post("https://api-ssl.bitly.com/v4/shorten", json=params, headers=header)
            data = response.json()
            short = data["id"]
        except Exception:
            short = long_url
        return short

    def getReferralLink(self, url):
        messaggio = "<i>Impossibile applicare il referral</i> su " + url
        success = False
        store = ""

        if "amazon.it" in url:
            url = self.remove_tag(url, "ref")
            url = self.remove_tag(url, "linkId")
            url = self.remove_tag(url, "tag")
            separator = url.find("?") > 0 and "&" or "?"
            messaggio = self.short("{0}{1}tag={2}".format(url, separator, self.settings["referrals"]["amazon"]))
            success = True
            store = "Amazon"

        elif "banggood.com" in url:
            url = self.remove_tag(url, "p")
            url = self.remove_tag(url, "utm_campaign")
            url = self.remove_tag(url, "utm_content")
            separator = url.find("?") > 0 and "&" or "?"
            messaggio = self.short("{0}{1}p={2}".format(url, separator, self.settings["referrals"]["banggood"]))
            success = True
            store = "Banggood"

        elif "gearbest.com" in url:
            url = self.remove_tag(url, "lkid")
            url = self.remove_tag(url, "eo")
            separator = url.find("?") > 0 and "&" or "?"
            messaggio = self.short("{0}{1}lkid={2}".format(url, separator, self.settings["referrals"]["gearbest"]))
            success = True
            store = "Gearbest"

        return success, messaggio, store

    def check_referral(self, url):
        new_url = url

        if "https://" not in new_url and "http://" not in new_url:
            new_url = "http://" + new_url

        new_url = new_url.replace("it.gearbest","gearbest")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "it,en","Accept-Encoding": "gzip, deflate"}
        new_url = Session().head(new_url, timeout=10, headers=headers).url

        if any(x in new_url for x in ["amazon", "banggood", "gearbest"]) and not any(x in new_url for x in self.settings["referrals"]["allowed"]):
            new_url.replace("//gearbest", "//it.gearbest")
            return self.short(self.getReferralLink(new_url)[1])

        return False

    def handle_referral(self, msg):
        urls = self.get_link(msg)
        testo = msg["text"]
        found = False
        for url in urls:
            new_url = self.check_referral(url)
            if new_url:
                found = True
                testo = testo.replace(url, new_url)
        return testo, found
