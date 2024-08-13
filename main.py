"""
MIT License

Copyright (c) 2021 Nemika

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import discord, os, textwrap, io, traceback

from contextlib import redirect_stdout

from core.files import Data
from core import checks

from colorama import init, Style, Fore

from cogs.prefix import getPrefix

from discord.ext import commands

init(autoreset=True)

config = Data("config").yaml_read()

intents = discord.Intents.all(); intents.members = True

bot = commands.Bot(command_prefix=getPrefix, case_insensitive=True, help_command=None, intents=intents)

@bot.event
async def on_ready():
    print(f"{Fore.CYAN}[READY] {Style.RESET_ALL}Bot initialized!")

@checks.manager()
@bot.command(aliases=["e"])
async def eval(ctx, *, body: str):
    raw = False
    """Evaluates a code"""

    env = {
        'bot': bot,
        'ctx': ctx,
        'channel': ctx.message.channel,
        'author': ctx.message.author,
        'guild': ctx.message.guild,
        'message': ctx.message,
       }

    env.update(globals())

    stdout = io.StringIO()

    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

    try:
        exec(to_compile, env)
    except Exception as e:
        return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

    func = env['func']
    try:
        with redirect_stdout(stdout):
          ret = await func()
    except Exception:
        value = stdout.getvalue()
        await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
    else:
        value = stdout.getvalue()
        try:
            await ctx.message.add_reaction('\u2705')
        except:
            pass

        if ret is None:
            if value:
                if raw:
                  await ctx.send(f"{value}")
                else:
                  await ctx.send(f'```py\n{value}\n```')
        else:
            pass

@checks.manager()
@bot.command(hidden=True)
async def load(ctx, *, module):
    try:
      bot.load_extension(f"cogs.{module}")
    except commands.ExtensionError as e:
      await ctx.send(f'{e.__class__.__name__}: {e}')
    else:
      embed=discord.Embed(title=f"Loaded {str(module).capitalize()}", description=f"Successfully loaded cogs.{str(module).lower()}!", color=0x2cf818)
      await ctx.send(embed=embed)

@checks.manager()
@bot.command(hidden=True)
async def unload(ctx, *, module):
    try:
      bot.unload_extension(f"cogs.{module}")
    except commands.ExtensionError as e:
      await ctx.send(f'{e.__class__.__name__}: {e}')
    else:
      embed=discord.Embed(title=f"Unloaded {str(module).capitalize()}", description=f"Successfully unloaded cogs.{str(module).lower()}!", color=0xeb1b2c)
      await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"{Fore.CYAN}[READY] {Style.RESET_ALL}Bot initialized!")
    await load_extensions()  # Call the async function to load extensions

async def load_extensions():
    for file in [i for i in os.listdir("cogs") if i.endswith(".py")]:
        try:
            await bot.load_extension(f"cogs.{file[:-3]}")  # Await the load_extension
            print(f"{Fore.GREEN}[SUCCESS] {Style.RESET_ALL}Successfully loaded {Fore.YELLOW}{file}")
        except Exception as e:
            print(f"{Fore.RED}[ERROR] {Style.RESET_ALL}Failed to load {Fore.YELLOW}{file} {Style.RESET_ALL}due to an exception: {Style.DIM}{e}")

    dirs = [i for i in [x for x in os.walk("cogs")][0][1] if i.find(".") == -1]

    for folder in dirs:
        for file in [i for i in os.listdir(f"cogs/{folder}") if i.endswith(".py")]:
            try:
                await bot.load_extension(f"cogs.{folder}.{file[:-3]}")  # Await the load_extension
                print(f"{Fore.GREEN}[SUCCESS] {Style.RESET_ALL}Successfully loaded {Fore.YELLOW}{file}")
            except Exception as e:
                print(f"{Fore.RED}[ERROR] {Style.RESET_ALL}Failed to load {Fore.YELLOW}{file} {Style.RESET_ALL}due to an exception: {Style.DIM}{e}")

# Start the bot
bot.run(config["token"])
