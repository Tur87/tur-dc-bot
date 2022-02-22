#!/usr/bin/python3
''' Discord bot for Tur. '''
import os
import sys
import json
import discord
import logging as log
from lazylog import Logger
from discord.ext import commands as dcomm


current_dir = os.path.dirname(os.path.abspath(__file__))
term_specs = {"level": log.INFO, "splitLines": True, "pretty": True }
Logger.init(current_dir, termSpecs=term_specs)
log.getLogger("discord").setLevel(log.WARNING)
config = {}
prefix = '-'
with open(f'{current_dir}/config.json', encoding='utf-8') as cfgfh:
    config = json.loads(cfgfh.read())
if 'token' not in config:
    log.critical('Config is missing token')
    sys.exit(1)
token = config['token']
if 'prefix' in config:
    prefix = config['prefix']
intents = discord.Intents.default()
intents.members = True
dcbot = dcomm.Bot(command_prefix=prefix, intents=intents)

async def manage_voice_text_channels(member, guild, channel):
    ''' Create associated text channels and manage user access. '''
    await guild.fetch_channels()
    textchannel = None
    textname = channel.name.lower()
    members = 0
    for cmember in channel.members:
        if cmember.bot is True:
            continue
        members += 1
    for chan in guild.text_channels:
        if chan.category != channel.category or chan.name != textname:
            continue
        textchannel = chan
    if textchannel is None:
        musicbot = None
        mbcmd = None
        perms = discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
            create_instant_invite=False
        )
        # if '1' in textname:
        #     musicbot = await guild.fetch_member(836610895395946576)
        #     mbcmd = '!t1'
        # if '2' in textname:
        #     musicbot = await guild.fetch_member(876922094510833664)
        #     mbcmd = '!t2'
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                read_messages=False,
                send_messages=False,
                view_channel=False,
                create_instant_invite=False
            ),
            guild.me: perms
        }
        if musicbot is not None:
            overwrites[musicbot] = perms
        for cmember in channel.members:
            overwrites[cmember] = perms
        textchannel = await guild.create_text_channel(
            f'{textname}',
            overwrites=overwrites,
            category=channel.category,
            position=channel.position + 1,
            reason=f'VC {textname} in use'
        )
        if mbcmd is not None:
            await textchannel.send(
                content=f'To use the music bot, commands start with {mbcmd}'
            )
    if member not in channel.members:
        await textchannel.set_permissions(
            member,
            view_channel=False,
            read_messages=False,
            send_messages=False,
            create_instant_invite=False
            )
    else:
        await textchannel.set_permissions(
            member,
            view_channel=True,
            read_messages=True,
            send_messages=True,
            create_instant_invite=False
            )
    if members < 1:
        await textchannel.delete(
            reason='VC {textname} not in use'
        )
        return True
    return True

@dcbot.event
async def on_ready():
    ''' Once the bot is ready, log ready. '''
    log.info("%s has connected to Discord!", dcbot.user)
    await dcbot.change_presence(activity=discord.Game(name=config['activity'],type=1))

@dcbot.event
async def on_message(message):
    ''' Handle all messages except ones from the bot. '''
    if message.author == dcbot.user:
        return
    await dcbot.process_commands(message)
    return

'python' '/app/bot.py'
@dcbot.event
async def on_voice_state_update(member, before, after):
    ''' When a user changes voice state, check channels for neccessary action. '''
    log.info("%s updated from %s to %s", member, before, after)
    if before.channel is not None:
        await manage_voice_text_channels(member, before.channel.guild, before.channel)
    if after.channel is not None:
        await manage_voice_text_channels(member, after.channel.guild, after.channel)
    return


if __name__ == '__main__':
    dcbot.run(token)
