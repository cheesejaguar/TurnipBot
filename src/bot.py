from datetime import datetime, time
import discord
from discord.ext import commands
from src.settings import TOKEN
from src.firebase import Island, fetch_islands, fetch_residents, find_home_island, is_registered, island_exists, highest_price, remove_resident

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
               "Fri PM": 9,
               "Sat AM": 10,
               "Sat PM": 11}
week = {0: "Mon ",
        1: "Tue ",
        2: "Wed ",
        3: "Thu ",
        4: "Fri ",
        5: "Sat "}


def get_current_slot():
    # returns current slot, but False if no slot available
    weekday = datetime.now().weekday()
    if weekday == 6:
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


def validate_price(price):
    """Validate turnip price is within reasonable range (1-999 bells)."""
    try:
        price_int = int(price)
        if price_int < 1:
            return None, "Price must be at least 1 bell."
        if price_int > 999:
            return None, "Price seems too high. Maximum is 999 bells."
        return price_int, None
    except (ValueError, TypeError):
        return None, "Invalid price. Please enter a number."


def register_resident(ctx, island_name):
    author = str(ctx.message.author)
    if not island_name or not island_name.strip():
        return "Please provide an island name. Usage: !register \"Island Name\""
    island_name = island_name.strip()
    if is_registered(author):
        return "User {} is already registered.".format(ctx.message.author.mention)
    try:
        island = Island(island_name)
        if not island_exists(island_name):
            island.create()
        else:
            island.pull()
        island.residents.append(author)
        island.push()
        return "User {} is now registered to {}.".format(ctx.message.author.mention, island_name)
    except Exception as e:
        print("Registration error for {}: {}".format(author, str(e)))
        return "Registration error. Please try again or contact an admin."


def unregister_resident(ctx):
    author = str(ctx.message.author)
    home_island = is_registered(author)
    if not home_island:
        return "You are not registered to any island."
    try:
        if remove_resident(author, home_island):
            return "{} has been unregistered from {}.".format(ctx.message.author.mention, home_island)
        return "Could not unregister. Please try again."
    except Exception as e:
        print("Unregistration error for {}: {}".format(author, str(e)))
        return "Unregistration error. Please try again or contact an admin."


def get_prices(target):
    island_name = is_registered(str(target))
    if island_name:
        island = Island(island_name)
        island.pull()
        print(len(island.prices))
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
    if not author_island:
        return "User is not registered, please register with !register"

    validated_price, error = validate_price(price)
    if error:
        return error

    island = Island(author_island)
    island.pull()
    if desired_slot:
        try:
            if desired_slot == "Sunday":
                island.purchase_price = validated_price
                island.push()
            else:
                time_slot_idx = slot_lookup[desired_slot]
                island.prices[time_slot_idx] = validated_price
                island.push()
            return "{} set price for {} to {} bells.".format(ctx.message.author.mention, desired_slot, validated_price)
        except KeyError:
            return "Invalid time slot specified, please use three letter day with AM or PM, i.e. Mon AM"
    time_slot = get_current_slot()
    if time_slot == "Sunday":
        island.purchase_price = validated_price
        island.push()
        return "{} set Sunday purchase price to {} bells.".format(ctx.message.author.mention, validated_price)
    elif time_slot:
        time_slot_idx = slot_lookup[time_slot]
        island.prices[time_slot_idx] = validated_price
        island.push()
        return "{} set price for {} to {} bells.".format(ctx.message.author.mention, time_slot, validated_price)
    return "Could not set price, Nook's Cranny is currently closed."


def best_price(ctx):
    current_slot = get_current_slot()
    if current_slot == "Sunday":
        return "Nook's Cranny doesn't buy turnips on Sunday - it's buying day!"
    if not current_slot:
        return "Nook's Cranny is currently closed (open 8am-10pm)."
    result = highest_price(slot_lookup[current_slot])
    if not result:
        return "No prices have been recorded for this time slot yet."
    person, price = result
    discord_user = ctx.message.guild.get_member_named(person)
    if discord_user:
        return "Current best price is {} with a price of {} bells per turnip.".format(discord_user.mention, price)
    return "Current best price is {} bells per turnip (from {}).".format(price, person)


def return_prediction_url(ctx):
    author = str(ctx.message.author)
    author_island = is_registered(author)
    if not author_island:
        return None
    island = Island(author_island)
    island.pull()
    base_url = "https://turnipprophet.io/?prices="
    combined_prices = [island.purchase_price] + island.prices
    price_array = [str(each) for each in combined_prices]
    query_string = ".".join(price_array).replace(".0.", "..").replace("nan", "")
    return (base_url + query_string).replace("=0.", "=.")


def reset_week_prices(ctx):
    """Reset all prices for a new week."""
    author = str(ctx.message.author)
    author_island = is_registered(author)
    if not author_island:
        return "User is not registered, please register with !register"
    island = Island(author_island)
    island.pull()
    island.prices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    island.purchase_price = 0
    island.push()
    return "{} reset all turnip prices for {}. Ready for a new week!".format(
        ctx.message.author.mention, author_island
    )


@bot.command(name='turnip')
async def turnip(ctx):
    response = "Stalks!"
    await ctx.send(response)


@bot.command(name="register")
async def register_user(ctx, island: str):
    """ Register your username for tracking turnip prices, !register "island name" """
    response = register_resident(ctx, island)
    await ctx.send(response)


@bot.command(name="unregister")
async def unregister_user(ctx):
    """ Unregister from your current island """
    response = unregister_resident(ctx)
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


@bot.command(name="list_islands")
async def list_islands(ctx):
    """ Lists all registered islands """
    island_list = fetch_islands()
    response = "**Current registered islands:** " + str(island_list)
    await ctx.send(response)


@bot.command(name="get_residents")
async def get_residents(ctx, island_name: str):
    """ Lists all residents of given island """
    residents = [ctx.message.guild.get_member_named(name).mention for name in fetch_residents(island_name)]
    response = "Residents of {} are {}".format(island_name, str(residents))
    await ctx.send(response)


@bot.command(name="predict")
async def predict_turnips(ctx):
    """ Provides a link to turnip price prediction """
    url = return_prediction_url(ctx)
    if url:
        response = "Link to your turnip price forecast: {}".format(url)
    else:
        response = "You are not registered to an island. Please register with !register first."
    await ctx.send(response)


@bot.command(name="reset_week")
async def reset_week(ctx):
    """ Reset all turnip prices for a new week """
    response = reset_week_prices(ctx)
    await ctx.send(response)


@bot.command(name="help_turnip")
async def help_turnip(ctx):
    """ Display help for all TurnipBot commands """
    help_text = """```
TurnipBot Commands:

Registration:
  !register "Island Name"  - Register to an island (creates if new)
  !unregister             - Leave your current island
  !my_island              - See which island you're registered to
  !list_islands           - List all registered islands
  !get_residents "Island" - See who lives on an island

Price Tracking:
  !set_price <price>           - Set price for current time slot
  !set_price <price> "Mon AM"  - Set price for specific slot
  !set_price <price> Sunday    - Set Sunday purchase price
  !my_prices                   - View your island's prices
  !get_prices @user            - View another user's prices
  !best                        - Find current best price
  !reset_week                  - Clear all prices for new week

Analysis:
  !predict                - Get TurnipProphet forecast link

Time Slots: Mon/Tue/Wed/Thu/Fri/Sat + AM or PM
Store Hours: 8am-12pm (AM) | 12pm-10pm (PM)
```"""
    await ctx.send(help_text)


def run():
    bot.run(TOKEN)
