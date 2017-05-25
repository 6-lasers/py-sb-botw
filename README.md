# py-sb-botw
Python tools for managing build of the week

Workflow for maintaining Hall of Fame:

1a) Run botw_scrapeJsonToYml.py with a query for finding BotW posts
1b) Manually obtain search JSON (using /r/starbound/search.json, or other means) and pass it to botw_scrapJsonToYml.py
2) Run botw_genHallOfFame.py on the YAMl produced in step 1
3) Use output of botw_genHallOfFame.py to create or edit the Hall of Fame post

botw.yml is an example of output--it is a generated file containing all entries from October 17 (beginning of 'Novakid Fluffalo Ranch') to May 23 (end of 'Monumental Disaster')

Workflow for obtaining current week's BotW entries:
<placeholder>
