#!/usr/bin/env python
######################################################
#
#    botw_genHallOfFame.py
#
#  Generates a Hall of Fame post formatted
#  for posting on Reddit.
#
#  Usage: botw_genHallOfFame.py <input.yml> <output.txt>
#
######################################################

import sys
import optparse
import operator

import yaml

def main(argv=None):
    usage="botwParse.py <input.yml> <output.txt>"
    parser = optparse.OptionParser(usage=usage)
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        ymlName, outTxtName = args
    except ValueError:
        print "ERROR: Invalid number of arguments"
        print usage
        return 1
    
    # Load YAML database
    ymlFile = open(ymlName, "r")
    
    database = yaml.load(ymlFile)
    
    ymlFile.close()
    
    # Compile list of all entrants and entries
    entrants = dict()
    winners = dict()
    runnersup = dict()
    entries = []
    
    outTxtFile = open(outTxtName, "w")
    
    # Collect list of all entries
    for botw in database['botw']:
        for entry in botw['entries']:
            entries.append(entry)
    
    # Collect list of all entrants, winners, and runners up
    for botw in database['botw']:
        for entry in botw['entries']:
            # Build list of entrants
            if entry['entrant'] not in entrants:
                entrants[entry['entrant']] = 0
            entrants[entry['entrant']] += 1
        # 'winner' is an array since there can be a tie
        for winner in botw['winner']:
            if winner not in winners:
                winners[winner] = 0
            winners[winner] += 1
        # 'runnerup' is hand-selected, so there can't be a tie--implemented as scalar
        if botw['runnerup'] not in runnersup:
            runnersup[botw['runnerup']] = 0
        runnersup[botw['runnerup']] += 1
    
    # Generate header
    outTxtFile.write("---\n\n")
    outTxtFile.write("**Total BotW: {0}**\n\n".format(len(database['botw'])))
    outTxtFile.write("**Total unique entrants: {0}**\n\n".format(len(entrants)))
    outTxtFile.write("**Total entries: {0}**\n\n".format(len(entries)))
    
    # Hall of Fame banner
    outTxtFile.write("---\n\n")
    outTxtFile.write("## **Hall of Fame**\n\n")
    outTxtFile.write("---\n\n")
    # Generate actual Hall of Fame
    for botw in reversed(database['botw']):
        outTxtFile.write("[{0}]({1})\n\n".format(botw['title'], botw['url']))
        for winner in botw['winner']:
            winning_entry = filter(lambda x:x['entrant']==winner, botw['entries'])[0]
            outTxtFile.write("* Winner{3}: [{0} by {1}]({2})\n\n".format(winning_entry['title'], winning_entry['entrant'], winning_entry['url'], " (tied)" if len(botw['winner']) > 1 else ""))
        runnerup_entry = filter(lambda x:x['entrant']==botw['runnerup'], botw['entries'])[0]
        outTxtFile.write("* Runner up: [{0} by {1}]({2})\n\n".format(runnerup_entry['title'], runnerup_entry['entrant'], runnerup_entry['url']))
        outTxtFile.write("---\n\n")
    
    outTxtFile.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

