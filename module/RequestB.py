"""
@author:  Dracovian
@date:    2021-02-10
@license: WTFPL
"""
# [ERROR] Unstructured of proxy problem
"""
http.client.HTTPSConnection: Used to grab data from sites that use TLS or SSL encryption.
"""
from http.client import HTTPSConnection
# docs: https://docs.python.org/3/library/http.client.html
'''
>>> import http.client
>>> conn = http.client.HTTPSConnection("localhost", 8080)
>>> conn.set_tunnel("www.python.org")
>>> conn.request("HEAD","/index.html")
'''

"""
os.makedirs: Used to create a folder with subfolders.
os.path:     Used to combine and split file paths.
"""
from os import makedirs, path

"""
sys.stderr: Used to write to the standard error filestream.
"""
from sys import stderr

"""
time.sleep: Used to pause the script for a set time.
"""
from time import sleep

"""
json.loads: Used to convert a serialized string into a dictionary object.
"""
from json import loads

from globalVars import GlobalVars # to fix proxy problem

def warn(message):
    """
    Throw a warning message without halting the script.
    :param message: A string that will be printed out to STDERR.
    """

    # Append our message with a newline character.
    stderr.write('[WARN] {0}\n'.format(message))

class DiscordRequest(object):
    """
    The Python 3 compatible version of the DiscordRequest class.
    """
    def __init__(self): self.headers = {}
    def setHeaders(self, headers): self.headers = headers
    def sendRequest(self, url):
        """
        Send a request to the target URL and return the response data.
        :param url: The URL to the target that we're wanting to grab data from.
        """
        # Split the URL into parts.
        urlparts = url.split('/')
        # Grab the domain name from the urlparts.
        domain = urlparts[2].split(':')[0]
        # Grab the URL path from the urlparts.
        urlpath = '/{0}'.format('/'.join(urlparts[3:]))
        
        # Determine if the domain is safe or unsafe.
        if domain.endswith('.discordapp.net') or domain.endswith('.discord.com') or domain in ['discordapp.net', 'discord.com']:
            safedomain = True

        # Create a reference to the HTTPSConnection class.
        if GlobalVars.args.direct:
            connection = HTTPSConnection(domain, 443)
        else:
            connection = HTTPSConnection('localhost', GlobalVars.args.port)
            connection.set_tunnel(domain)

        # Ensure that we're not sending authorization tokens to non-Domain domains.
        if safedomain:
            headers = self.headers
        else:
            headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://discord.com/'}
            
        # Request the data from the connection.
        connection.request('GET', urlpath, headers=headers)

        # Retrieve the response from the request.
        response = connection.getresponse()

        # TODO: Remove this before releasing
        for header in response.getheaders():
            if header[0] == 'Retry-After':
                print(header)

        # Return the response if the connection was successful.
        if 199 < response.status < 300:
            return response
        
        # Recursively run this function if we hit a redirect page.
        elif 299 < response.status < 400:

            # Grab the URL that we're redirecting to.
            url = response.getheader('Location')

            # Grab the domain name for the redirected location.
            domain = url.split('/')[2].split(':')[0]

            # Follow the redirect
            self.sendRequest(url)
        
        # Otherwise throw a warning message to acknowledge a failed connection.
        else: warn('HTTP {0} from {1}.'.format(response.status, url))

        # Handle HTTP 429 Too Many Requests
        if response.status == 429:
            retry_after = loads(response.read()).get('retry_after', None)

            if retry_after:   
                # Sleep for 1 extra second as buffer
                sleep(1 + retry_after)
                return sendRequest(self, url)

        # Return nothing to signify a failed request.
        return None
    
    def downloadFile(self, url, filename, buffer=0): # [ERROR] Unstructured of proxy problem
        """
        Download the file to the correct location on our storage device.
        :param url: The URL for the file that we're wanting to download.
        :param filename: The full file path to where we are wanting to store the downloaded file.
        :param buffer: The buffer size in bytes that we want to use to download our file in chunks.
        """

        # Grab the folder path from the full file name.
        filepath = path.split(filename)[0]

        # Determine if the file path exists, if not then create it.
        if not path.exists(filepath):
            makedirs(filepath)
        
        # Determine if the file already exists, if so then skip this function.
        if path.isfile(filename):
            return None

        # Request the response data from the URL.
        response = self.sendRequest(url)

        # Determine if the request data is not empty, if so then skip this function.
        if response is None:
            return None
        
        # Get the file size in bytes.
        filesize = int(response.getheader('Content-Length'))
        
        # Create a variable to store the amount of bytes that we've already downloaded thus far.
        downloaded = 0

        # Determine how many chunks we can feasibly push with our filesize.
        numchunks = int(filesize / buffer)

        # Determine how much of the last chunk is needed to finish the download.
        lastchunk = filesize % buffer

        # Open the new file for appending bytes to.
        with open(filename, 'a+b') as filestream:

            # Determine if we can grab the file byte-by-byte or if our buffer is 0 or larger than our file size.
            if response.getheader('Accept-Ranges') != 'bytes' or buffer <= 0 or numchunks < 1:

                # Print something out for the user to read.
                print('\rDownloading {0}...'.format(' ' * 7), end='')

                # Just simply write the full contents of the file instead of streaming it in chunks.
                filestream.write(response.read())

                # Close the file stream.
                filestream.close()

                # Continue the script.
                return None
            
            # Iterate through each chunk of the file until we hit the filesize limit.
            for i in range(numchunks):

                # Generate another request class.
                request = DiscordRequest()

                # Grab the current request headers.
                headers = self.headers

                # Create a variable to store the byte position for the end of the chunk.
                chunk = downloaded + buffer - 1

                # Update the headers to include the chunk depending on how close we are to finishing the download.
                headers.update({'Range': 'bytes={0}-{1}'.format(downloaded, chunk)})

                # Set the percentage to the current downloaded percent.
                percentage = 100 * downloaded / filesize
                
                # Set the headers for the new Request object.
                request.setHeaders(headers)

                # Grab the data response from the new Request object.
                response = request.sendRequest(url)

                # If the response is empty then break free from this loop.
                if response is None:

                    # Close the file
                    filestream.close()

                    # Break free
                    return None

                # Print something out to the user.
                print('\rDownloading {0:3.2f}%...'.format(percentage), end='')
                
                # Write the contents of the chunk to the file.
                filestream.write(response.read())

                # Update the downloaded variable to reflect the current filesize.
                downloaded += buffer
            
            if lastchunk > 0:

                # Generate another request class.
                request = DiscordRequest()

                # Grab the current request headers.
                headers = self.headers

                # Update the headers.
                headers.update({'Range': 'bytes={0}-'.format(downloaded)})

                # Set the percentage to 100% at this point.
                percentage = 100.0

                # Set the headers for the new Request object.
                request.setHeaders(headers)

                # Grab the data response from the new Request object.
                response = request.sendRequest(url)

                # If the response is empty then break free from this loop.
                if response is None:

                    # Close the file
                    filestream.close()

                    # Break free
                    return None

                # Print something out to the user.
                print('\rDownloading {0:3.2f}%...'.format(percentage), end='')
                
                # Write the contents of the chunk to the file.
                filestream.write(response.read())
            
            # Close the file stream.
            filestream.close()

            # Reset the downloaded variable.
            del self.headers['Range']
