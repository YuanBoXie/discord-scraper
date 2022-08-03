"""
@author:  Dracovian
@date:    2021-02-10
@license: WTFPL
"""

"""
sys.stderr:       Used to access the standard error filestream from the OS.
sys.version_info: Used to determine which version of Python is being used to run the script.
"""
from sys import stderr, version_info

"""
datetime.datetime:  Used to access the datetime class and its functions for easier date processing.
datetime.timedelta: Used to make the process of subtracting time much easier with less chances of an error on my behalf.
"""
from datetime import datetime, timedelta

"""
mimetypes.MimeTypes: Used to access the MimeTypes class and its functions for quickly determining if a file extension is an image, video, or something else.
"""
from mimetypes import MimeTypes

"""
os.makedirs: Used to create a folder with subfolders.
os.getcwd:   Used to get the current working directory for the commandline, hopefully this is the same directory as the discord.py file.
os.path:     Used to combine and split file paths since Windows uses a different path separator character to *nix systems such as Linux and macOS.
os._exit:    Used to halt the script without calling cleanup handlers, flushing stdio buffers, or any cleanup routines (we really want this script to stop at this point)
"""
from os import makedirs, getcwd, path
from os import _exit as exit

"""
signal.SIGINT: Used to detect CTRL+C (Command+C) inputs during runtime.
signal.signal: Used to tie in the SIGINT with an event function that can allow us to clear up any cached JSON data upon exiting.
"""
from signal import SIGINT, signal

"""
json.loads: Used to convert a serialized string into a dictionary object.
json.dumps: Used to convert a dictionary object into a serialized string.
"""
from json import loads, dump

"""
random.choice: Used to simplify the process of "randomly" choosing a value from an array.
"""
from random import choice

"""
time.mktime: Used to get the current timestamp of the system, this is here to uphold Python 2 compatibility in the script.
"""
from time import mktime

"""
This conditional statement will be used to import the class from the correct file based on the version of the Python interpreter used.
"""
if version_info.major == 3:  # This means that we're running Python 3.X
    from .RequestB import DiscordRequest

elif version_info.major == 2:  # This means that we're running Python 2.X
    from .RequestA import DiscordRequest

else:  # This means that we're running some version of Python before 2.X or after 3.X
    stderr.write('[ERROR]: Invalid version of Python detected! This script only supports Python 2 and Python 3.\n')
    exit(1)

"""
Create a function and tie SIGINT to said function.
"""
def sigintEvent(sig, frame):
    print('You pressed CTRL + C')
    exit(0)

signal(SIGINT, sigintEvent)

def error(message):
    """
    Throw an error message and then halt the script.
    :param message: A string that will be printed out to STDERR before exiting the script.
    """

    # Append our message with a newline character.
    stderr.write('[ERROR]: {0}\n'.format(message))

    # Halt the script right here, do not continue running the script after this point.
    exit(1)

def warn(message):
    """
    Throw a warning message without halting the script.
    :param message: A string that will be printed out to STDERR.
    """

    # Append our message with a newline character.
    stderr.write('[WARN] {0}\n'.format(message))

class DiscordConfig(object):
    """
    This class will only serve the purpose of converting a dictionary object into a class object.
    """

class DiscordScraper(object):
    """
    This class will contain all of the important functions that will be used that works with both Python 2 and Python 3 interpreters.
    """

    def __init__(self, configfile=None, apiversion=None):
        """
        :param self: A reference to the class object that will be used to call any non-static functions in this class.
        :param configfile: The configuration file that this script will rely on to function as it's supposed to, if one isn't given then it will use the default value.
        :param apiversion: The API version that Discord uses for its backend, this is currently set to "v8" as of November 2020.
        """
        if configfile is None: configfile = 'config.json'
        if apiversion is None: apiversion = 'v8'

        # Generate a direct file path to the configuration file.
        configfile = path.join(getcwd(), configfile)

        # Throw an error if the configuration file doesn't exist.
        if not path.exists(configfile):
            error('Configuration file can not be found at the following location: {0}'.format(configfile))

        with open(configfile, 'r') as configfilestream:
            configfiledata = configfilestream.read()
        # Convert the serialized JSON contents of the configuration file into a dictionary.
        configdata = loads(configfiledata)
        # Convert the configuration dictionary into a class object.
        config = type('DiscordConfig', (object, ), configdata)()
        tokenfile = path.join(getcwd(), config.tokenfile)
        print("[debug]tokenfile:",tokenfile)
        if not path.exists(tokenfile):
            error('Authorization token file can not be found at the following location: {0}'.format(tokenfile))
        with open(tokenfile, 'r') as tokenfilestream:
            tokenfiledata = tokenfilestream.readline().rstrip()
        print("[debug]token:",tokenfiledata[:5],"...")
        # Create a dictionary to store the HTTP request headers that we will be using for all requests.
        self.headers = {
            'User-Agent': config.useragent,    # The user-agent string that tells the server which browser, operating system, and rendering engine we're using.
            'Authorization': tokenfiledata     # The authorization token that authorizes this script to carry out actions with your account, this script only requires this to access the data on the specified guilds and channels for scraping purposes. NEVER UNDER ANY CIRCUMSTANCE SHARE THIS VALUE TO ANYONE YOU DO NOT TRUST!
        }

        # Create some class variables to store the configuration file data.
        self.apiversion = apiversion      # The backend Discord API version which denotes which API functions are available for use and which are deprecated.
        self.buffersize = config.buffer   # The file download buffer that will be stored in memory before offloading to the hard drive.
        self.options    = config.options  # The experimental options portion of the configuration file that will give extra control over how the script functions.
        self.types      = config.types    # The file types that we are wanting to scrape and download to our storage device.

        # Make the options available for quick and easy access.
        self.validateFileHeaders = config.options['validateFileHeaders']      # The option that will not only check the MIME type of a file but go one step further and check the magic number (header) of the file.
        self.generateFileChecksums = config.options['generateFileChecksums']  # The option that will generate a document listing off generated checksums for each file that was scraped for duplicate detection.
        self.sanitizeFileNames = config.options['sanitizeFileNames']          # The option that will rename files and folders to avoid as many problems with filesystem and reserved file names in most operating systems.
        self.compressImageData = config.options['compressImageData']          # The option that will enable image file compression to save on storage space when downloading data, this will likely be a generic algorithm.
        self.compressTextData = config.options['compressTextData']            # The option that will enable textual data compression to save on storage space when downloading data, this will most likely be GZIP compression.
        self.gatherJSONData = config.options['gatherJSONData']                # The option that will determine whether or not the script should cache the response text in JSON formatting.
        
        # Use Python ternary operators to set the class variables for direct messages and guilds that we should scrape.
        # self.directs = config.directs if len(config.directs) > 0 else {}
        self.guilds  = config.guilds  if len(config.guilds ) > 0 else {}

        # Create a blank guild name, channel name, and folder location class variable.
        self.guildname = None
        self.channelname = None
        self.location = None

        # Halt the script if there are no direct messages or guilds to scrape, since it would be useless to run this script without any data to scrape.
        # if len(config.directs) == 0 and len(config.guilds) == 0:
        if len(config.guilds) == 0:
            error('No guilds or DMs were set to be grabbed, exiting!')
        
        # Create a class variable to store the URI query for our search requests.
        self.query = DiscordScraper.generateQueryBody(
            images = config.query['images'],
            files  = config.query['files' ],
            embeds = config.query['embeds'],
            links  = config.query['links' ],
            videos = config.query['videos'],
            nsfw   = config.query['nsfw'  ]
        )

    def grabGuildName(self, id, dm=None):
        """
        Send a request to retrieve the guild name by its ID.
        :param id: The ID for the guild we want to retrieve the name for.
        :param dm: A true or false (boolean) value that determines if we're scraping a direct message.
        """

        # If the dm is empty, then set it to false.
        if dm is None:
            dm = False

        # Determine if we're in a dm.
        if dm:

            # Just pass the safe name on through.
            self.guildname = DiscordScraper.getSafeName(id)

            # Exit the function.
            return None

        # Create a variable that references the DiscordRequest object.
        request = DiscordRequest()

        # Set the headers for the request.
        request.setHeaders(self.headers)

        # Generate the API location from the parameters.
        url = 'https://discord.com/api/{0}/guilds/{1}'.format(self.apiversion, id)

        # Make a request to retrieve the API data from Discord.
        response = request.sendRequest(url)

        # Return a randomized name if the request data is empty.
        if response is None:

            # Send a warning to notify the user that we're creating a random name for the guild.
            warn('Unable to gather guild name from its ID, generating one instead!')

            # Generate 8 "random" characters to serve as our generated guild name.
            randomguildname = DiscordScraper.randomString(8)

            # Set the guild name class variable with our new name.
            self.guildname = u'{0}_{1}'.format(id, randomguildname)
        
        # Otherwise use the gathered guild data to retrieve the guild name.
        else:

            # Convert the response data from serialized text to a dictionary.
            data = loads(response.read())

            # Grab the guild name from the data.
            guildname = DiscordScraper.getSafeName(data['name']) if self.sanitizeFileNames else data['name']

            # Set the guild name class variable with the guild name.
            self.guildname = u'{0}_{1}'.format(id, guildname)

    
    def grabChannelName(self, id, dm=None):
        """
        Send a request to retrieve the channel name by its ID.
        :param id: The ID for the channel that we want to retrieve the name for.
        :param dm: A true or false (boolean) value that determines if we're scraping a direct message.
        """

        # If the dm is empty, then set it to false.
        if dm is None:
            dm = False

        # Determine if we're in a dm.
        if dm:

            # Just set the ID.
            self.channelname = id

            # Exit this function
            return None

        # Create a variable that references the DiscordRequest object.
        request = DiscordRequest()

        # Set the headers for the request.
        request.setHeaders(self.headers)

        # Generate the API location from the parameters.
        url = 'https://discord.com/api/{0}/channels/{1}'.format(self.apiversion, id)

        # Make a request to retrieve the API data from Discord.
        response = request.sendRequest(url)

        # Return a randomized name if the request data is empty.
        if response is None:

            # Send a warning to notify the user that we're creating a random name for the channel.
            warn('Unable to gather channel name from its ID, generating one instead!')

            # Generate 8 "random" characters to serve as our generated channel name.
            randomchannelname = DiscordScraper.randomString(8)

            # Set the channel name class variable with our new name.
            self.channelname = u'{0}_{1}'.format(id, randomchannelname)
        
        # Otherwise use the gathered channel data to retrieve the channel name.
        else:

            # Convert the response data from serialized text to a dictionary.
            data = loads(response.read())

            # Grab the channel name from the data.
            channelname = DiscordScraper.getSafeName(data['name']) if self.sanitizeFileNames else data['name']

            # Set the channel name class variable with the channel name.
            self.channelname = u'{0}_{1}'.format(id, channelname)
    
    def createFolders(self):
        """
        Create the folder structure for the particular guild/DM and channels that we're wanting to scrape.
        """

        # Set the direct folder path for the current channel.
        folderpath = path.join(getcwd(), 'scrapes', self.guildname, self.channelname)

        # Create the path if it does not exist.
        if not path.exists(folderpath):
            makedirs(folderpath)
        
        # Set the location class variable.
        self.location = folderpath

    def downloadJSON(self, data, year, month, day):
        """
        Cache the JSON data from all the scraped channels.
        :param data: The response data from Discord's backend API that should contain the information we desire.
        :param month: The month when the data was scraped.
        :param year: The year when the data was scraped.
        """
        
        # Determine if we have configured the script to cache JSON data to begin with.
        if self.gatherJSONData:

            # Create a cache directory.
            cachedir = path.join(getcwd(), 'cached', self.guildname, self.channelname)

            # Check if it already exists, if not then create it.
            if not path.exists(cachedir):
                makedirs(cachedir)

            # Generate the direct file name for the cachefile.
            cachefile = path.join(cachedir, '{0}_{1}_{2}.cache.json'.format(year, month, day))

            # Determine if the cachefile already exists, if so then skip it (TODO this might cause issues for incomplete runs, so this needs to be figured out in due time).
            if path.isfile(cachefile):
                return None
            
            # Open the cachefile for appending textual data.
            with open(cachefile, 'w') as cachefilestream:
                
                # Write the JSON data directly to the file.
                dump(data, cachefilestream, indent=4)
    
    def startDownloading(self, url, location):
        """
        Call the Requests.download function to begin downloading our files.
        :param url: The direct URL (proxied URL to protect from requesting any malicious sites that might be watching out for the request header that stores our authorization token) for our content.
        :param location: The folder that we will be downloading the content into.
        """
        
        # Split the url into parts.
        urlparts = url.split('/')
        
        # Generate a file name from the url parts.
        filename_head = urlparts[-2]
        filename_foot = urlparts[-1]

        # Generate a file name from the url parts.
        filename = DiscordScraper.getSafeName('{0}_{1}'.format(filename_head, filename_foot)) if self.sanitizeFileNames else '{0}_{1}'.format(filename_head, filename_foot)

        # Join the file name with the location.
        filename = path.join(location, filename)

        # Skip this function if the file already exists.
        if path.isfile(filename):
            return None
        
        # Create a request.
        request = DiscordRequest()

        # Set the request headers.
        request.setHeaders(self.headers)

        # Download the file directly.
        request.downloadFile(url, filename, self.buffersize)

    def checkMimetypes(self, data):
        """
        Avoid downloading any files that are of the types we do not want to download in accordance with the configuration file settings.
        :param data: The response data from Discord's backend API that should contain the information we desire.
        """

        try:

            # Determine if there are any results from our scrape.
            if data['total_results'] > 0:

                # Iterate through all messages one-by-one.
                for messages in data['messages']:

                    # Iterate through each message one-by-one.
                    for message in messages:
                        
                        # Iterate through all of the attachments to check them one-by-one.
                        for attachment in message['attachments']:

                            # Get the proxied URL for our content.
                            proxied = attachment['proxy_url']

                            # Get the proxied file name from the proxied URL.
                            proxiedfilename = proxied.split('/')[-1].split('?')[0]

                            # Get the mimetype for the proxied file name.
                            proxiedfilemime = DiscordScraper.getFileMimetype(proxiedfilename).split('/')[0]

                            # Determine if the proxied file is an image file.
                            if self.types['images'] and proxiedfilemime == 'image':
                                
                                # Begin downloading this file if so.
                                self.startDownloading(proxied, self.location)
                            
                            # Determine if the proxied file is a video file.
                            if self.types['videos'] and proxiedfilemime == 'video':
                                
                                # Begin downloading this file if so.
                                self.startDownloading(proxied, self.location)
                            
                            # Determine if the proxied file is neither an image or a video file.
                            if self.types['files'] and proxiedfilemime not in ['image', 'video']:
                                
                                # Begin downloading this file if so.
                                self.startDownloading(proxied, self.location)
                            
                        # Iterate through all of the embedded contents to check them one-by-one.
                        for embed in message['embeds']:

                            # Determine if there are any embedded images.
                            if self.types['images']:

                                # Get the URL for our content.
                                url = embed['image']['proxy_url']
                                
                                # Begin downloading this file if so.
                                self.startDownloading(url, self.location)

                            # Determine if there are any embedded videos.
                            if self.types['videos']:

                                # Get the URL for our content.
                                url = embed['video']['proxy_url']

                                # Begin downloading this file if so.
                                self.startDownloading(url, self.location)
        except:
            pass
    
    @staticmethod
    def randomString(length):
        """
        A static function that is callable in the form of DiscordScraper.randomString.
        :param length: A numerical value that will determine the number of characters will be in our "random" string.
        """

        # This will be the character set for the random string, the random string will only consist of these characters.
        charset = "0123456789ABCDEF"  # Some will recognize this as the character set for hexadecimal values, and that is true.

        # Return a string formed from the joining of an array of "random" characters.
        return ''.join([choice(charset) for i in range(length)])

    @staticmethod
    def getFileMimetype(name):
        """
        Return the guessed mimetype for the input file name.
        :param name: The file name whose mimetype we want to guess.
        """

        # Create a variable to store the guessed mimetype for the file.
        mimetype = MimeTypes().guess_type(name)[0]

        # Determine if the mimetype value is empty, return a blob mimetype if it is empty.
        if mimetype is None:
            return 'application/octet-stream'
        
        # Return the mimetype if it is not empty.
        return mimetype
    
    @staticmethod
    def timestampToSnowflake(timestamp):
        """
        A static function that is callable in the form of DiscordScraper.timestampToSnowflake.
        :param timestamp: A numerical value that is representative of the UNIX epoch to the nearest second (not millisecond).
        """

        # Multiply the timestamp by 1000 to approximate the UNIX epoch to the nearest millisecond.
        timestamp *= 1000

        # Subtract the UNIX epoch of January 1, 2015 from the timestamp as this is the minimum timestamp that Discord supports because Discord has only been around since May 2015.
        timestamp -= 1420070400000

        # Return the timestamp value bitshifted to the left by 22 bits.
        return int(timestamp) << 22
    
    @staticmethod
    def snowflakeToTimestamp(snowflake):
        """
        A static function that is callable in the form of DiscordScraper.snowflakeToTimestamp.
        :param snowflake: A numerical value that is representative of the Discord-tailored epoch to the nearest millisecond (not second).
        """

        # Bitshift the snowflake value to the right by 22 bits.
        snowflake >>= 22

        # Add the UNIX epoch of January 1, 2015 to the snowflake (see the timestampToSnowflake function above for more information on why we have to do this).
        snowflake += 1420070400000

        # Return the snowflake value divided by 1000 to get the timestamp value to the nearest second.
        return snowflake / 1000.0
    
    @staticmethod
    def getDayBounds(day, month, year):
        """
        Return an array of snowflakes that is representative of the start and end of the specified date.
        :param day: The day that we're wanting to grab the snowflakes for.
        :param month: The month that we're wanting to grab the snowflakes for.
        :param year: The year that we're wanting to grab the snowflakes for, we're assuming the use of the Gregorian calendar.
        """

        # Get the minimum timestamp value or 00:00 (12:00 AM).
        mintime = mktime((year, month, day,  0,  0,  0, -1, -1, -1))

        # Get the maximum timestamp value or 23:59 (11:59 PM).
        maxtime = mktime((year, month, day, 23, 59, 59, -1, -1, -1))

        # Convert the minimum timestamp value to a snowflake.
        minsnow = DiscordScraper.timestampToSnowflake(mintime)

        # Convert the maximum timestamp value to a snowflake.
        maxsnow = DiscordScraper.timestampToSnowflake(maxtime)

        # Return an array with the minimum snowflake and maximum snowflake values in it.
        return [minsnow, maxsnow]
    
    @staticmethod
    def getSafeName(name):
        """
        Sanitize a string for use in filenaming so as to prevent errors related to disallowed filenames based on whichever OS this script is being ran on.
        :param name: A string of characters that we're wanting to sanitize.
        """

        # Create an array storing all the disallowed values that will interfere with certain operating system file naming schemes.
        disallowed = [
            '/dev',          # Linux and BSD systems will store their device files in this directory.
            '/devices',      # Solaris will store their device files in this directory.
            'Devices:',      # RISC OS will store their device files in this format.
            '\\DEV','/DEV',  # MS-DOS and PC DOES 2.x store theirs in these places.
            'U:\\DEV',       # MagiC, MiNT, and MultiTOS from Atari stores in this place.
            '\\\\devices\\', # Windows 9x device file location.
            '\\\\.\\',       # Windows NT device file location.
            
            # Prepare yourself for a list of device file names that are often reserved on Windows and OS/2.
            'CON', 'PRN', 'AUX', 'NUL', 'CLOCK', 'CLOCK$', 'KEYBD$', 'KBD$', 'SCREEN$', 'POINTER$', 'MOUSE$',
            '$IDLE$', 'CONFIG$', 'LST', 'PLT', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LTP6', 'LPT7', 'LPT8',
            'LPT9', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9' '82164A', 'PIPE',
            'MAILSLOT',
        ]

        # Determine if the filename is in any of the disallowed names above.
        if name in disallowed:
            
            # Get the file extension from the filename.
            extension = name.split('.')[-1]

            # Generate a random filename that is 16 characters in length.
            randname = DiscordScraper.randomString(16)

            # Set the name variable to the newly generated name.
            name = '{0}.{1}'.format(randname, extension)
        
        # Create a variable to store the valid characters of our file name.
        valid = []

        # Iterate through each character of our file name to ensure that there's no disallowed characters in there.
        for char in name:
            
            # Determine if the character is not in the list of invalid characters.
            if char not in '\\/<>:"|?*':

                # Append the character to the valid character array.
                valid.append(char)
        
        # Join the array of characters into a string and return that value.
        return ''.join(valid)
    
    @staticmethod
    def generateQueryBody(**kwargs):
        """
        Generate a valid portion of the URI query used to specify what we want to search for in Discord.
        :param kwargs: The keyword-based arguments that we will be receiving, this is a variadic argument meaning that we can send anywhere from zero to potentially infinite arguments.
        """

        # Create an array to store each of our URI parameters.
        parameters = []

        # Iterate through the keyword-based arguments to retrieve each individual item.
        for key, value in kwargs.items():

            # Determine if the value is true and if it doesn't contain the value of "NSFW".
            if value and key != 'nsfw':

                # Append the partial query string to the parameters array.
                parameters.append('has={0}'.format(key[:-1]))
            
            # Determine if the value contains the text "NSFW".
            if value and key == 'nsfw':

                # Append the partial query string to the parameters array.
                parameters.append('include_nsfw={0}'.format(str(value).lower()))
            
        # Join the array of partial URI parameters and return that value.
        return '&'.join(parameters)

    @staticmethod
    def requestData(url, headers=None):
        """
        Make a simplified alias to the Discord Requests sendRequest class function.
        :param url: The URL that we want to grab data from.
        :param headers: The headers dictionary that we want to set.
        """
        if headers is None: headers = {}
        request = DiscordRequest()
        request.setHeaders(headers)
        return request.sendRequest(url)