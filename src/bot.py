from datetime import datetime, time
import discord
from discord.ext import commands
from src.settings import TOKEN
from src.firebase import Island, find_home_island, is_registered, island_exists, highest_price

bot = commands.Bot(command_prefix='!')
slot_lookup = {"Mon AM": 0,
               "Mon PM": 1,
               "Tue AM": 2,
               "Tue PM": 3,
               "Wed AM": 4,
               "Wed PM": 5,
               "Thu AM": 6,
               "Thu PM": 7,
               "Fri AM": 8,
               "Fri PM": 9}
week = {0: "Mon ",
        1: "Tue ",
        2: "Wed ",
        3: "Thu ",
        4: "Fri "}


def get_current_slot():
    # returns current slot, but False if no slot available
    weekday = datetime.now().weekday()
    if weekday == 6:
        return False
    elif weekday == 7:
        return "Sunday"
    else:
        am = [time(8, 00), time(11, 59, 59)]  # AM hours are 8am to 12pm
        pm = [time(12, 00), time(22, 00)]  # PM hours are 12pm to 10pm
        current_time = datetime.now().time()
        if am[0] <= current_time <= am[1]:
            return week[weekday] + "AM"
        elif pm[0] <= current_time <= pm[1]:
            return week[weekday] + "PM"
        else:
            return False


def register_resident(ctx, island_name):
    author = str(ctx.message.author)
    if not is_registered(author):
        try:
            island = Island(island_name)
            if not island_exists(island_name):
                island.create()
            island.residents.append(author)
            island.push()
        except:
            return "Registration error, please complain loudly."
        return("User {} is now registered.".format(ctx.message.author.mention))
    else:
        return("User {} is already registered.".format(ctx.message.author.mention))


def get_prices(target):
    island_name = is_registered(str(target))
    if island_name:
        island = Island(island_name)
        island.pull()
        response_constructor = ["```Prices: \n"]
        response_constructor.append("Sunday purchase price: {} bells \n".format(island.purchase_price))
        for idx, (day, price) in enumerate(zip(list(slot_lookup.keys()), island.prices)):
            if idx % 2:
                response_constructor.append("{}: {} bells \n".format(day, price))
            else:
                response_constructor.append("{}: {} bells \t".format(day, price))
        return "".join(response_constructor[:]) + "```"
    else:
        return "User is not registered, please register with !register"


def set_price(ctx, price, desired_slot=None):
    author = str(ctx.message.author)
    author_island = is_registered(author)
    if author_island:
        island = Island(author_island)
        island.pull()
        if desired_slot:
            try:
                time_slot_idx = slot_lookup[desired_slot]
                island.prices[time_slot_idx] = int(price)
                island.push()
                return "{} set price for {} to {} bells.".format(ctx.message.author.mention, desired_slot, price)
            except KeyError:
                return "Invalid time slot specified, please use three letter day with AM or PM, i.e. Mon AM"
        time_slot = get_current_slot()
        if time_slot:
            time_slot_idx = slot_lookup[time_slot]
            island.prices[time_slot_idx] = int(price)
            island.push()
            return "{} set price for {} to {} bells.".format(ctx.message.author.mention, time_slot, price)
        return "Could not set price, Nook's Cranny is currently closed."
    else:
        return "User is not registered, please register with !register"


def best_price(ctx):
    person, price = highest_price(slot_lookup[get_current_slot()])
    discord_user = ctx.message.guild.get_member_named(person)
    return "Current best price is {} with a price of {} bells per turnip.".format(discord_user.mention, price)


@bot.command(name='turnip')
async def turnip(ctx):
    response = "Stalks!"
    await ctx.send(response)


@bot.command(name="register")
async def register_user(ctx, island: str):
    """ Register your username for tracking turnip prices, !register "island name" """
    response = register_resident(ctx, island)
    await ctx.send(response)


@bot.command(name="set_price")
async def set_turnip_price(ctx, price: int, desired_slot=None):
    """ Set price for current time slot """
    response = set_price(ctx, str(price), desired_slot)
    await ctx.send(response)


@bot.command(name="my_prices")
async def get_my_price(ctx):
    """ Return list of your current prices """
    response = get_prices(str(ctx.message.author))
    await ctx.send(response)


@bot.command(name="get_prices")
async def get_target_price(ctx, target: discord.User):
    """ Return list of target user prices """
    response = get_prices(str(target))
    await ctx.send(response)


@bot.command(name="best")
async def get_best_price(ctx):
    """ Return current highest price for turnips """
    response = best_price(ctx)
    await ctx.send(response)


@bot.command(name="my_island")
async def what_is_my_island(ctx):
    """ Find what island you are registered to. """
    my_island = find_home_island(ctx.message.author)
    if my_island:
        response = "Your home island is {}".format(my_island)
    else:
        response = "You are not registered to an island!"
    await ctx.send(response)


def run():
    bot.run(TOKEN)
