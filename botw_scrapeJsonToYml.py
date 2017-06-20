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

# Pattern to identify a BotW topic post
topic_pattern = "Build of the Week theme is:"
# Old pattern was "This weeks build topic"

# Patterns to look for in the topic post
entries_begin_pattern = "**ENTRIES**"
# old pattern was "Current entrees"
entries_end_pattern = "**WINNER**"
# old pattern was "-------------"

winners_end_pattern = "**RUNNER-UP**"

desc_begin_pattern = "You must submit your entry" # used to be "Build Criteria"
desc_end_pattern = "BUILDING TIPS" # used to be "Winners will be chosen"

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
        
        search = reddit.subreddit('starbound').search(input, syntax='cloudsearch', sort='new')
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
    # a fixed pattern in the text
    for post in foundPosts:
        if topic_pattern in post['data']['selftext']:
            outputYmlFile.write("  - title: " + post['data']['title'].split(":")[1].strip() + "\n")
            outputYmlFile.write("    url: " + post['data']['url'] + "\n")
            
            # Compile list of entries
            entries = []
            entries_started = False
            desc = ""
            desc_started = False
            winners = []
            winner_started = False
            runnerup = None
            runnerup_started = False
            for line in post['data']['selftext'].splitlines():
                line = replace_unicode(line)
                # Search for pattern which indicates beginning of entries
                if entries_begin_pattern in line:
                    entries_started = True
                # continue until pattern which indicates end of entries
                elif entries_end_pattern in line:
                    entries_started = False
                    # Winner starts right after entries
                    # TODO: this might not be true forever
                    winner_started = True
                elif winners_end_pattern in line:
                    winner_started = False
                    # Runner-up starts right after winner
                    # TODO: this might not be true forever
                    runnerup_started = True
                # Get all non-blank lines in between entry
                # start and end--these are our entries
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
                # Grab winner(s)
                elif winner_started and line != "":
                    expmatch = re.search("\[(.*)\s+by\s+(.*)\]\s*\((.*)\)", line)
                    winners.append(expmatch.group(2))
                # Grab runnerup
                elif runnerup_started and line != "":
                    expmatch = re.search("\[(.*)\s+by\s+(.*)\]\s*\((.*)\)", line)
                    runnerup = expmatch.group(2)
                # Identify description beginning
                elif desc_begin_pattern in line:
                    desc_started = True
                elif desc_started:
                    # and ending
                    if desc_end_pattern in line:
                        desc_started = False
                    # All the lines in between make up the description.
                    # Remove leading spaces
                    else:
                        desc += "      " + line.lstrip() + "\n"
            
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
            outputYmlFile.write("    winner:\n")
            for winner in winners:
                outputYmlFile.write("      - \"{0}\"\n".format(winner))
            if runnerup:
                outputYmlFile.write("    runnerup: \"{0}\"\n".format(runnerup))
    
    outputYmlFile.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

