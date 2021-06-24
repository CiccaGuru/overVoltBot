from pony.orm import Database, Required, Optional, Set, PrimaryKey

db = Database("sqlite", "../makersita.db", create_db=True)


class User(db.Entity):
    chatId = PrimaryKey(int, sql_type='BIGINT', size=64)
    firstName = Optional(str)
    lastName = Optional(str)
    username = Optional(str)
    lastStatus = Optional(str)
    messages = Set("Message")


class Message(db.Entity):
    user = Required(User)
    text = Optional(str)
    date = Required(int, sql_type='BIGINT', size=64)
    chatId = Required(int, sql_type='BIGINT', size=64)
    msgId = Required(int, sql_type='BIGINT', size=64)
    edited = Required(bool, default=False)



db.generate_mapping(create_tables=True)
if __name__ == '__main__':
    from pony.orm import db_session, commit
    from json import load
    from datetime import datetime

    with open("../export.json", encoding="utf8") as jsfile:
        data = load(jsfile)
    total = len(data["messages"])
    chatId = -1001108947027

    savedUsers = set()
    savedMsgs = set()

    with db_session:
        for i in reversed(range(total)):
            message = data["messages"][i]
            if i % 1000 == 0:
                print(f"Parsing {i}/{total}")
                if i % 100000 == 0:
                    print("Saving progress...")
                    commit()

            if message["type"] == "service":
                if message.get("action") == "invite_members":
                    if message["actor_id"].startswith("user") and message["actor"] is not None:
                        fullname = message["actor"].split(" ")
                        firstname = fullname[0]
                        lastname = ""
                        if len(fullname) > 1:
                            lastname = " ".join(fullname[1:])

                        userid = int(message["actor_id"][4:])
                        if userid in savedUsers:
                            dbuser = User.get(chatId=userid)
                        # elif User.exists(chatId=userid):
                        #     dbuser = User.get(chatId=userid)
                        #     savedUsers.add(userid)
                        else:
                            dbuser = User(
                                chatId=userid,
                                firstName=firstname,
                                lastName=lastname,
                                username=""
                            )
                            savedUsers.add(userid)

            elif message["type"] == "message":
                if message["from"] is not None:
                    if message["from_id"].startswith("user"):
                        msgtext = message.get("text", "")
                        if type(msgtext) == list:
                            ntext = ""
                            for item in msgtext:
                                ntext += (" "+item) if type(item) == str else (" "+item["text"])
                            msgtext = ntext.strip()

                        msgid = message["id"]
                        date = datetime.strptime(message["date"], "%Y-%m-%dT%H:%M:%S")
                        msgdate = int(date.timestamp())

                        fullname = message["from"].split(" ")
                        firstname = fullname[0]
                        lastname = ""
                        if len(fullname) > 1:
                            lastname = " ".join(fullname[1:])

                        userid = int(message["from_id"][4:])
                        if userid in savedUsers:
                            dbuser = User.get(chatId=userid)
                        # elif User.exists(chatId=userid):
                        #     dbuser = User.get(chatId=userid)
                        #     savedUsers.add(userid)
                        else:
                            dbuser = User(
                                chatId=userid,
                                firstName=firstname,
                                lastName=lastname,
                                username=""
                            )
                            savedUsers.add(userid)

                        if (chatId, msgid) in savedMsgs:
                            dbmsg = Message.get(chatId=chatId, msgId=msgid)
                            if message.get("edited"):
                                date = datetime.strptime(message["edited"], "%Y-%m-%dT%H:%M:%S")
                                dbmsg.date = int(date.timestamp())
                                dbmsg.edited = True
                        # elif Message.exists(chatId=chatId, msgId=msgid):
                        #     dbmsg = Message.get(chatId=chatId, msgId=msgid)
                        #     savedMsgs.add((chatId, msgid))
                        else:
                            editflag = False
                            if message.get("edited"):
                                date = datetime.strptime(message["edited"], "%Y-%m-%dT%H:%M:%S")
                                msgdate = int(date.timestamp())
                                editflag = True
                            dbmsg = Message(
                                user=dbuser,
                                text=msgtext,
                                date=msgdate,
                                chatId=chatId,
                                msgId=msgid,
                                edited=editflag
                            )
                            savedMsgs.add((chatId, msgid))
