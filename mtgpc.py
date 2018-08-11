import itertools
import grequests
import re
import requests
import string
from currency_converter import CurrencyConverter
from telegram.ext import Updater, CommandHandler

def pricecheck(req, cardset = ""):
    spl = req.split()
    req = "http://gatherer.wizards.com/Pages/Search/Default.aspx?name="
    for w in spl:
        req += "+[{}]".format(w)
    response = requests.get(req)
    s = response.text
    if "Card/Details" not in response.url:
        i = s.find("?m") + 14
        cardid = s[i:i+s[i:].find('"')]
        response = requests.get("http://gatherer.wizards.com/Pages/Card/Details.aspx?printed=false&multiverseid=" + cardid)
        s = response.text
    t = re.search('(?<=<title>).+?(?=</title>)', s, re.DOTALL).group().strip()
    cardname = t[:t.find("(")-1]
    if cardset == "":
        cardset = t[t.find("(")+1:t.find(")")]
    newname = ""
    for c in cardname:
        if c not in string.ascii_letters and c != " ":
            pass
        else:
            newname += c
    c = CurrencyConverter('http://www.ecb.europa.eu/stats/eurofxref/eurofxref.zip')
    response = requests.get("https://www.mtggoldfish.com/price/{0}/{1}#paper".format(
        '+'.join(cardset.split()), '+'.join(newname.split())))
    s = response.text
    i = s.find("'>P") + 43
    cardprice = s[i:i+s[i:].find('<')]
    response = requests.get("https://www.mtggoldfish.com/price/{0}/{1}#paper".format(
        '+'.join(cardset.split())+":Foil", '+'.join(newname.split())))
    s = response.text
    i = s.find("'>P") + 43
    fcardprice = s[i:i+s[i:].find('<')]
    try:
        return cardname, cardset, c.convert(cardprice, 'USD', 'RUB'), c.convert(fcardprice, 'USD', 'RUB')
    except ValueError:
        return False, "Card not found"

def pc(bot, update):
    print(update.message.text)
    rsp = pricecheck(update.message.text)
    print(update.message.text)
    if not rsp[0]:
        update.message.reply_text("Card not found")
    else:
        update.message.reply_text("{}\n{}\nCard price: {} RUB\nFoil card price: {}".format(rsp[0], rsp[1], rsp[2], rsp[3]))

def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def main():
    updater = Updater(os.getenv('API_TOKEN', 'oops_no_token'))

    updater.dispatcher.add_handler(CommandHandler('pc', pc))
    updater.dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()

    print("Started!")
    updater.idle()

if __name__ == '__main__':
    main()
