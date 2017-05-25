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
        reddit = praw.Reddit(client_id='<id>',
                             client_secret='<secret>',
                             user_agent='windows:py-sb-botw:0.1 (by /u/6_lasers)')
        
        search = reddit.subreddit('starbound').search(input, syntax='lucene', sort='new')
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
    # TODO: this might change (as well as other text patterns this script relies on)
    for post in foundPosts:
        if "This weeks build topic" in post['data']['selftext']:
            outputYmlFile.write("  - title: " + post['data']['title'].split(":")[1].strip() + "\n")
            outputYmlFile.write("    url: " + post['data']['url'] + "\n")
            
            # Compile list of entries
            entries = []
            entries_started = False
            for line in post['data']['selftext'].splitlines():
                # Convention is that a "Current entrees" (sic) line begins the entries
                if "Current entrees" in line:
                    entries_started = True
                elif entries_started:
                    # and a bunch of dashes ends the entries
                    if "-------------" in line:
                        entries_started = False
                    # Get all non-blank lines in between
                    elif line != "":
                        # Format looks something like:
                        # [The last remnant by TrIpTiCuS] (https://www.reddit.com/r/starbound/comments/6bhc4g/botwthe_last_remnant_repost_because_i_forgot_botw/)
                        expmatch = re.search("\[(.*)\s+by\s+(.*)\]\s*\((.*)\)", line)
                        if expmatch:
                            entries.append(expmatch.groups())
                        else:
                            # Due to typos, the expression sometimes fails, so fail gracefully
                            # TODO: is there any way programmatically to salvage the line?
                            print "ERROR on line: " + line
                # Convention is that the description begins with "Build Criteria"
                elif "Build Criteria" in line:
                    desc_started = True
                elif desc_started:
                    # and description ends with "Winners will be chosen" or a bunch of dashes
                    if "-------------" in line or "Winners will be chosen" in line:
                        desc_started = False
                    # All the lines in between make up the description
                    else:
                        desc += "      " + line + "\n"
            
            # Print description
            outputYmlFile.write("    desc: |\n")
            outputYmlFile.write(desc)

            # Now that we have the list, print it in YAML format.
            # I don't use a YAML dumper because it doesn't
            # get the format the way I like it..
            outputYmlFile.write("    entries:\n")
            for entry in entries:
                outputYmlFile.write("    - entrant: \"{0}\"\n".format(entry[1]))
                outputYmlFile.write("      title: \"{0}\"\n".format(entry[0]))
                outputYmlFile.write("      url: " + entry[2] + "\n")
            # Have to fill in winner, runnerup by hand since that comes from next week's post
            outputYmlFile.write("    winner: [\"\"]\n")
            outputYmlFile.write("    runnerup: \"\"\n")
    
    outputYmlFile.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

