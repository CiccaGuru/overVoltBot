from telepotpro.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


def prenota(domain, link_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🏷 Prenota offerta",
                             callback_data="prenotaLink#{}#{}".format(domain, link_id))
    ]])


def open_scontino(domain, link_id):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="➡️ Apri con Scontino",
                             url="tg://resolve?domain=Scontino_bot&start={}_{}".format(domain, link_id))
    ]])
