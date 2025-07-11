Download asset pngs from Influence SDK into an icons subdirectory. Combine resources with buildings into this single directory.
https://github.com/influenceth/sdk/tree/next/assets/icons

production_chains.json: found on the Influence discord. I assume this will dramatically change later on and this will need to be re-worked.

productbot.py: Update path to productbot.conf and update insert path for reporting functions

reporting/productionChain.py: Update path to productbot.conf

restart_productbot.sh: Paths would need to be changed to the actual install path

productbot.conf: commits are ignored and some explanation is needed on how to rebuild productbot.conf:

[productbot]
token = productbot discord token goes here
product_channel = productbot discord channel id goes here

[production]
json = '/path/to/productbot/production_chains.json'

[icons]
icons_path = /path/to/icons
