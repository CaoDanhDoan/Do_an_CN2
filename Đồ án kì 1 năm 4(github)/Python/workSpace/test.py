import telegram 
bot = telegram.Bot(token='7553315989:AAHl1VDdCzPP3noX3A7TB0U0lPVW5FsLJ_A') 
if __name__ == '__main__': 
    print(bot.get_me()) 
    bot.send_message(chat_id="7762126946", text="Post ist da")
