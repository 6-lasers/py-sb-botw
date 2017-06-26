#!/usr/bin/env python
######################################################
#
#    botw_reconstructPostsAndUpload.py
#
#  Generates a set of archive comments
#
#  Usage: botw_reconstructPostsAndUpload.py <input.yml> <output.txt> <upload topic ID> <append>
#
######################################################

import sys
import optparse
import operator
import datetime

import yaml

import praw

def format_entry(entry):
    return "[ {0} by {1} ] ({2})".format(entry['title'], entry['entrant'], entry['url'])
    

def main(argv=None):
    usage="botw_reconstructPostsAndUpload.py <input.yml> <output.txt> <upload topic ID> <append>"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        ymlName, outTxtName, uploadTopicID, append = args
    except ValueError:
        print "ERROR: Invalid number of arguments"
        print usage
        return 1
    
    # Load YAML database
    ymlFile = open(ymlName, "r")
    
    database = yaml.load(ymlFile)
    
    ymlFile.close()
    
    append = int(append)
    
    reddit = praw.Reddit(client_id='<id>',
                         client_secret='<secret>',
                         user_agent='windows:py-sb-botw:0.1 (by /u/6_lasers)',
                         username='<user>', password='<password>')
    
    # Get the topic ID in which to construct the archive
    if uploadTopicID != "":
        topic = praw.models.Submission(reddit, id=uploadTopicID)
    
    # Relevant time deltas
    endOfWeek = datetime.timedelta(days=6)
    nextWeek = datetime.timedelta(days=7)
    
    # Start date of first BotW (modern era)
    currentdate = datetime.date.fromordinal(database['meta']['startdate'])
    
    outTxtFile = open(outTxtName, "w")
    
    comments = []
    # For each entry in the BotW YAML, generate a post
    # containing entries, winner, description, etc.
    # Store it in one big string
    for botw in database['botw']:
        # If this topic has a specially marked duration,
        # increment by that many weeks. Default is 1
        duration = botw['duration'] if 'duration' in botw else 1
        
        # Date, title, description
        datestring = "Week of **{0}-{1}**".format(currentdate.strftime("%B %d, %Y"), (currentdate + (nextWeek * (duration - 1)) + endOfWeek).strftime("%B %d, %Y"))
        entryString = "---\n"
        entryString += datestring + ". Week's theme was:\n"
        entryString += "## " + botw['title'] + "\n"
        entryString += "---\n"
        entryString += "Build criteria was:\n"
        entryString += botw['desc'] + "\n"
        # Entries
        entryString += "---\n"
        entryString += "**Entries:**\n\n"
        for entry in botw['entries']:
            entryString += format_entry(entry) + "\n\n"
        
        # Winner(s) and runner-up
        winning_entries = filter(lambda x: x['entrant'] in botw['winner'], botw['entries'])
        runnerup_entry = filter(lambda x: x['entrant'] == botw['runnerup'], botw['entries'])[0]
        entryString += "---\n"
        entryString += "**Winner(s):**\n\n"
        for entry in winning_entries:
            entryString += format_entry(entry) + "\n\n"
        entryString += "**Runner up:**\n\n"
        entryString += format_entry(runnerup_entry) + "\n\n"
        entryString += "---\n"
        
        # Write to text file first of all
        outTxtFile.write(entryString)
        
        # If uploadTopicID given, reply as a comment to that post
        comment_link = ""
        if uploadTopicID != "":
            comment_link = topic.reply(entryString).permalink()
        comments.append((datestring, botw['title'], comment_link))
        
        # Increment to next topic's date
        currentdate += nextWeek * duration
    
    # Create string for table of contents
    postString = "---\n"
    for comment in comments:
        postString += "[{0}: {1}]({2})\n\n".format(comment[0], comment[1], comment[2])
        postString += "---\n\n"
    
    # Replace topic text with this string
    if uploadTopicID != "":
        # If 'append' set, preserve previous post contents
        if append:
            postString = topic.selftext + "\n\n" + postString
        topic.edit(postString)
    
    # Also write to text file
    outTxtFile.write(postString)
    
    outTxtFile.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

