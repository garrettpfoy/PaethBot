import discord
from discord.ext.commands import Bot
from discord.ext import commands
from discord.voice_client import VoiceClient
import sqlite3 as sqlite
import asyncio
import sys
import os
import json
import random

#Bot settings: 
TOKEN = "EMPTY" #IMPORTANT DO NOT CHANGE UNLESS YOU KNOW WHAT YOU ARE DOING!
STATUS = "Live | !tv" #Sets bot 'playing' game
PREFIX = "!" #Sets the prefix you want to use throughout ALL commands
#Permissions: 
ADMIN_ROLEID_1 = "544002764804456449" #Get the ROLE id for any role you want to be able to use !admin commands
ADMIN_ROLEID_2 = "535214528531529758" #Get the ROLE id for any role you want to be able to use !admin commands
ADMIN_ROLEID_3 = "508724522610982923" #Get the ROLE id for any role you want to be able to use !admin commands
ADMIN_ROLEID_4 = "508723361979826192" #Get the ROLE id for any role you want to be able to use !admin commands
ADMIN_ROLEID_5 = "509712095651299339" #Get the ROLE id for any role you want to be able to use !admin commands
#other settings/placeholders
WEBSITE = "https://twitter.com/Lucky7Gaming" #Sets our website link for our !website command
TEAMSPEAK = "https://discord.gg/FGKkhMb" #Sets our TS link for !ts
BROADCAST_CHANNEL = "510607267352281098" #Sets channel bot will message when you use !admin broadcast {message}
UPDATE_CHANEL = "567863152826515467"

QUEUE = []
qCheck = "END"

HEIST = ["PaethBot#1265"]
TITLES = []

Client = discord.Client()
client = commands.Bot(command_prefix="!")  #Doesn't do anything, when I used a onMessage even not onCommand, may update if I find it makes a difference


@client.event
async def on_ready():
    global QUEUE
    print("Bot has been initialized and booted successfully. Version 1.4. Made by PickleZ") #On-Load message, please leave my name in here.
    print(" ")
    await client.change_presence(game=discord.Game(name=STATUS)) #Changes the bot's 'playing' game. Set this in settings on line 13
    
    channel = client.get_channel('421472023538302978')
    
    async for msg in client.logs_from(channel):
        await client.delete_message(msg)
    
        
    roles = await client.send_message(channel, "Welcome to Paeth's Community! In order to keep your experience as targeted as possible, please react to whichever emoji best fits your interests. \n \n<:fortnite:544232365313228800> - Fortnite \n\n<:csgo:544232345620709376> - CS:GO \n\n<:overwatch:544232310896328739> - Overwatch\n \n<:apex:544232279325540359> - Apex Legends \n\n<:cod:544232280374247453> - Call of Duty\n\n ")
    await client.add_reaction(roles, ":fortnite:544232365313228800")
    await client.add_reaction(roles, ":csgo:544232345620709376")
    await client.add_reaction(roles, ":overwatch:544232310896328739")
    await client.add_reaction(roles, ":apex:544232279325540359")
    await client.add_reaction(roles, ":cod:544232280374247453")
    

  
@client.event
async def on_member_join(member):
    with open('users.json', 'wt') as f: #This opens up our users.json file. I use it to store coins per user ID
        users = json.load(f)
    with open('users.json', 'r') as f:
        users = json.load(f)
    
    await update_data(users, member)
    
    with open('users.json', 'w') as f: #This opens up our users.json file. I use it to store coins per user ID
        json.dump(users, f)


@client.event
async def on_message(message): #I use the onMessage event to basically track commands. May change to onCommand if I find it is better
    with open('users.json', 'r') as f:
        users = json.load(f)
    global QUEUE
    global qCheck
    global TITLES
    
    await update_data(users, message.author)
    await checkChance(users, message.author)
    
    #Returns the website URL set in settings
    if message.content.upper() == str(PREFIX) + "WEBSITE" or message.content.upper() == str(PREFIX) + "TWITTER" or message.content.upper() == str(PREFIX) + "TWEET":
        await client.send_message(message.channel, "My twitter can be found at: " + str(WEBSITE))
        
    elif message.content.upper() == str(PREFIX) + "TV":
        await sendTVEmbed(message)
        await client.delete_message(message)
    
    elif message.content.upper() == str(PREFIX) + "EMAIL":
        await client.send_message(message.channel, "You can email me about **Business** concerns at: paethbusiness@gmail.com. _Note: Any non-business concerns can be done in DM's via twitter_!")
  
    #Returns the teamspeak URL(if that's what you call it) to the user
    elif message.content.upper() == str(PREFIX) + "DISCORD" or message.content.upper() == str(PREFIX) + "TEAMSPEAK" or message.content.upper() == str(PREFIX) + "VOICE":
        await client.send_message(message.channel, "Our discord invite link is: " + str(TEAMSPEAK))
   
    elif message.content.upper() == "!QUEUE START":
        await client.send_message(message.channel, "I have started a queue. Viewable in #queue")
        channel = client.get_channel("544239075474014258")
        reactable = await client.send_message(channel, "Beginning a new queue event. \n \n React with a :white_check_mark: to join the queue!")
        await client.add_reaction(reactable, "✅")
        qCheck == "START"
        print(QUEUE)
    
    elif message.content.upper().startswith("!QUEUE LIST"):
        args = message.content.split(" ")
        await client.send_message(message.channel, "I am gathering all users that have entered the queue, one minute...")
        string = "Users in queue: "
        for user in QUEUE:
            string = string + user + ", "
        await client.send_message(message.channel, string)
    
    elif message.content.upper().startswith("!QUEUE SELECT"):
        args = message.content.split(" ")
        selected = random.choice(QUEUE)
        QUEUE.remove(selected)
        await client.send_message(message.channel, "Randomly selecting one user from the Quee. The user is: <@" + str(selected) + ">!")
        
   #Basically calls on users.json and get's their coin count
    elif message.content.upper() == str(PREFIX) + "COINS" or message.content.upper() == str(PREFIX) + "BAL" or message.content.upper() == str(PREFIX) + "BALANCE" or message.content.upper() == str(PREFIX) + "COIN" or message.content.upper() == str(PREFIX) + "CREDITS":
        await client.send_message(message.channel, "Your current balance is {0} coins! Use !store to open up the shop, or use !gamble to gamble your coins{1}".format(users[message.author.id]['coins'], "!"))
    
    #Menu of commands for gambling
    elif message.content.upper() == str(PREFIX) + "GAMBLE" or message.content.upper() == str(PREFIX) + "BET":
        await client.send_message(message.channel, "You can use the following commands in order to gamble your coins: \n **!gamble coinflip {amount}** _Low risk, low reward_ \n **!gamble roulette {amount} {red/black/green}** _Medium risk, Medium reward_ \n **!gamble slots {amount}** _High risk, High reward_ ")
   
   #Coinflip gambling game. 50% chance. Doubles bet
    elif message.content.upper().startswith(str(PREFIX) + "GAMBLE COINFLIP"):
        args = message.content.split(" ")
        flipAmount = args[2]
        await runCoinFlip(users, message.author, flipAmount, message.channel)
    
    #Roulette gambling game. 47.5% on black or red, 5% on green heart <3
    elif message.content.upper().startswith(str(PREFIX) + "GAMBLE ROULETTE"):
        args = message.content.split(" ")
        betAmount = int(args[2])
        color = "{0}".format(str(args[3]))
        await runRoulleteRoll(users, message.author, betAmount, color, message.channel)
   
   #Slots gambling game, super low chances, 100x your bet
    elif message.content.upper().startswith(str(PREFIX) + "GAMBLE SLOTS"):
        args = message.content.split(" ")
        betAmount = int(args[2])
        await runSlotMachine(users, message.author, betAmount, message.channel)
   
   #Admin only command: Broadcasts 
    elif message.content.upper().startswith(str(PREFIX) + "ADMIN BROADCAST"):
        args = message.content.split(" ")
        server = message.server
        if await permissionCheck(message) == True:
            await client.send_message(server.get_channel(str(BROADCAST_CHANNEL)), "{0}".format(" ".join(args[2:])))
        else:
            await client.send_message(message.channel, "You don't have permission to use that admin command. You must be Moderator or higher.")
    
    #Admin only command: Ban a player. Currently offline until I can get a ban tracking system to see who bans who
    elif message.content.upper().startswith(str(PREFIX) + "ADMIN BAN "):
        if await permissionCheck(message) == True:
            args = message.content.split(" ")
            playerTotal = "{0}".format(str(args[2]))
            playerName = "{0}".format(str(playerTotal[2:-1]))
            days = "{0}".format(int(args[3]))
            reason = "{0}".format(str(args[4:]))
            await client.ban(playerName, days)
        else:
            await client.send_message(message.channel, "You don't have permission to use that admin command. You must be a Moderator or higher.")
    
    #Admin only command: Takes an amount of coins from a user
    elif message.content.upper().startswith(str(PREFIX) + "ADMIN COINS TAKE"):
        args = message.content.split(" ")
        if await permissionCheck(message) == True:
            playerTotal = "{0}".format(str(args[3]))
            playerName = playerTotal[2:-1]
            amount = args[4]
            users[playerName]['coins'] -= int(amount)
            await client.send_message(message.channel, "Removed {0} coins from player: <@{1}>".format(amount, playerName))
        else:
            await client.send_message(message.channel, "You don't have permission to use that admin command. You must be a Moderator or higher.")
    
    #Admin only command: Gives a set number of coins to a player
    elif message.content.upper().startswith(str(PREFIX) + "ADMIN COINS GIVE"):
        if await permissionCheck(message) == True:
            args = message.content.split(" ")
            playerTotal = "{0}".format(str(args[3]))
            playerName = playerTotal[2:-1]
            amount = args[4]
            users[playerName]['coins'] += int(amount)
            await client.send_message(message.channel, "Added {0} coins to player: <@{1}>".format(amount, playerName))
        
        else:
            await client.send_message(message.channel, "You don't have permission to use that admin command. You must be a Moderator or higher.")
        
    elif message.content.upper().startswith(str(PREFIX) + "ADMIN BANKHEIST START"):
        if await permissionCheck(message) == True:
            args = message.content.split(" ")
            joinIn = int(args[3])
            time = int(args[4])
            await startHeist(message, joinIn, time)

    #Admin only command: Gets the balance of a user (in coins)
    elif message.content.upper().startswith(str(PREFIX) + "ADMIN COINS GET"):
        if await permissionCheck(message) == True:
            args = message.content.split(" ")
            playerTotal = "{0}".format(str(args[3]))
            playerName = playerTotal[2:-1]
            await client.send_message(message.channel, "<@{0}>'s total coin count is: {1} coin(s).".format(playerName, users[playerName]['coins']))
        else:
            await client.send_message(message.channel, "You don't have permission to use that admin command. You must be a Moderator or higher.")
            
    elif message.content.upper().startswith(str(PREFIX) + "ADMIN PUSH"):
        args = message.content.split(" ")
        server = message.server
        if await permissionCheck(message) == True:
            await client.send_message(server.get_channel(str(UPDATE_CHANEL)), "**[+]** {0}".format(" ".join(args[2:])))
        else:
            await client.send_message(message.channel, "You don't have permission to use that admin command. You must be a Moderator or higher.")
            
    #Admin only command: Resets a user/players balance
    elif message.content.upper().startswith(str(PREFIX) + "ADMIN COINS RESET"):
        if await permissionCheck(message) == True:
            args = message.content.split(" ")
            playerTotal = "{0}".format(str(args[3]))
            playerName = playerTotal[2:-1]
            users[playerName]['coins'] = 0
            await client.send_message(message.channel, "Reset the balance of player: <@{0}>".format(playerName))
        else:
            await client.send_message(message.channel, "You don't have permission to use that admin command. You must be a Moderator or higher.")
       
    #Admin only command: Brings up help menu about our admin commands 
    elif message.content.upper().startswith(str(PREFIX) + "ADMIN") or message.content.upper().startswith(str(PREFIX) + "ADMIN HELP") or message.content.upper().startswith(str(PREFIX) + "ADMINS"):
        if await permissionCheck(message) == True:
            await adminHelp(message.channel)
        else:
            await client.send_message(message.channel, "You don't have permission to use that admin command. You must be a Moderator or higher.")

    elif message.content.upper().startswith(str(PREFIX) + "HELP") or message.content.upper().startswith(str(PREFIX) + "COMMANDS"):
        await sendHelpEmbed(message.channel)
    
    elif message.content.upper() == "!SPECS":
        await client.send_message(message.channel, ("My Specs: "))
    
    elif message.content.upper().startswith("!PROMO"):
        args = message.content.split(" ")
        promo = args[1:]
        channel = client.get_channel("539582520933744640")
        await client.send_message(message.channel, "I will be pushing your promo into our self-promo chat.")
        
        string = ""
        
        for word in promo:
            string = string + word + " "
        
        await sendEmbed(channel, string)
    
    elif message.content.upper().startswith(str(PREFIX) + "PLAYWITHME"): #!playwithme {title} {open or not} {description}
        args = message.content.split(" ")
        amtOfArgs = len(args)
        if amtOfArgs < 4:
            await client.send_message(message.channel, "Sorry, but in order to use this command you need to use it like this: `!playwithme {title} {open/closed} {description}")
        else:
            descriptionList = args[3:]
            string = ""
            for word in descriptionList:
                string = string + str(word) + " "
            
            title = str(args[1])
            
            server = message.server
            everyonePerm = discord.PermissionOverwrite(read_messages=False, send_messages=False)
            accessPerm = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            voiceEveryone = discord.PermissionOverwrite(view_channel=False, connect=False)
            voiceAccess = discord.PermissionOverwrite(view_channel=True, connect=True)
            
            
            voiceChannel = await client.create_channel(server, str(title), (server.default_role, voiceEveryone), (message.author, voiceAccess), type=discord.ChannelType.voice)
            textChannel = await client.create_channel(server, str(title), (server.default_role, everyonePerm), (message.author, accessPerm))
            
            
            await sendCreationEmbed(textChannel, message.author)
            TITLES.append(str(textChannel.name))
            
            
            status = str(args[2])
            if status.upper() == "OPEN":
                channelType = "OPEN"
            else:
                channelType = "CLOSED"
            
            if channelType == "OPEN":
                await joinMeEmbed(message, message.author, channelType, title, string, textChannel, voiceChannel)
                print("Tech works so yayif this works :P")
            
            
        
        
    with open('users.json', 'w') as f: 
        json.dump(users, f)

  

@client.event
async def on_channel_create(channel):
    await asyncio.sleep(3)
    global TITLES
    checker = channel.name
    print(channel.name)
    
    for title in TITLES:
        if title == str(checker) and str(channel.type) == "text":
            await sixtyClosure(channel)



@client.event
async def on_reaction_add(reaction, user):
    with open('users.json', 'r') as f:
        users = json.load(f)

    global QUEUE
    global joinIn
    await asyncio.sleep(1)

    print(str(reaction.emoji))
    if str(reaction.emoji) == "<:csgo:544232345620709376>":
        role = discord.utils.get(user.server.roles, name="CS:GO")
        await client.add_roles(user, role)
        print("Added role CS:GO to user: " + str(user))
    if str(reaction.emoji) == "<:overwatch:544232310896328739>":
        role = discord.utils.get(user.server.roles, name="Overwatch")
        await client.add_roles(user, role)
        print("Added role Overwatch to user: " + str(user))
    if str(reaction.emoji) == "<:apex:544232279325540359>":
        role = discord.utils.get(user.server.roles, name="Apex Legends")
        await client.add_roles(user, role)
        print("Added role Apex Legends to user: " + str(user))
    if str(reaction.emoji) == "<:cod:544232280374247453>":
        role = discord.utils.get(user.server.roles, name="Call of Duty")
        await client.add_roles(user, role)
        print("Added role Call of Duty to user: " + str(user))
    if str(reaction.emoji) == "<:fortnite:544232365313228800>":
        role = discord.utils.get(user.server.roles, name="Fortnite")
        await client.add_roles(user, role)
        print("Added role Fortnite to user: " + str(user))
    if str(reaction.emoji) == "✅":
        print("User " + str(user) + " has just joined the queue.")
        QUEUE.append(str(user))
        if str(QUEUE[0]) == "PaethBot#1265":
            QUEUE.remove(QUEUE[0])
        else:
            await client.send_message(user, "You have been added to the queue!")
            print(QUEUE)
    if str(reaction.emoji) == "💰":
        print("User " + str(user) + " has just attempted to join the bank heist")
        if str(user) == "PaethBot#1265":
            print("Removing Bot's Eligibility")
        else:
            tempCoins = users[user.id]['coins']
            if tempCoins < 150:
                await client.send_message(user, "Sorry, but your heist-mates saw that you didn't have enough coins to join them, and kicked you to the curb!")
            else:
                for name in HEIST:
                    if str(name) == str(user):
                        print("User already in the queue")
                    else:
                        await client.send_message(user, "Congrats! Your heist-mates accepted your join request and took your 150 coins!")
                        await client.send_message(user, "Check in on the bankheist channel to see progress")
                        users[user.id]['coins'] -= 150
                        HEIST.append(str(user))

                

    with open('users.json', 'w') as f:
        json.dump(users, f)      


async def sendTVEmbed(message):
    embed = discord.Embed(
        title = "Twitch - ImPaeth",
        description = "https://twitch.tv/impaeth",
        colour = discord.Color.blue()
    )
    embed.set_footer(text = "Check out my stream! I'd love to see you there ;)")
    embed.set_author(name = "ImPaeth")
    embed.set_thumbnail(url="https://s3.amazonaws.com/peoplepng/wp-content/uploads/2018/10/30161140/Live-PNG-Images.png")
    embed.add_field(name = "How to watch: ", value = "Want to watch me? It's quite simple. Simply navigate to https://twitch.tv/impaeth and make sure to hit that follow button so you can always see when I go live!")
    embed.add_field(name = "How to subscribe: ", value = "Love watching me? If you wish to subscribe, navigate to my page, and go to the top right of the embeded video stream. There should be a 'subscribe' button, click that and follow the instructions!")
    embed.add_field(name = "How to donate: ", value = "Want to help me reach my goals? You can donate to me here: https://streamlabs.com/impaeth")
    
    sendMessage = await client.send_message(message.channel, embed=embed)


async def update_data(users, user): #Updates data if is new user
    if not user.id in users:
        users[user.id] = {}
        users[user.id]['coins'] = 0

async def checkChance(users, user): #Checks chance of a user if they are getting a coin on that message. !store will eventually increase chances
    outcome = ['point', 'nopoint', 'nopoint', 'nopoint', 'nopoint', 'nopoint', 'nopoint', 'nopoint']
    chance = random.choice(outcome)
    if chance == 'point':
        users[user.id]['coins'] += 1
    
async def sendCreationEmbed(channel, user):
    embed = discord.Embed(
        title = "Play-With-Me Instructions: " + "{0}".format(str(user)),
        description = "Welcome to your very own channel for whatever you need! \n\nIf you want to know what's up with YOUR channels test out our custom menu !pwm menu\n\nThanks for being a member of this community!\n\nNote: These channels close after 60 minutes",
        colour = discord.Color.blue()
        )
        
    sendMessage = await client.send_message(channel, embed=embed)
    sendSecondMessage = await client.send_message(channel, "<@{0}>".format(str(user.id)))

async def sendEmbed(channel, string):
    embed = discord.Embed(
        title = "PROMO",
        description = str(string),
        colour = discord.Color.blue()
        )
    message = await client.send_message(channel, embed=embed)


async def sixtyClosure(channel):
    global TITLES
    minsLeft = 60
    
    embed = discord.Embed(
        title = "Play-With-Me Countdown",
        description = str(minsLeft),
        colour = discord.Color.blue()
    )
    message = await client.send_message(channel, embed=embed)
    await client.pin_message(message)
    print(str(channel.name))
    
    for min in range(1, (minsLeft + 1)):
        minsLeft = minsLeft - 1
        await asyncio.sleep(60)
        embed = discord.Embed(
            title = "Play-With-Me Countdown",
            description = str(minsLeft),
            colour = discord.Color.blue()
        )
        await client.edit_message(message, embed=embed)
    
    mes = await client.send_message(channel, "Closing both the voice channel, and text channel associated with this playme! Thanks for being a part of this community!")
    await asyncio.sleep(5)
    voiceName = str(channel.name)
    
    server = mes.server
    
    
    for channel in server.channels:
        if str(channel.name) == voiceName:
            await client.delete_channel(channel)
    
                
    
    
        

async def startHeist(message, start, count):
    with open('users.json', 'r') as f:
        users = json.load(f)
        
    global HEIST
    server = message.server
    temp = []
    HEIST = []
    channel = client.get_channel("568081038014808094")
    chance = random.randrange(1, 101)
    editor = await client.send_message(channel, "Starting a bankheist, who wants in? \n\n Information:\nBuy In Amount: $150 coins\nTime until start: " + str(count) + " seconds \nChance of Success: " + str(chance) + "\n\n To enter and pay the amount, please click the :moneybag: emoji!")
    await client.add_reaction(editor, "💰")
    for second in range(1, count + 1):
        await asyncio.sleep(1)
        count = count - 1
        editor = await client.edit_message(editor, "Starting a bankheist, who wants in? \n\n Information:\nBuy In Amount: $150 coins\nTime until start: " + str(count) + " seconds \nChance of Success: " + str(chance) + "\n\n To enter and pay the amount, please click the :moneybag: emoji!")
        
        
        
    heistString = ""
    for player in HEIST:
        heistString = heistString + str(player) + ", "
        
    
    await client.send_message(channel, "That's it! The heist has started, the members that have joined us are: " + heistString + ". We are entering the bank now...")
    await asyncio.sleep(2)
    for posChance in range(1, chance + 1):
        temp.append("SUCCESS")
    for negChance in range(1, 100 - chance):
        temp.append("FAILURE")
    outcome = random.choice(temp)
    await client.send_message(channel, "You climb the stairs, and BLAMO! the sirens go off, you have only a limited time to complete this heist!")
    await asyncio.sleep(1)
    if outcome == "SUCCESS":
        await client.send_message(channel, "You get into the vault, and, and, JACKPOT! You hit it rich!")
        await asyncio.sleep(1)
        await client.send_message(channel, "You grabbed as much as you could, and you hit the road!")
        await asyncio.sleep(2)
        earnings = random.randrange(1, 1000)
        await client.send_message(channel, "Once you got back to the rendevouz point, you tallied up all of your earnings to be: " + str(earnings) + " each!")
        
        user = server.get_member_named(str(player))
        
        for player in HEIST:
            users[user.id]['coins'] += int(earnings)
    else:
        await client.send_message(channel, "You get into the vault, and, and, SURPRISE! The cops were there, you try and run out the side door!")
        await asyncio.sleep(1)
        await client.send_message(channel, "But the cops were there too! You were caught and went to jail!")

    with open('users.json', 'w') as f:
        json.dump(users, f)     
    


async def runCoinFlip(users, user, betAmount, channel): #Runs our coin flip gambling game and adjusts balance
    if int(betAmount) > int(users[user.id]['coins']):
        await client.send_message(channel, "Sorry, but you don't have enough coins to gamble that much! Total coins: {0}{1}".format(str(users[user.id]['coins']), "."))
    else:
        flipPossibleOutcome = ['Loose', 'Win']
        flipOutcome = random.choice(flipPossibleOutcome)
        if flipOutcome.upper() == "WIN":
            users[user.id]['coins'] += int(betAmount) * 2
            await client.send_message(channel, "Congrats! You won your cointoss! You doubled your bet of {0}! Your new balance: {1}".format(str(betAmount), str(users[user.id]['coins'])))
        elif flipOutcome.upper() == "LOOSE":
            users[user.id]['coins'] -= int(betAmount)
            await client.send_message(channel, "Oh no! You lost your cointoss and your bet of {0}! Your new balance is: {1}".format(str(betAmount), str(users[user.id]['coins'])))
            
            
            
async def twitchPing(userID, twitchName):
    await client.send_message(userID, "Hello, the twitch user '" + twitchName + "' has used your discord ID to try and confirm an account sync.")


async def joinMeEmbed(message, user, channelType, title, tdescription, addToChannel, voiceChannel):
    channel = client.get_channel("545375112250261531")
    
    embed = discord.Embed(
        title = str(user) + "'s JoinMe",
        description = str(tdescription),
        colour = discord.Color.blue()
    )
    embed.set_footer(text='To request/join ' + str(user) + "'s JoinMe, simply react with 🎮")
    
    heckin = await client.send_message(channel, embed=embed)
    
    await client.add_reaction(heckin, "🎮")
    
    x = 1
    
    while x != 0:
        res = await client.wait_for_reaction("🎮")
    
        accessPerm = discord.PermissionOverwrite(view_channel=True, connect=True)
        textAccessPerm = discord.PermissionOverwrite(send_messages=True, read_messages=True)
    
        print("Attempting to add user: " + str(res.user) + " to channel.")
        await client.edit_channel_permissions(addToChannel, res.user, textAccessPerm)
        await client.edit_channel_permissions(voiceChannel, res.user, accessPerm)
        print("Success! User added!")
    
        await sendAddedEmbed(addToChannel, res.user)
    

    
    
async def sendAddedEmbed(channel, user):
    embed = discord.Embed(
        title = "Added user!",
        description = "I have added the user: " + "<@{0}>".format(user.id),
        colour = discord.Color.blue()
    )
    
    message = await client.send_message(channel, embed=embed)



async def runRoulleteRoll(users, user, betAmount, color, channel): #Runs the Roulette gambling game and then adjusts balance
    if int(betAmount) > int(users[user.id]['coins']):
        await client.send_message(channel, "Sorry but you don't have enough coins to gamble that much! Total coins: {0}{1}".format(str(users[user.id]['coins']), "."))
    elif color.upper() == "RED" or color.upper() == "GREEN" or color.upper() == "BLACK":
        chance = random.randint(1, 1000)
        
        if chance > 0 and chance <= 475 and color.upper() == "RED":
            users[user.id]['coins'] += int(betAmount) * 2
            await client.send_message(channel, "Congrats! The roulette table rolled the color :red_circle: which means you won! Your initial bet of {0} has just increased your balance to be now: {1}{2}".format(str(betAmount), str(users[user.id]['coins']), "!"))
        elif chance > 0 and chance <= 475 and color.upper() == "BLACK":
            users[user.id]['coins'] -= int(betAmount)
            await client.send_message(channel, "Oh no! The roulette table rolled :red_circle: but you bet on black! You lost your bet of {0}{1}".format(str(betAmount), "!"))
        elif chance > 0 and chance <= 475 and color.upper() == "GREEN":
            users[user.id]['coins'] -= int(betAmount)
            await client.send_message(channel, "Oh no! The roulette table rolled :red_circle: but you bet on green! You lost your bet of {0}{1}".format(str(betAmount), "!"))
        elif chance > 475 and chance <= 950 and color.upper() == "RED":
            users[user.id]['coins'] -= int(betAmount)
            await client.send_message(channel, "Oh no! The roulette table rolled :black_circle: but you bet on red! You lost your bet of {0}{1}".format(str(betAmount), "!"))
        elif chance > 475 and chance <= 950 and color.upper() == "BLACK":
            users[user.id]['coins'] += int(betAmount) * 2
            await client.send_message(channel, "Congrats! The roulette table rolled the color :black_circle: which means you won! Your initial bet of {0} has just increased your balance to be now: {1}{2}".format(str(betAmount), str(users[user.id]['coins']), "!"))
        elif chance > 475 and chance <= 950 and color.upper() == "GREEN":
            users[user.id]['coins'] -= int(betAmount)
            await client.send_message(channel, "Oh no! The roulette table rolled :black_circle: but you bet on green! You lost your bet of {0}{1}".format(str(betAmount), "!"))
        elif chance > 950 and chance <= 1000 and color.upper() == "RED":
            users[user.id]['coins'] -= int(betAmount)
            await client.send_message(channel, "Oh no! The roulette table rolled :green_heart: but you bet on red! You lost your bet of {0}{1}".format(str(betAmount), "!"))
        elif chance > 950 and chance <= 1000 and color.upper() == "BLACK":
            users[user.id]['coins'] -= int(betAmount)
            await client.send_message(channel, "Oh no! The roulette table rolled :green_heart: but you bet on black! You lost your bet of {0}{1}".format(str(betAmount), "!"))
        elif chance > 950 and chance <= 1000 and color.upper() == "GREEN":
            users[user.id]['coins'] += int(betAmount) * 10
            await client.send_message(channel, "Congrats! The roulette table rolled the color :green_heart: which means you won! Your initial bet of {0} has just increased your balance to be now: {1}{2}".format(str(betAmount), str(users[user.id]['coins']), "!"))
    else:
        await client.send_message(channel, "Whoops, something went wrong. Make sure you include an amount, and then the color of your choice.")


async def runSlotMachine(users, user, betAmount, channel): #Runs the slot machine gambling game then adjusts user balance
    emojis = [':cherries:', ':seven:', ':lemon:', ':moneybag:', ':bell:']
    emoji1 = random.choice(emojis)
    emoji2 = random.choice(emojis)
    emoji3 = random.choice(emojis)
    
    if int(betAmount) > int(users[user.id]['coins']):
        await client.send_message(channel, "Whoops, you don't have enough money to bet that much. Your balance is currently {0} coins".format(str(users[user.id]['coins'])))
        
    elif emoji1 == emoji2 and emoji2 == emoji3:
        users[user.id]['coins'] += int(betAmount) * 100
        await client.send_message(channel, "Spinning... \n Spinning... \n Spinning...")
        await client.send_message(channel, "{0} {1} {2}".format(emoji1, emoji2, emoji3))
        await client.send_message(channel, "Congrats! You spun three {0}{1}{2}'s in a row! Your bet was {3} and thus increased your balance by {4}. Your current updated balance: {5}".format(emoji1, emoji2, emoji3, betAmount, int(betAmount) * 100, str(users[user.id]['coins'])))
    
    else:
        users[user.id]['coins'] -= int(betAmount)
        await client.send_message(channel, "Spinning... \n  Spinning... \n   Spinning...")
        await client.send_message(channel, "{0} {1} {2}".format(emoji1, emoji2, emoji3))
        await client.send_message(channel, "Oh no! Your spin wasn't a winner. Your balance went down by your bet of {0}. Your updated balance is: {1}".format(betAmount, str(users[user.id]['coins'])))





async def adminHelp(channel): #Function to send the admin embed link
    embed = discord.Embed(
        title = '!admin ban [player]',
        description = 'Permenantly bans a player',
        colour = discord.Color.blue()
    )
    embed.set_footer(text='bot by: PickleZ')
    embed.set_author(name='PaethBot v1.1')
    embed.add_field(name='!admin broadcast [message]', value='Announces your message to the #announcements channel', inline=False)
    embed.add_field(name='!admin coins give [player] [amount]', value='Gives a player a set amount of coins', inline=False)
    embed.add_field(name='!admin coins take [player] [amount]', value='Takes a certain amount of coins away from a player', inline=False)
    embed.add_field(name='!admin coins reset [player]', value='Takes a certain amount of coins away from a player', inline=False)
    
    await client.send_message(channel, embed=embed)

async def ticketCountdown(author, channel, timeLeft):
    global lastEmbed
    timer = 60
    embed = discord.Embed(
        colour = discord.Color.red()
    )
    embed.set_author(name="Ticket Closing in: {0}".format(str(timeLeft)))
    
    return embed
    
        
async def sendHelpEmbed(channel): #Function to send the help embed link
    embed = discord.Embed(
        title = 'Help Commands: ',
        description = " ",
        colour = discord.Color.blue()
    )
    embed.set_footer(text="bot by: PickleZ")
    embed.set_author(name="PaethBot v1.4")
    embed.add_field(name="!gamble", value="Use this command to get all gamble sub-commands", inline=False)
    embed.add_field(name="!coins", value="Use this command to keep track of all your coins!", inline=False)
    embed.add_field(name="!admin", value ="Use of this command is only possible if you have the correct permissions, brings up admin GUI.", inline=False)
    embed.add_field(name="!twitter", value="Use of this command brings up our website information", inline=False)
    embed.add_field(name="!discord", value="Use of this command brings up our teamspeak information", inline=False)
    embed.add_field(name="!store", value="Use of this command brings up our store sub-commands", inline=False)
    
    await client.send_message(channel, embed=embed)

async def permissionCheck(message): #Permission check system for all roles defined in settings
    if ADMIN_ROLEID_1 in [role.id for role in message.author.roles]:
        return True
    elif ADMIN_ROLEID_2 in [role.id for role in message.author.roles]:
        return True
    elif ADMIN_ROLEID_3 in [role.id for role in message.author.roles]:
        return True
    elif ADMIN_ROLEID_4 in [role.id for role in message.author.roles]:
        return True
    elif ADMIN_ROLEID_5 in [role.id for role in message.author.roles]:
        return True
    
client.run(TOKEN)
