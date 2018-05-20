[![CircleCI](https://circleci.com/gh/cacocracy/minimic/tree/development.svg?style=svg)](https://circleci.com/gh/cacocracy/minimic/tree/development)

# Minimic

A inventory-management tool.

## Install

Once cloned locally, create a virtualenv, `cd` into the repo, and...

`pip install -e .`

The command `minimic` will then be available.

## Recipes

1. To get the profiles of the 10-most galleried profiles in inventory.
   
   `minimic inventory | head -n 10 | awk '{ print $1 }' | minimic profile`

2. Disk usage of archive
   
   `du -h $MINIMIC_ARCHIVE`

3. Save a set of galleries from a list
   
   `cat listfile_of_ids | minimic gallery`

4. Check archive for errors
   
   `minimic status`

