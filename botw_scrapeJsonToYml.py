#!/usr/bin/env python
######################################################
#
#    botw_scrapeJsonToYml.py
#
#  Takes JSON returned from a Reddit request,
#  extracts BotW topic posts from it, parses
#  those posts for entries/winner information,
#  and outputs in YAML format
#
#  Usage: botw_scrapeJsonToYml.py <input> <output.yml>
#
######################################################

import os
import sys
import optparse
import json
import re

# Python Reddit API Wrapper
# You can remove this if you just want to load JSON from a text file
import praw

def main(argv=None):
    usage="botw_scrapeJsonToYml.py <input> <output.yml>"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        input, outputYmlName = args
    except ValueError:
        print "ERROR: Invalid number of arguments"
        print usage
        return 1
    
    # If input is a real file path, assume it's
    # a JSON request saved to a file
    if os.path.exists(input):
        inputJsonFile = open(input, "r")
        searchContents = json.load(inputJsonFile)
        inputJsonFile.close()
        
        foundPosts = searchContents['data']['children']
    # Otherwise, it's a search query
    else:
        foundPosts = []
        reddit = praw.Reddit(client_id='<client>',
                             client_secret='<secret>',
                             user_agent='<agent>')
        
        search = reddit.subreddit('postpreview').search(input, syntax='lucene', sort='new')
        for result in search:
            foundPosts.append({
                'data': {
                    'selftext': result.selftext,
                    'title': result.title,
                    'url': result.url,
                }
            })
    
    outputYmlFile = open(outputYmlName, "w")
    
    # Go through each search result. We're looking for
    # BotW topic posts. By convention, these contain
    # "This weeks build topic" in the text and have a title like:
    # "BOTW: <something>"
    for post in foundPosts:
        if "This weeks build topic" in post['data']['selftext']:
            print "  - title: " + post['data']['title'].split(":")[1].strip()
            print "    url: " + post['data']['url']
            
            # Compile list of entries
            entries = []
            entries_started = False
            for line in post['data']['selftext'].splitlines():
                # Convention is that a "Current entrees" (sic) line begins the entries
                if "Current entrees" in line:
                    entries_started = True
                # and a bunch of dashes ends the entries
                elif "-------------" in line:
                    entries_started = False
                # Get all non-blank lines in between
                elif entries_started and line != "":
                    # Format looks something like:
                    # [The last remnant by TrIpTiCuS] (https://www.reddit.com/r/starbound/comments/6bhc4g/botwthe_last_remnant_repost_because_i_forgot_botw/)
                    expmatch = re.search("\[(.*)\s+by\s+(.*)\]\s*\((.*)\)", line)
                    if expmatch:
                        entries.append(expmatch.groups())
                    else:
                        # Due to typos, the expression sometimes fails, so fail gracefully
                        # TODO: is there any way programmatically to salvage the line?
                        print "ERROR on line: " + line
            
            # Now that we have the list, print it in YAML format.
            # I don't use a YAML dumper because it doesn't
            # get the format the way I like it..
            print "    entries:"
            for entry in entries:
                print "    - entrant: \"{0}\"".format(entry[1])
                print "      title: \"{0}\"".format(entry[0])
                print "      url: " + entry[2]
            # Have to fill in winner, runnerup by hand since that comes from next week's post
            print "    winner: [\"\"]"
            print "    runnerup: \"\""
    
    outputYmlFile.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

