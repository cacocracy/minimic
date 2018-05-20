[![CircleCI](https://circleci.com/gh/cacocracy/minimic/tree/development.svg?style=svg)](https://circleci.com/gh/cacocracy/minimic/tree/development)

# Minimic

A inventory-management tool.

## Recipes

1. To get the profiles of the 10-most galleried profiles in inventory.
   `minimic inventory | head -n 10 | awk '{ print $1 }' | minimic profile`
