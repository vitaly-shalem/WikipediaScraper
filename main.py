# ##################################################################
#  project:     wikipedia scraper
#  date:        june 2023
#  author:      vitaly shalem
#  description: a project @ becode
#               see more details in readme.md
# ##################################################################

import os
import sys
import getopt

sys.path.insert(0, os.path.abspath('.'))

from utils.leaders_scraper import *

if __name__ == "__main__":
    try:
        # scrape leaders data
        print("Retrieving data...")
        leaders_per_country = get_leaders()
        # save results in a json file
        print("Saving results...")
        output_file = save(leaders_per_country)
        print("PLease, check leaders.json in the project folder...")
    except getopt.GetoptError:
        sys.exit(-1)
