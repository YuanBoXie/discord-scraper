"""
@author:  Dracovian
@date:    2021-02-10
@license: WTFPL
"""

"""
datetime.timedelta: Used to subtract an entire day from the current one.
datetime.datetime:  Used to retrieve the current day.
"""
from ast import parse
from datetime import timedelta, datetime

"""
module.DiscordScraper: Used to access the Discord Scraper class functions.
"""
from module import DiscordScraper

"""
os._exit: Used to exit the script.
"""
from os import _exit as exit

"""
module.DiscordScraper.loads: Used to access the json.loads function documented in the DiscordScraper class file.
"""
from module.DiscordScraper import loads

def getLastMessageGuild(scraper, guild, channel):
    """
    Use the official Discord API to retrieve the last publicly viewable message in a channel.
    :param scraper: The DiscordScraper class reference that we will be using.
    :param guild: The ID for the guild that we're wanting to scrape from.
    :param channel: The ID for the channel that we're wanting to scrape from.
    """
    # Docs: https://discord.com/developers/docs/resources/channel#get-channel-messages
    # API function for retrieving channel messages (we don't care about the 100 message limit this time).
    lastmessage = 'https://discord.com/api/{0}/channels/{1}/messages?limit=1'.format(scraper.apiversion, channel)
    # Update the HTTP request headers to set the referer to the current guild channel URL.
    scraper.headers.update({'Referer': 'https://discord.com/channels/{0}/{1}'.format(guild, channel)})

    try:
        # [ERROR] [WinError 10060] 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。
        response = DiscordScraper.requestData(lastmessage, scraper.headers) 
        # If we returned nothing then return nothing.
        if response is None: return None
        
        # Read the response data and convert it into a dictionary object.
        data = loads(response.read())

        # Retrieve the snowflake of the post and convert it into a timestamp.
        timestamp = DiscordScraper.snowflakeToTimestamp(int(data[0]['id']))

        # Return the datetime object from the given timestamp above.
        return datetime.fromtimestamp(timestamp)

    except Exception as ex:
        print(ex)

def startDM(scraper, alias, channel, day=None):
    """
    The initialization function for the scraper script to grab direct message contents.
    :param scraper: The DiscordScraper class reference that we will be using.
    :param alias: The named alias for the direct message.
    :param channel: The ID for the direct message we're wanting to scrape from.
    :param day: The datetime object for the day that we're wanting to scrape.
    """

    # TODO: I still need to get around to implementing DM scraping, hopefully I can figure out a method of getting the true DM url from a user ID/Snowflake value to make things easier to configure.
    pass

def startGuild(scraper, guild, channel, day=None):
    """
    The initialization function for the scraper script.
    :param scraper: The DiscordScraper class reference that we will be using.
    :param guild: The ID for the guild that we're wanting to scrape from.
    :param channel: The ID for the channel that we're wanting to scrape from.
    """

    # Get the snowflakes for the current day.
    snowflakes = DiscordScraper.getDayBounds(day.day, day.month, day.year)

    # Generate a valid URL to the undocumented API function for the search feature.
    search = 'https://discord.com/api/{0}/channels/{1}/messages/search?min_id={2}&max_id={3}&{4}'.format(scraper.apiversion, channel, snowflakes[0], snowflakes[1], scraper.query)

    # Update the HTTP request headers to set the referer to the current guild channel URL.
    scraper.headers.update({'Referer': 'https://discord.com/channels/{0}/{1}'.format(guild, channel)})

    try:
        # Generate the guild name.
        if scraper.guildname == None:
            scraper.grabGuildName(guild)

        # Generate the channel name.
        if scraper.channelname == None:
            scraper.grabChannelName(channel)

        # Generate the scrape folders. TODO: Re-enable this before pushing to the public.
        scraper.createFolders()

        # Grab the API response for the search query URL.
        response = DiscordScraper.requestData(search, scraper.headers)

        # If we returned nothing then continue on to the previous day.
        if response is None:

            # Set the day to yesterday.
            day += timedelta(days=-1)

            # Recursively call this function with the new day.
            startGuild(scraper, guild, channel, day)
        
        # Read the response data.
        data = loads(response.read().decode('iso-8859-1'))
        
        # Get the number of posts.
        posts = data['total_results']
        
        # Determine if we have multiple offsets.
        if (posts > 25):
            pages = int(posts / 25) + 1
            
            for page in range(2, pages + 1):
                # Generate a valid URL to the undocumented API function for the search feature.
                search = 'https://discord.com/api/{0}/channels/{1}/messages/search?min_id={2}&max_id={3}&{4}&offset={5}'.format(scraper.apiversion, channel, snowflakes[0], snowflakes[1], scraper.query, 25 * (page - 1))

                # Update the HTTP request headers to set the referer to the current guild channel URL.
                scraper.headers.update({'Referer': 'https://discord.com/channels/{0}/{1}'.format(guild, channel)})

                try:

                    # Grab the API response for the search query URL.
                    response = DiscordScraper.requestData(search, scraper.headers)
                    
                    # Read the response data.
                    data2 = loads(response.read().decode('iso-8859-1'))
                    
                    # Append the messages from data2 into data.
                    for message in data2['messages']:
                        data['messages'].append(message)
                        
                except:
                    pass
            

        # Cache the JSON data if there's anything to cache (don't fill the cache directory with useless API response junk).
        if posts > 0:
            scraper.downloadJSON(data, day.year, day.month, day.day)

        # Check the mimetypes of the embedded and attached files.
        scraper.checkMimetypes(data)
        
    except:
        pass

    # Set the day to yesterday.
    day += timedelta(days=-1)
    
    # Return the new day
    return day
        
def start(scraper, guild, channel, day=None):
    """
    The initialization function for the scraper script.
    :param scraper: The DiscordScraper class reference that we will be using.
    :param guild: The ID for the guild that we're wanting to scrape from.
    :param channel: The ID for the channel that we're wanting to scrape from.
    """
    
    # Determine if we've already initialized the DiscordScraper class, if so then clean it out and re-initialize a new one.
    if scraper is not None:
        del scraper
        scraper = DiscordScraper()

    # Determine if the day is empty, default to the current day if so.
    if day is None:
        day = datetime.today()

    # Determine if the year is no less than 2015 since any time before this point will be guaranteed invalid.
    if day.year <= 2014:
        exit(0)
        
    # The smallest snowflake that Discord recognizes is from January 1, 2015.
    while day > datetime(2015, 1, 1):
        day = startGuild(scraper, guild, channel, day)



import argparse
def argsParser():
    parser = argparse.ArgumentParser(description='Discord Spiders')
    parser.add_argument('-d', '--direct', help='Connect directly without proxy')
    parser.add_argument('-p', '--port', default='7890', help='Local Proxy Port')
    args = parser.parse_args()
    return args

if __name__ == '__main__':    
    args = argsParser()
    from globalVars import GlobalVars
    GlobalVars.args = args

    discordscraper = DiscordScraper()
    for guild, channels in discordscraper.guilds.items():
        for channel in channels:
            print("[debug]try to connect {}:{}".format(guild, channels))
            # Retrieve the datetime object for the most recent post in the channel.
            lastdate = getLastMessageGuild(discordscraper, guild, channel)
            print("[debug]Last Active Date:",lastdate)
            # Start the scraper for the current channel.
            start(discordscraper, guild, channel, lastdate) # for debug temporary annoted

    # # Iterate through the direct messages to scrape.
    # for alias, channel in discordscraper.directs.items():
    #     # Start the scraper for the current direct message.
    #     startDM(discordscraper, alias, channel)