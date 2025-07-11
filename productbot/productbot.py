#!/usr/bin/python3

import sys
import os
import os.path
import configparser
import discord
import asyncio
import logging
import requests
import traceback
import time
from datetime import datetime
from decimal import Decimal

sys.path.insert(0,'/home/bios/productbot')
import reporting.productionChain as chain

global session
session = requests.session()

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True

logging.basicConfig(level=logging.WARNING)

class MyDiscordClient(discord.Client):

    product_channel = 1111111111111111111

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_task = self.loop.create_task(self.main_loop())
        self.bg_task = self.loop.create_task(self.background_tasks())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('--- PRODUCTBOT ENGAGED ---')

        members = await self.guilds[0].fetch_members().flatten()
        for member in members:
            if len(member.roles) == 1:
                continue
            for role in member.roles:
                if role.name.lower() == "guardian":
                    guardian_members.append(member.id)
                if role.name.lower() == "verified guardian":
                    if not member.id in guardian_members:
                        guardian_members.append(member.id)



    async def main_loop(self):
        await self.wait_until_ready()
        while True:
            await asyncio.sleep(1)


    async def background_tasks(self):
        await self.wait_until_ready()
        while True:
            try:
                await asyncio.sleep(180)
                await self.repopulate_guardian_members()

            except:
                print(traceback.format_exc())


    async def command_types(self, message):

        send_text = "**1**:\tRaw Materials\n**2**:\tRefined Materials\n**3**:\tRefined Metals\n**4**:\tComponents\n**5**:\tShip Components\n**6**:\tFinished Goods\n**7**:\tShips\n**8**:\tBuildings\n"
        await message.channel.send(send_text)


    async def command_category(self, message, category_code):

        special_characters = '!@#$%^&*()+?=,<>/"'
        if any(c in special_characters for c in category_code):
            await message.channel.send('product command supports only numeric characters')
            return

        if category_code.isnumeric():
            if int(category_code) == 1:
                category_name = 'Raw Material'
            elif int(category_code) == 2:
                category_name = 'Refined Material'
            elif int(category_code) == 3:
                category_name = 'Refined Metal'
            elif int(category_code) == 4:
                category_name = 'Component'
            elif int(category_code) == 5:
                category_name = 'Ship Component'
            elif int(category_code) == 6:
                category_name = 'Finished Good'
            elif int(category_code) == 7:
                category_name = 'Ship'
            elif int(category_code) == 8:
                category_name = 'Building'
            else:
                send_text = str(category_code) + " is not a valid type code\n"
                await message.channel.send(send_text)
                return

            print("getting products for %s" % category_name)
            products = chain.getProducts(category_name)
            send_text = "**Products from the " + category_name + " category**\n"
            for row in products:
                product_id = row['product_id']
                product_name = row['product_name']
                product_category = row['category']
                send_text = send_text + "**" + product_id + "**" + ":\t " + product_name + "\t**Category**: " + str(product_category) + "\n"

            if len(send_text) > 2000:
                n = 2000
                split_text_arr = [send_text[i:i+n] for i in range(0, len(send_text), n)]
                for text_chunk in split_text_arr:
                    await message.channel.send(text_chunk)
            else:
                await message.channel.send(send_text)


    async def command_inputs(self, message, product_id):

        special_characters = '!@#$%^&*()+?=,<>/"'
        if any(c in special_characters for c in product_id):
            await message.channel.send('input command supports only alphanumeric characters')
            return

        products = chain.findProducts(product_id)
        product_name = chain.getProductName(product_id)
        if product_name is None:
            await message.channel.send("product not found")
            return

        send_text = product_name + " with ID " + product_id + " is used in the following products\n"

        for row in products:
            output_id = row['product_id']
            output_name = row['product_name']
            output_type = row['product_type']
            output_complexity = row['product_score']
            output_category = row['category']
            output_mass = row['weight']
            output_volume = row['volume']
            output_quantized = row['quantized']
            send_text = send_text + "**" + str(output_id) + "**:\t" + output_name + "\t**|\tType:**\t" + output_type + "\t**|\tMass:** " + str(output_mass) + "\t**|\tVolume:** " + str(output_volume) + "\t**|\tFactor:** " + str(output_complexity) + "\t**|\tCategory:**\t" + str(output_category) + "\n"


        if len(send_text) > 2000:
            n = 2000
            split_text_arr = [send_text[i:i+n] for i in range(0, len(send_text), n)]
            for text_chunk in split_text_arr:
                await message.channel.send(text_chunk)
        else:
            await message.channel.send(send_text)


    async def command_search(self, message, search_string):

        search_results = None
        if len(search_string) < 3:
            await message.channel.send('Search requires at least 3 characters')
            return

        special_characters = '!@#$%^&*()-+?=,<>/"'
        if any(c in special_characters for c in search_string):
            await message.channel.send('Search supports only alphanumeric characters')
            return

        search_results = chain.searchProducts(search_string)

        if search_results is None:
            await message.channel.send('Nothing found')
            return

        if len(search_results) == 0:
            await message.channel.send('Nothing found')
            return

        send_text = "**Possible Matches**\n"
        for row in search_results:
            product_id = row['product_id']
            product_name = row['product_name']
            send_text = send_text + "**" + str(product_id) + "**" + ".\t" + product_name + "\n"

        await message.channel.send(send_text)


    async def command_product(self, message, product_id):

        special_characters = '!@#$%^&*()+?=,<>/"'
        if any(c in special_characters for c in product_id):
            await message.channel.send('product command supports only alphanumeric characters')
            return

        print("calling getComponents with %s" % product_id)
        product_data, production_chain = chain.getComponents(product_id)

        product_name = product_data['product_name']
        product_type = product_data['product_type']
        product_category = product_data['category']
        product_mass = product_data['weight']
        product_volume = product_data['volume']
        product_quantized = product_data['quantized']

        chains = len(production_chain)

        for row in production_chain:
            process_id = row['process_id']
            process_name = row['process_name']
            building_id = row['building_id']
            building_name = row['building_name']
            mAdalianHoursPerSR = row['mAdalianHoursPerSR']
            bAdalianHoursPerAction = row['bAdalianHoursPerAction']
            process_score = row['process_score']
            inputs_list = row['inputs']
            outputs_list = row['outputs']
            outputs_count = 0
            inputs_count = 0

            for inputs_row in inputs_list:
                inputs_count+=1

            for outputs_row in outputs_list:
                outputs_count+=1

            outputs_units = []

            for o_row in outputs_list:
                if o_row['product_id'] == product_id:
                    product_unitsPerSR = o_row['unitsPerSR']
                if len(o_row) > 1:
                    outputs_units.append({"output_id": o_row['product_id'], "output_name": o_row['product_name'], "output_type": o_row['product_type'], "output_mass": o_row['weight'], "output_volume": o_row['volume'], "unitsPerSR": o_row['unitsPerSR']})


            embed=discord.Embed(title=("**" + product_name + " produced through " + process_name + " has " + str(inputs_count) + " inputs**"))
            embed.add_field(name="Product ID", value=product_id, inline=True)
            embed.add_field(name="Product Type", value=product_type, inline=True)
            embed.add_field(name="Product Category", value=product_category, inline=True)
            embed.add_field(name="Building", value=building_name, inline=True)
            embed.add_field(name="Factor", value=(process_score + 1), inline=True)
            embed.add_field(name="Outputs Count", value=outputs_count, inline=True)
            embed.add_field(name="Mass", value=product_mass, inline=True)
            embed.add_field(name="Volume", value=product_volume, inline=True)
            embed.add_field(name="Quantized", value=product_quantized, inline=True)
            embed.add_field(name="UnitsPerSR", value=product_unitsPerSR, inline=True)
            embed.add_field(name="HoursPerSR", value=mAdalianHoursPerSR, inline=True)
            embed.add_field(name="HoursPerAction", value=bAdalianHoursPerAction, inline=True)

            send_text = ""
            for a_inputs_row in inputs_list:
                input_id = a_inputs_row['product_id']
                input_name = a_inputs_row['product_name']
                input_type = a_inputs_row['product_type']
                input_category = a_inputs_row['product_category']
                input_mass = a_inputs_row['product_weight']
                input_volume = a_inputs_row['product_volume']
                input_complexity = a_inputs_row['product_score']
                input_unitsPerSR = a_inputs_row['unitsPerSR']
                input_quantized = a_inputs_row['product_quantized']
                kilos = (int(input_mass) * int(input_unitsPerSR))
                if kilos >= 1000:
                    kilos = (kilos / 1000)
                    kilos = str(kilos) + " t"
                else:
                    kilos = str(kilos) + " k"

                if len(input_volume) > 0:
                    liters = (float(input_volume) * int(input_unitsPerSR))
                    liters = round(liters, 2)
                    if liters >= 1000:
                        liters = (liters / 1000)
                        liters = round(liters, 2)
                        liters = str(liters) + " m3"
                    else:
                        liters = str(liters) + " l"
                else:
                    liters = ''

                send_text = send_text + "**" + str(input_id) + "**: " + input_name + " **| Type:** " + input_type + " **| Factor:** " + str(input_complexity) + " **| Units:** " + str(input_unitsPerSR) + " **| Mass:** " + str(kilos) + " **| Volume:** " + str(liters) + "\n"

            if outputs_count > 1:
                new_send_text = "\n\n**" + process_name + " also produces " + str(outputs_count) + " additional outputs**\n"
                for a_outputs_row in outputs_units:
                    if a_outputs_row['output_id'] != product_id:
                        new_send_text = new_send_text + "**" + str(a_outputs_row['output_id']) + "**:\t" + a_outputs_row['output_name'] + "\t**|\tType:** " + a_outputs_row['output_type'] + "\t**|\tunitsPerSR:**\t" + str(a_outputs_row['unitsPerSR']) + "\n"

            squeezed_spaces = product_name.replace(" ", "")
            image = squeezed_spaces + ".v1.png"
            thumbnail_path = icons_path + "/" + squeezed_spaces + ".v1.png"
            if os.path.isfile(thumbnail_path):
                thumbnail = thumbnail_path
                thumb_file = discord.File(thumbnail, filename=image)
            else:
                thumbnail = None

            header_text = "\n========================================================================================\n"

            if thumbnail is not None:
                attachment = "attachment://" + image
                await message.channel.send(header_text)
                embed.set_thumbnail(url=attachment)
                await message.channel.send(file=thumb_file, embed=embed)
                if len(send_text) > 0:
                    await message.channel.send(send_text)
                if outputs_count > 1:
                    await message.channel.send(new_send_text)
            else:
                await message.channel.send(header_text)
                await message.channel.send(embed=embed)
                if len(send_text) > 0:
                    await message.channel.send(send_text)
                if outputs_count > 1:
                    await message.channel.send(new_send_text)


    async def command_help(self, message):

        if message:
            help_text = "**~product (~p) <product_id>** *Return production chain for product*\n" \
            + "**~category (~c) <category_id>** *Return all products in designated category_id*\n" \
            + "**~search (~s) <search_string>** *Return products matching search string*\n" \
            + "**~inputs (~i) <product_id>** *Return products that use product_id as an input*\n" \
            + "**~types (~t)** *Return category types and category type ids*\n" \
            + "**~help (~h)** *This help message*\n"

        await message.channel.send(help_text)


    async def repopulate_guardian_members(self):

        guardians = []
        for member in self.guilds[0].members:
            if len(member.roles) == 1:
                continue
            for role in member.roles:
                if role.name.lower() == "guardian":
                    guardians.append(member.id)
                if role.name.lower() == "verified guardian":
                    if not member.id in guardians:
                        guardians.append(member.id)
        global guardian_members
        guardian_members = guardians


    async def on_message(self, message):

        try:
            # Prevent bot from reacting to it's own messages
            if message.author == self.user: return

            if not message.content.lower().startswith('~'): return

            if message.guild:
                print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " *** BOT COMMAND: " + str(message.author.id) + " - " + message.author.name + " - Message: " + message.content)

            if not message.guild: # This is a DM
                print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " *** BOT DM: " + str(message.author.id)  + " - " + message.author.name + " - Message: " + message.content)
                vip = False
                if message.author.id in guardian_members:
                    vip = True
                if vip == False:
                    await message.channel.send('Only Guardians Allowed!')
                    return

            ## Non-guardians cannot proceed beyond this point
            if not message.author.id in guardian_members:
                return

            if message.content.lower().startswith('~product '):
                product_id = message.content.replace('~product ','').strip()
                await self.command_product(message, product_id)
                return

            if message.content.lower().startswith('~p '):
                product_id = message.content.replace('~p ','').strip()
                await self.command_product(message, product_id)
                return

            if message.content.lower().startswith('~inputs '):
                product_id = message.content.replace('~inputs ','').strip()
                await self.command_inputs(message, product_id)
                return

            if message.content.lower().startswith('~i '):
                product_id = message.content.replace('~i ','').strip()
                await self.command_inputs(message, product_id)
                return

            if message.content.lower().startswith('~types'):
                await self.command_types(message)
                return

            if message.content.lower().startswith('~t'):
                await self.command_types(message)
                return

            if message.content.lower().startswith('~category '):
                category_code = message.content.replace('~category ','').strip()
                await self.command_category(message, category_code)
                return

            if message.content.lower().startswith('~c '):
                category_code = message.content.replace('~c ','').strip()
                await self.command_category(message, category_code)
                return

            if message.content.lower().startswith('~search '):
                search_string = message.content.replace('~search ','').strip()
                await self.command_search(message, search_string)
                return

            if message.content.lower().startswith('~s '):
                search_string = message.content.replace('~s ','').strip()
                await self.command_search(message, search_string)
                return

            if message.content.lower().startswith('~help'):
                await self.command_help(message)
                return

            if message.content.lower().startswith('~h'):
                await self.command_help(message)
                return

        except:
            print(traceback.format_exc())


def main():

        global discord_token
        global productDiscordClient
        global product_channel
        global icons_path
        global guardian_members

        guardian_members = []

        # load config options and secrets
        config_file="/home/bios/productbot/productbot.conf"
        if os.path.exists(config_file):
                config = configparser.ConfigParser()
                config.read(config_file)
                discord_token = config.get('productbot', 'token')
                product_channel = config.get('productbot', 'product_channel')
                icons_path = config.get('icons', 'icons_path')
        else:
                raise Exception(config_file)

        productDiscordClient=MyDiscordClient(intents=intents)
        productDiscordClient.run(discord_token)

if __name__ == "__main__" : main()
