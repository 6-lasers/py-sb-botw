#!/usr/bin/env python
######################################################
#
#    botw_entriesJsonToPost.py
#
#  Takes JSON returned from a Reddit request,
#  extracts BotW posts from it, and
#  prints a list of authors, titles, and URLs
#  formatted as a Reddit post. Alternatively,
#  uses a PRAW search request to fill this information
#
#  Usage: botw_entriesJsonToPost.py <input> <skip count>
#
######################################################

import os
import sys
import optparse
import json
import re
import operator

# Python Reddit API Wrapper
# You can remove this if you just want to load JSON from a text file
import praw

# Reddit username of the BotW curator
botw_curator = "-ologist"
botw_topic_pattern = r"Build of the Week:" # Used to be r"BOTW\s*:"

def main(argv=None):
    usage="botw_entriesJsonToPost.py <input> <skip count>"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        input, skip = args
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
                    'permalink': result.permalink,
                    'author': result.author,
                    'selftext_html': result.selftext_html,
                    'score': result.score,
                }
            })
    
    # Normally, searching stops as soon as you hit a BotW topic post.
    # Skip argument is intended to let you skip posts so that you
    # can gather entries for a previous week
    # TODO: should just use CloudSearch syntax for this and use a date range..
    skip = int(skip)
    
    entries = []
    cnt = 0
    for post in foundPosts:
        # Non-image posts by the BotW curator beginning with the topic pattern are considered to be cut-offs
        # Image link determined if selftext_html is None
        if post['data']['selftext_html'] != None and post['data']['author'] == botw_curator and re.match(botw_topic_pattern, post['data']['title']):
            # Consider skip argument here
            cnt += 1
            if cnt > skip:
                print "Stopping at " + post['data']['title']
                break
            else:
                print "Saw " + post['data']['title'] + " and skipping it"
                print "{0} of {1}".format(cnt, skip)
        # Image link. To be lenient, also consider text posts with URLs
        # Image link determined if selftext_html is None
        elif post['data']['selftext_html'] == None or "http" in post['data']['selftext']:
            rejected = False
            
            # Expected format: [BotW] <title> or (BotW) <title>.
            # "BotW" not case sensitive
            # Okay to have other characters in the brackets
            expmatch = re.search(r"(?:\[.*BotW.*\]|\(.*BotW.*\))\s*(.*)", post['data']['title'], re.IGNORECASE)
            if expmatch:
                title = expmatch.group(1)
            else:
                # Backup: try looking for BotW: <title>, BotW- <title>, or just BotW <title>
                # "BotW" not case sensitive
                # Okay to have other characters before the colon or dash
                expmatch = re.search(r".*BotW(?:.*?[:-])?\s*(.*)", post['data']['title'], re.IGNORECASE)
                if expmatch:
                    title = expmatch.group(1)
                else:
                    # False negatives are the worst outcome because someone's submission is lost.
                    # Even if a submission fails all tests, append it with a "rejected" flag.
                    # Anything with BotW (case-insensitive) would be here, e.g. "Does BotW allow mods"
                    # (assuming the post met the above requirements)
                    title = post['data']['title']
                    print "Rejected " + title
                    rejected = True
            # Construct a Reddit-formatted entry. Should look like:
            # [<title> by <author>](url)
            # Reddit 'permalink' field doesn't include the actual reddit.com address
            entries.append(("[ {0} by {1} ] (https://www.reddit.com{2})".format(title, post['data']['author'], post['data']['permalink'].split("?")[0]),post['data']['score'], rejected))
    
    # Separate debugging info from actual output
    print "\n\n--List of entries begins--\n\n"
    
    # Print all entries. Mark 'rejected' ones with WARNING
    # so that they can be hand-reviewed
    for entry in entries:
        if entry[2]:
            print "---WARNING---"
        print entry[0] + "\n"
    
    print "\n\n--Entries sorted by score begins--\n\n"
    
    # Sort entries in descending order of score
    entries.sort(key=operator.itemgetter(1), reverse=True)
    # Print all entries along with their score.
    # "rejected" entries get an asterisk and may be false positives
    for entry in entries:
        print "({1}{2})\t{0}".format(entry[0], entry[1], "*" if entry[2] else "")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

