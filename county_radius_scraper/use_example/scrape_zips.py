import os
from county_radius_scraper import scrape_tools as s

CONFIG_PARENT_PATH = os.getcwd()
CONFIG_PATH = os.path.join(CONFIG_PARENT_PATH, 'scrape_config.json')

CONFIG = s.json_loader(CONFIG_PATH)
RADIUS_CONFIG = CONFIG['within_radius']
COUNTY_CONFIG = CONFIG['county']

if __name__ == "__main__":
    print(s.zips_within_radius(**RADIUS_CONFIG))
    print(s.zips_in_county(**COUNTY_CONFIG))
    print(s.zip_coordinates(RADIUS_CONFIG['base_zipcode']))
