#!/usr/bin/env python
######################################################
#
#    botw_genHallOfFame.py
#
#  Generates a Hall of Fame post formatted
#  for posting on Reddit.
#
#  Usage: botw_genHallOfFame.py <input.yml> <output.txt> [--format <format select>]
#
######################################################

import sys
import optparse
import operator

import yaml


#
# BEGIN FUNCTIONS FOR FORMATTER 'default'
#
def writeHallOfFameEntry(fp, botw):
    fp.write("{0}: [{1}]({2})\n\n".format(botw['datestring'], botw['title'], botw['url']))
    for winner in botw['winner']:
        winning_entry = filter(lambda x:x['entrant']==winner, botw['entries'])[0]
        fp.write("* Winner{3}: [{0} by {1}]({2})\n\n".format(winning_entry['title'], winning_entry['entrant'], winning_entry['url'], " (tied)" if len(botw['winner']) > 1 else ""))
    # Runnerup is discontinued in newer topics
    if 'runnerup' in botw:
        runnerup_entry = filter(lambda x:x['entrant']==botw['runnerup'], botw['entries'])[0]
        fp.write("* Runner up: [{0} by {1}]({2})\n\n".format(runnerup_entry['title'], runnerup_entry['entrant'], runnerup_entry['url']))
    fp.write("---\n\n")
#
# END FUNCTIONS FOR FORMATTER 'default'
#

#
# BEGIN FUNCTIONS FOR FORMATTER 'exp'
#
def writeHallOfFameHeaderAlt(fp):
    fp.write("BotW Topic|Winner(s)|Runner up\n")
    fp.write("-|-|-\n")

def writeHallOfFameEntryAlt(fp, botw):
    fp.write("[**{0}**]({1})|".format(botw['title'], botw['url']))
    fp.write(botw['datestring'] + "|")
    if len(botw['winner']) > 1:
        fp.write("**TIE**: ")
    for winner in botw['winner']:
        winning_entry = filter(lambda x:x['entrant']==winner, botw['entries'])[0]
        fp.write("[{0} by {1}]({2}){3}".format(winning_entry['title'], winning_entry['entrant'], winning_entry['url'], " AND " if len(botw['winner']) > 1 and winner != botw['winner'][-1] else ""))
    # Runnerup is discontinued in newer topics
    if 'runnerup' in botw:
        runnerup_entry = filter(lambda x:x['entrant']==botw['runnerup'], botw['entries'])[0]
        fp.write("|[{0} by {1}]({2})\n".format(runnerup_entry['title'], runnerup_entry['entrant'], runnerup_entry['url']))
    else:
        fp.write("|---\n")
#
# END FUNCTIONS FOR FORMATTER 'exp'
#

formats_dict = {
    'default': {
        'header_func': None,
        'entry_func': writeHallOfFameEntry,
    },
    'exp': {
        'header_func': writeHallOfFameHeaderAlt,
        'entry_func': writeHallOfFameEntryAlt,
    }
}

def main(argv=None):
    usage="botwParse.py <input.yml> <output.txt> [--format <format select>]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("--format", "-f", help="select output format", default="default")
    
    (options, args) = parser.parse_args()
    
    # Get arguments
    try:
        ymlName, outTxtName = args
    except ValueError:
        print "ERROR: Invalid number of arguments"
        print usage
        return 1
        
    # Select formatter based on optional argument
    formatter = formats_arr[options.format]
    
    # Load YAML database
    ymlFile = open(ymlName, "r")
    
    database = yaml.load(ymlFile)
    
    ymlFile.close()
    
    # Relevant time deltas
    nextWeek = datetime.timedelta(days=7)
    
    # Start date of first BotW (modern era)
    currentdate = datetime.date.fromordinal(database['meta']['startdate'])
    
    # Compile list of all entrants and entries
    entrants = dict()
    entries = []
    
    # Collect list of all entries and entrants
    for botw in database['botw']:
        for entry in botw['entries']:
            entries.append(entry)
            # Build list of entrants
            if entry['entrant'] not in entrants:
                entrants[entry['entrant']] = 0
            entrants[entry['entrant']] += 1
    
    # Calculate timestamps
    for botw in database['botw']:
        # If this topic has a specially marked duration,
        # increment by that many weeks. Default is 1
        duration = botw['duration'] if 'duration' in botw else 1
        
        # Store date as a string
        botw['datestring'] = "**{0}**".format(currentdate.strftime("%d %B %Y"))
        
        # Increment to next topic's date
        currentdate += nextWeek * duration
    
    outTxtFile = open(outTxtName, "w")
    
    # Generate header
    outTxtFile.write("---\n\n")
    outTxtFile.write("**Total BotW: {0}**\n\n".format(len(database['botw'])))
    outTxtFile.write("**Total unique entrants: {0}**\n\n".format(len(entrants)))
    outTxtFile.write("**Total entries: {0}**\n\n".format(len(entries)))
    
    # Hall of Fame banner
    outTxtFile.write("---\n\n")
    outTxtFile.write("## **Hall of Fame**\n\n")
    outTxtFile.write("---\n\n")
    
    #
    # Generate actual Hall of Fame using the selected formatter
    #
    
    # Not every formatter has a header
    if 'header_func' in formatter and formatter['header_func']:
        formatter['header_func'](outTxtFile)
    # Write entries
    for botw in reversed(database['botw']):
        formatter['entry_func'](outTxtFile, botw)
    
    outTxtFile.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

