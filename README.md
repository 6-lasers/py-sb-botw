# py-sb-botw
Python tools for managing build of the week

## Workflow for maintaining Hall of Fame:

1a) Run botw_scrapeJsonToYml.py with a query for finding BotW posts (in the past, used "title:botw author:Syntax1985")

1b) Manually obtain search JSON (using /r/starbound/search.json, or other means) and pass it to botw_scrapJsonToYml.py

2\) Run botw_genHallOfFame.py on the YAMl produced in step 1

3\) Use output of botw_genHallOfFame.py to create or edit the Hall of Fame post

botw.yml is an example of output--it is a generated file containing all entries from October 17 (beginning of 'Novakid Fluffalo Ranch') to May 23 (end of 'Monumental Disaster')

## Workflow for obtaining current week's BotW entries:

1) Run botw_entriesJsonToPost.py with the appropriate arguments. Typically use "title:botw" for the query, and skip=1 if next week's topic had already been posted, else skip=0

2) Examine print output from botw_entriesJsonToPost.py to eliminate false positives and select the winner. Selecting winner maybe better to do by hand for now since the calls separating out the false positives in the sort are extremely naive

TODO: Need to add appropriate cutoff detection to know which posts "belong" in the current week. Old method won't work anymore (see comments in script)
