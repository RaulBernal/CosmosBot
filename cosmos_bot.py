#!/usr/bin/python
# -*- coding: utf-8 -*-
import datetime
import os
import botogram #pip3 install botogram2
import json
import requests


from config import token, path_to_daemon, url_api, bcna_address, operator_address, chain_id, priv_key, wallet_name, url_explorer, url_explorer2

# TODO
# url_api + /staking/pool  --> bonded_tokens

bot = botogram.create(token)
bot.about = "Telegram Bot for get info about BCNA chain. \nIf you found any bugs or have suggestions for new functionalities...\nPlease contact us!"
bot.owner = "BitCanna Community"
#========================
@bot.command("getrewards")
def getrewards_command(chat, message, args):
    """Get rewards replying to a given address"""
    address = message.reply_to_message.text
    url = url_api + 'distribution/delegators/' + address + '/rewards'
    try:
        response = requests.get(url,headers={"Accept": "application/json"},)
    except:
        conn_error = "An error occurred, try to put a valid address"
        chat.send(conn_error)
        print(message.sender.username+"\n"+conn_error)
    else:
        data = response.json()
        balance = data["result"]
        chat.send("The current reward is: \n```" + str(balance["total"]) + "```")
        chat.send(url)
        #print(message.sender.username+"\n"+address+"\n"+balance)


#==========================================================================
@bot.command("getblockcount")
def getblockcount_command(chat, message, args):
    """Check this to know if your fullnode-validator is synced"""
    get_block = os.popen(path_to_daemon + 'status').read()
    loaded_json = json.loads(get_block)
    print("Result:", loaded_json['sync_info']['latest_block_height'])
    block = str(loaded_json['sync_info']['latest_block_height'])
    chat.send("The current Block is "+block)
#==========================================================================
@bot.command("getbalance")
def getlist_command(chat, message, args):
    """This will show the balance of your config address"""
    msg = ""
    get_last = os.popen(path_to_daemon + 'query bank balances ' + bcna_address + ' -o json').read()
    loaded_json = json.loads(get_last)
    denom = loaded_json["denom"]
    amount = loaded_json["amount"]
    msg = 'You have ' + amount + denom
    chat.send(msg)
#==========================================================================
@bot.command("getvalidators")
def getmasternode_command(chat, message, args):
    """This will show the online VALIDATORS"""
    get_validators = os.popen(path_to_daemon + ' query staking validators -o json').read()
    loaded_json = json.loads(get_validators)
    print(loaded_json)
    msg = ""
    count = 0
    chat.send ("List of online VALIDATORS") 
    print ("List of online VALIDATORS")
    print ("==========================")
    for tx in loaded_json["validators"]:
        msg = msg + '*' + str(tx["description"]["moniker"]) + '* - Jailed: ' + str(tx["jailed"]) + '\nPOWER: ' + str(tx["delegator_shares"]) + '\n'
        count = count + 1
    print (msg + "\nTotal: " + str(count))
    chat.send(msg + "\nTotal: " + str(count))
#==========================================================================
@bot.command("explorer")  # sample to build a textfile and send it by telegram
def explorer_command(chat, message, args):
    chat.send ('Click at the URL: ' + url_explorer)
    get_address = os.popen(path_to_daemon + 'status | jq .validator_info.address | tr -d \'"\'').read()
    chat.send ('Click at the URL: ' + url_explorer2 + get_address["address"])

#==========================================================================
@bot.prepare_memory          #Automated actions
def init(shared):
    shared["subs"] = []

@bot.command("subscribe")
def subscribe_command(shared, chat, message, args):
    """Subscribe to the hourly daemon checking"""
    subs = shared["subs"]
    subs.append(chat.id)
    shared["subs"] = subs
    

@bot.timer(3600) #every hour
def checker(bot, shared):
    get_info = os.popen(path_to_daemon + 'status | jq .sync_info.catching_up').read()
    if get_info.find('false') == 0: #if found false is synced
        print('Daemon is running')
    else:    
         for chat in shared["subs"]:
            bot.chat(chat).send("Hey! your BCNA validator is down!")
         #something to do if is down
         #starting = os.popen(path_to_daemon + " start").read()
    get_power = os.popen(path_to_daemon + 'status | jq .validator_info.voting_power').read()
    if get_power.find('"0"') == 0: #if found false is jailed
        print('Validator is JAILED!!!')
        for chat in shared["subs"]:
            bot.chat(chat).send("Hey! your BCNA validator is JAILED!")

    else:    
        print('Validator have got POWER')

#==============================================================================

# This runs the bot, until ctrl+c is pressed
if __name__ == "__main__":
    bot.run() 
