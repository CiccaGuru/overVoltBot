# overVoltBot

This is the official bot for the YouTube channel [overVolt](https://www.youtube.it/overVoltOfficial).

## Make it work with your own bot
In order to make it work with your own bot you need to:
1. Install `pip3` using your package manager
2. Create a folder in which you'll download the repo folder
3. I suggest you to user `pipenv` or `virtualenv` to avoid conflicts (look for them on Google if you don't know how to use them)
4. Clone this repo with `$ git pull https://github.com/CiccaGuru/overVoltBot.git`
5. Install missing dependencies with `$ pip3 install -r requirements.txt`
6. Create the following files:
  * __TOKEN__ containing your bot token
  * __CHANNEL_ID__ containing your YouTube Channel ID (for YouTube integration)
  * __DEVELOPER_KEY__ containing your Google's Developer Key
7. Now you're ready!

## What does it do?

At the moment, it has the following functionalities:

### Referrals
Add a referral to a given link (`/referral` command) from Amazon, GearBest or Banggood, both in private and inline chats.

### YouTube search
Search on Youtube for an overVolt video (`/youtube` command), both in private and inline chats.

MORE COMING SOON!
