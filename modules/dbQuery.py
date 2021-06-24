from modules.database import User, Message
from pony.orm import db_session, select, avg, count
from datetime import datetime


@db_session
def topMessages(n: int=10):
    statusFilter = ["left", "kicked", ""]
    data = select((user, count(user.messages)) for user in User if user.lastStatus not in statusFilter).order_by(-2)
    return data.limit(n)


@db_session
def topCharsPerMessage(n: int=10, minMessages: int=30):
    statusFilter = ["left", "kicked", ""]
    data = select((
                      user,
                      avg(len(x.text) for x in user.messages if len(x.text) > 0)
                  ) for user in User if (count(user.messages) >= minMessages) and (user.lastStatus not in statusFilter)
                  ).order_by(-2)
    return data.limit(n)


@db_session
def charsPerMessage(user):
    return avg(len(x.text) for x in user.messages if len(x.text) > 0)


@db_session
def topEditRatio(n: int=10, minMessages: int=30):
    statusFilter = ["left", "kicked", ""]
    data = []
    for user in select(u for u in User if (count(u.messages) >= minMessages) and (u.lastStatus not in statusFilter)):
        data.append(
            (user, count(select(x for x in user.messages if x.edited)) / count(user.messages))
        )
    data.sort(key=lambda x: x[1], reverse=True)
    return data[:n]


@db_session
def editRatio(user):
    ratio = count(select(x for x in user.messages if x.edited)) / count(user.messages)
    return ratio


@db_session
def topFloodRatio(n: int=10, minMessages: int=30):
    statusFilter = ["left", "kicked", ""]
    data = []
    for user in select(u for u in User if (count(u.messages) >= minMessages) and (u.lastStatus not in statusFilter)):
        lastId = -1
        counter = 0
        firstOfGroup = True
        for msgId in select(x.msgId for x in user.messages).order_by(1):
            if msgId == lastId + 1:
                counter += 2 if firstOfGroup else 1
                firstOfGroup = False
            else:
                firstOfGroup = True
            lastId = msgId
        data.append(
            (user, counter / count(user.messages))
        )
    data.sort(key=lambda x: x[1], reverse=True)
    return data[:n]


@db_session
def floodRatio(user):
    lastId = -1
    counter = 0
    firstOfGroup = True
    for msgId in select(x.msgId for x in user.messages).order_by(1):
        if msgId == lastId+1:
            counter += 2 if firstOfGroup else 1
            firstOfGroup = False
        else:
            firstOfGroup = True
        lastId = msgId
    return counter / count(user.messages)


@db_session
def inactiveFor(days: int=7, allowEmptyStatus: bool=False):
    now = datetime.today().timestamp()
    statusFilter = ["left", "kicked"]
    if not allowEmptyStatus:
        statusFilter.append("")

    query = select(
        (user, int((now - max(select(x.date for x in user.messages))) / 86400))
        for user in User if user.lastStatus not in statusFilter)

    inactive = select((user, inDays) for (user, inDays) in query if inDays >= days)
    return inactive.order_by(-2)
