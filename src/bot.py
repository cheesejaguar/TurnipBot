from datetime import datetime, time
from discord.ext import commands
from src.settings import TOKEN
from src.firebase import Mayor, is_registered

bot = commands.Bot(command_prefix='!')

slot_lookup = {"Monday AM" : 0,
               "Monday PM" : 1,
               "Tuesday AM" : 2,
               "Tuesday PM" : 3,
               "Wednesday AM" : 4,
               "Wednesday PM" : 5,
               "Thursday AM" : 6,
               "Thursday PM" : 7,
               "Friday AM" : 8,
               "Friday PM" : 9}

week = {0: "Monday ",
        1: "Tuesday ",
        2: "Wednesday ",
        3: "Thursday ",
        4: "Friday ",
        7: "Sunday"}

def get_current_slot():
    # returns current slot, but False if no slot available
    weekday = datetime.now().weekday()
    if weekday == 6:
        return False
    elif weekday == 7:
        return "Sunday"
    else:
        am = [time(8, 00), time(11, 59, 59)] # AM hours are 8am to 12pm
        pm = [time(12, 00), time(22, 00)] # PM hours are 12pm to 10pm
        current_time = datetime.now().time()
        if am[0] <= current_time <= am[1]:
            return week[weekday] + "AM"
        elif pm[0] <= current_time <= pm[1]:
            return week[weekday] + "PM"
        else:
            return False

def create_mayor(ctx):
    author = str(ctx.message.author)
    if not is_registered(author):
        mayor = Mayor(author)
        mayor.push()
        return("User {} is now registered.".format(ctx.message.author.mention))
    else:
        return("User {} is already registered.".format(ctx.message.author.mention))

def get_prices(ctx):
    author = str(ctx.message.author)
    if  is_registered(author):
        mayor = Mayor(author)
        mayor.pull()
        response_constructor = ["Prices: \n"]
        for day, price in zip(list(slot_lookup.keys()), mayor.prices):
            response_constructor.append("{}: {} bells \n".format(day, price))
        return "".join(response_constructor[:])

def set_price(ctx, price):
    author = str(ctx.message.author)
    if  is_registered(author):
        mayor = Mayor(author)
        mayor.pull()
        time_slot = get_current_slot()
        if time_slot:
            time_slot_idx = slot_lookup[time_slot]
        mayor.prices[time_slot_idx] = int(price)
        print(mayor.prices)
        mayor.push()
        return "{} set price for {} to {} bells.".format(ctx.message.author.mention, time_slot, price)

@bot.command(name='turnip')
async def turnip(ctx, *, arg):
    response = "Stalks!".format(arg)
    await ctx.send(response)


@bot.command(name="register")
async def register_user(ctx):
    """ Register your username for tracking turnip prices """
    response = create_mayor(ctx)
    await ctx.send(response)

@bot.command(name="set_price")
async def set_turnip_price(ctx, *, price: int):
    """ Set price for current time slot """
    response = set_price(ctx, str(price))
    await ctx.send(response)

@bot.command(name="my_prices")
async def my_prices(ctx):
    """ Return list of your current prices """
    response = get_prices(ctx)
    await ctx.send(response)

def run():
    bot.run(TOKEN)
