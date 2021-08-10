from telepotpro import Bot
from telepotpro.exception import *
from pony.orm import db_session, select
from os.path import abspath, dirname, join
from json import load as jsload
from time import sleep
from threading import Thread
from datetime import datetime

from modules.apiHelpers import ApiHelpers
from modules.database import User, Message
from modules import keyboards, dbQuery

with open(join(dirname(abspath(__file__)), "settings.json")) as settings_file:
    js_settings = jsload(settings_file)

bot = Bot(js_settings["token"])
helpers = ApiHelpers(js_settings)
forwardChannel = js_settings["forwardChannel"]
makersita = -1001108947027


@db_session
def getUserString(user, forceName: bool=False):
    if user.username != "" and not forceName:
        return f"@{user.username}"
    fullname = " ".join((user.firstName, user.lastName))
    return f"<a href=\"tg://user?id={user.chatId}\">{fullname}</a>"


def getPosChar(n: int):
    chars = {
        1: "🥇", 2: "🥈", 3: "🥉",
        4: "4️⃣", 5: "5️⃣", 6: "6️⃣", 7: "7️⃣", 8: "8️⃣", 9: "9️⃣", 10: "🔟",
        "def": "-"
    }
    return chars.get(n, f"{n}.")


@db_session
def updateDB(msg, userOnly: bool=False):
    if not User.exists(lambda u: u.chatId == msg["from"]["id"]):
        dbuser = User(
            chatId=msg["from"]["id"],
            firstName=msg["from"].get("first_name", "Unknown"),
            lastName=msg["from"].get("last_name", ""),
            username=msg["from"].get("username", "")
        )
    else:
        dbuser = User.get(chatId=msg["from"]["id"])
        dbuser.firstName = msg["from"].get("first_name", "Unknown")
        dbuser.lastName = msg["from"].get("last_name", "")
        dbuser.username = msg["from"].get("username", "")

    dbmsg = None
    if not userOnly:
        if not Message.exists(lambda m: m.chatId == msg["chat"]["id"] and m.msgId == msg["message_id"]):
            dbmsg = Message(
                user=dbuser,
                text=msg.get("text", ""),
                date=msg["date"],
                chatId=msg["chat"]["id"],
                msgId=msg["message_id"]
            )
        else:
            if msg.get("edit_date"):
                dbmsg = Message.get(chatId=msg["chat"]["id"], msgId=msg["message_id"])
                dbmsg.text = msg.get("text", "")
                dbmsg.date = msg["edit_date"]
                dbmsg.edited = True

    return dbuser, dbmsg


@db_session
def makersFunctions(msg):
    if msg["chat"]["id"] != makersita:
        return

    if msg.get("new_chat_members"):
        for user in msg["new_chat_members"]:
            newJson = {"from": user}
            updateDB(newJson, userOnly=True)
    
    elif msg.get("from"):
        updateDB(msg)


@db_session
def runDatabaseUpdate(sender: int=None):
    for user in select(u for u in User):
        try:
            userInfo = bot.getChatMember(makersita, user.chatId)
            user.firstName = userInfo["user"].get("first_name", "Unknown")
            user.lastName = userInfo["user"].get("last_name", "")
            user.username = userInfo["user"].get("username", "")
            user.lastStatus = userInfo.get("status", "")
        except TelegramError:
            pass
        sleep(0.5)
    if sender is not None:
        try:
            bot.sendMessage(sender, "✅ Aggiornamento database finito!")
        except (TelegramError, BotWasBlockedError):
            bot.sendMessage(makersita, "✅ Aggiornamento database finito!")


@db_session
def reply(msg):
    makersFunctions(msg)

    chatId = msg["chat"]["id"]
    userId = msg["from"]["id"]
    userName = msg["from"]["first_name"]
    msgId = msg["message_id"]
    text = msg.get("text")

    if text is None:
        if chatId > 0:
            bot.sendMessage(chatId, "Non ho capito... /help")
        return

    ## ANY CHAT
    if text.startswith("/segnala "):
        try:
            link = helpers.get_link(msg)[0]
            if link:
                shorted = helpers.short(link)
                keyboard = None
                if any(w in shorted for w in ["bit.ly/", "amzn.to/"]):
                    linkId = shorted.split("/")[-1]
                    domain = "amznto" if "amzn.to" in shorted else "bitly"
                    keyboard = keyboards.prenota(domain, linkId)
                bot.sendMessage(forwardChannel, "<b>Nuova offerta segnalata!</b>\n"
                                                "<i>Da:</i> <a href=\"tg://user?id={}\">{}</a>\n\n"
                                                "{}".format(userId, userName, shorted),
                                parse_mode="HTML", disable_web_page_preview=True, reply_markup=keyboard)
                bot.sendMessage(chatId, "Grazie per la segnalazione, <b>{}</b>!".format(userName),
                                parse_mode="HTML")

        except Exception:
            bot.sendMessage(chatId, "<i>Non sono riuscito a segnalare l'offerta.</i>",
                            parse_mode="HTML", reply_to_message_id=msgId)
            raise

    elif text.lower().startswith("/topmessages") and (userId in js_settings["admins"]):
        n = int(text.split(" ")[1]) if len(text.split()) > 1 else 10
        lista = dbQuery.topMessages(n)
        message = f"📝 <b>TOP {n} messaggi MakersITA</b>\n"
        for i in range(len(lista)):
            user, nmsg = lista[i]
            pos = getPosChar(i + 1)
            message += f"\n{pos} {getUserString(user)}: {nmsg}"
        helpers.sendLongMessage(bot, chatId, message, parse_mode="HTML")

    elif text.lower().startswith("/topcpm") and (userId in js_settings["admins"]):
        n = int(text.split(" ")[1]) if len(text.split()) > 1 else 10
        minmsg = int(text.split(" ")[2]) if len(text.split()) > 2 else 30
        lista = dbQuery.topCharsPerMessage(n, minmsg)
        message = f"📝 <b>TOP {n} caratteri/messaggio MakersITA</b>\n" \
                  f"<i>Min. messaggi necessari: {minmsg}</i>\n"
        for i in range(len(lista)):
            user, cpm = lista[i]
            pos = getPosChar(i + 1)
            message += f"\n{pos} {getUserString(user)}: {cpm:.1f}"
        helpers.sendLongMessage(bot, chatId, message, parse_mode="HTML")

    elif text.lower().startswith("/membriinattivi") and (userId in js_settings["admins"]):
        n = int(text.split(" ")[1]) if len(text.split()) > 1 else 90
        lista = dbQuery.inactiveFor(n)
        message = f"👥 <b>Membri inattivi da {n} giorni:</b>\n"
        for user, days in lista:
            message += f"\n{getUserString(user)}: {days}"
        helpers.sendLongMessage(bot, chatId, message, parse_mode="HTML")

    elif text.lower().startswith("/topedit") and (userId in js_settings["admins"]):
        n = int(text.split(" ")[1]) if len(text.split()) > 1 else 10
        minmsg = int(text.split(" ")[2]) if len(text.split()) > 2 else 30
        lista = dbQuery.topEditRatio(n, minmsg)
        message = f"✏️ <b>TOP {n} edit ratio MakersITA</b>\n" \
                  f"<i>messaggi editati/messaggi totali (min. messaggi necessari: {minmsg})</i>\n"
        for i in range(len(lista)):
            user, ratio = lista[i]
            pos = getPosChar(i + 1)
            ratio *= 100
            message += f"\n{pos} {getUserString(user)}: {ratio:.2f}%"
        helpers.sendLongMessage(bot, chatId, message, parse_mode="HTML")

    elif text.lower().startswith("/topflood") and (userId in js_settings["admins"]):
        n = int(text.split(" ")[1]) if len(text.split()) > 1 else 10
        minmsg = int(text.split(" ")[2]) if len(text.split()) > 2 else 30
        lista = dbQuery.topFloodRatio(n, minmsg)
        message = f"📄 <b>TOP {n} flood ratio MakersITA</b>\n" \
                  f"<i>doppi messaggi/messaggi totali (min. messaggi necessari: {minmsg})</i>\n"
        for i in range(len(lista)):
            user, ratio = lista[i]
            pos = getPosChar(i + 1)
            ratio *= 100
            message += f"\n{pos} {getUserString(user)}: {ratio:.2f}%"
        helpers.sendLongMessage(bot, chatId, message, parse_mode="HTML")

    elif text.lower().startswith("/topmpd") and (userId in js_settings["admins"]):
        n = int(text.split(" ")[1]) if len(text.split()) > 1 else 10
        lista = dbQuery.topMessages(n)
        message = f"📝 <b>TOP {n} messaggi/giorno MakersITA</b>\n"
        for i in range(len(lista)):
            user, ratio = lista[i]
            pos = getPosChar(i + 1)
            message += f"\n{pos} {getUserString(user)}: {ratio:.1f}"
        helpers.sendLongMessage(bot, chatId, message, parse_mode="HTML")

    elif text.lower().startswith("/topgiorni") and (userId in js_settings["admins"]):
        n = int(text.split(" ")[1]) if len(text.split()) > 1 else 10
        lista = dbQuery.topMessages(n)
        message = f"📅 <b>TOP {n} giorni di attività MakersITA</b>\n"
        for i in range(len(lista)):
            user, days = lista[i]
            pos = getPosChar(i + 1)
            message += f"\n{pos} {getUserString(user)}: {days}"
        helpers.sendLongMessage(bot, chatId, message, parse_mode="HTML")


    ## PRIVATE CHAT
    if chatId > 0:
        if text == "/start":
            bot.sendMessage(chatId, "Ciao, sono il bot di overVolt!", parse_mode="html")

        elif text == "/help":
            bot.sendMessage(chatId, "Ciao, sono il bot di overVolt!\n\n"
                "Il bot è stato riscritto da zero, molti comandi non funzionano e sono stati deprecati.",
                parse_mode="html")

        elif text == "/referral":
            answer, found = helpers.handle_referral(msg)
            answer = answer.replace("/referral ", "")
            bot.sendMessage(chatId, answer, parse_mode="html")

        elif text.startswith("/start mystats"):
            rUser = User.get(chatId=userId)
            bot.sendMessage(chatId,
                            f"📊 <b>STATISTICHE UTENTE:</b> {getUserString(rUser)}\n"
                            f"\n"
                            f"📝 Messaggi inviati: <b>{dbQuery.messagesCount(rUser)}</b>\n"
                            f"📝 Media CPM: <b>{dbQuery.charsPerMessage(rUser):.1f}</b>\n"
                            f"✏️ Edit ratio: <b>{dbQuery.editRatio(rUser):.2f}%</b>\n"
                            f"📄 Flood ratio: <b>{dbQuery.floodRatio(rUser):.2f}%</b>\n"
                            f"📝 Media MPD: <b>{dbQuery.messagesPerDay(rUser):.1f}</b>\n"
                            f"📅 Membro da: <b>{dbQuery.membershipDays(rUser)} giorni</b>\n"
                            f"\n"
                            f"ℹ️ <b>Info dati</b>\n"
                            f"- CPM: media caratteri per messaggio\n"
                            f"- Edit ratio: la percentuale di messaggi editati su quelli inviati\n"
                            f"- Flood ratio: la percentuale di messaggi consecutivi (uno dopo l'altro) rispetto al totale\n"
                            f"- MPD: media messaggi al giorno", parse_mode="HTML")


    ## MAKERSITA
    elif chatId == makersita:
        isReply = "reply_to_message" in msg.keys()
        replyId = None if not isReply else msg["reply_to_message"]["message_id"]

        if text == "/updateDatabase" and (userId in js_settings["admins"]):
            bot.sendMessage(chatId, "🕙 Aggiorno il database...\n"
                                    "<i>Potrebbe volerci molto tempo, continuo in background.\n"
                                    "Controlla la chat privata per aggiornamenti!</i>",
                            parse_mode="HTML")
            Thread(target=runDatabaseUpdate, args=[userId], name="databaseUpdater").start()

        elif text.startswith("/parla ") and (userId in js_settings["admins"]):
            bot.sendMessage(chatId, text.split(" ", 1)[1], parse_mode="HTML", reply_to_message_id=replyId)
            bot.deleteMessage((chatId, msgId))

        elif text == "/userstats" and isReply and (userId in js_settings["admins"]):
            rUser = User.get(chatId=msg["reply_to_message"]["from"]["id"])
            bot.sendMessage(chatId,
                            f"📊 <b>STATISTICHE UTENTE</b>\n"
                            f"\n"
                            f"📝 Messaggi inviati: <b>{dbQuery.messagesCount(rUser)}</b>\n"
                            f"📝 Media CPM: <b>{dbQuery.charsPerMessage(rUser):.1f}</b>\n"
                            f"✏️ Edit ratio: <b>{dbQuery.editRatio(rUser):.2f}%</b>\n"
                            f"📄 Flood ratio: <b>{dbQuery.floodRatio(rUser):.2f}%</b>\n"
                            f"📝 Media MPD: <b>{dbQuery.messagesPerDay(rUser):.1f}</b>\n"
                            f"📅 Membro da: <b>{dbQuery.membershipDays(rUser)} giorni</b>\n"
                            f"\n"
                            f"ℹ️ <b>Info dati</b>\n"
                            f"- CPM: media caratteri per messaggio\n"
                            f"- Edit ratio: la percentuale di messaggi editati su quelli inviati\n"
                            f"- Flood ratio: la percentuale di messaggi consecutivi (uno dopo l'altro) rispetto al totale\n"
                            f"- MPD: media messaggi al giorno",
                            parse_mode="HTML", reply_to_message_id=replyId)

        elif text == "/mystats":
            user = User.get(chatId=userId)
            bot.sendMessage(chatId, "{}, <a href=\"https://t.me/overVoltBot?start=mystats_{}\">"
                                    "Clicca qui per vedere le tue statistiche</a>"
                                    "".format(getUserString(user), userId), parse_mode="HTML")

        else:
            testo, found = helpers.handle_referral(msg)
            if found and ("Impossibile applicare il referral" not in testo):
                nome = msg["from"]["first_name"]
                if "last_name" in msg["from"].keys():
                    nome += " " + msg["from"]["last_name"]
                bot.sendMessage(chatId,
                    "<b>[Link inviato da</b> <a href=\"tg://user?id={0}\">{1}</a><b>]</b>\n\n{2}".format(userId, nome, testo),
                    parse_mode="HTML", reply_to_message_id=replyId, disable_web_page_preview=True)
                bot.deleteMessage((chatId, msgId))


def button(msg):
    chatId = msg["message"]["chat"]["id"]
    userName = msg["from"]["first_name"]
    msgId = msg["message"]["message_id"]
    data = msg["data"]
    command = data.split("#")[0]
    params = data.split("#")[1:]

    if command == "prenotaLink":
        domain, linkId = params
        msgText = msg["message"]["text"]
        newText = msgText.replace("Nuova offerta segnalata!", "<b>[Prenotata da {}]</b>".format(userName))
        bot.editMessageText((chatId, msgId), newText, parse_mode="HTML", disable_web_page_preview=True,
                            reply_markup=keyboards.open_scontino(domain, linkId))


bot.message_loop({'chat': reply, 'callback_query': button})
while True:
    sleep(60)
    clock = datetime.now().strftime("%H:%M")
    if clock == "02:00":
        Thread(target=runDatabaseUpdate, name="databaseUpdater").start()
