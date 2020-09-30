import sys
import json
import pandas as pd
import numpy as np
import re
import requests as r


def json_dumper(dict_to_dump, json_path):
    """Export dictionary to designated folder in JSON format"""
    json_file = json.dumps(dict_to_dump, indent=4)
    with open(json_path, 'w') as f:
        f.write(json_file)
    print("Successfully exported dict to JSON!")


def json_loader(json_path):
    try:
        with open(json_path, 'r') as f0:
            json_object = json.load(f0)
        return json_object
    except json.decoder.JSONDecodeError:
        print('Unable to import content!')
        sys.exit()


def zips_within_radius(lower_radius, upper_radius, base_zipcode):
    """
    Grabs zipcodes within desired range of provided zipcode from zip-codes.com. Must be natural numbers for bounds (0, 1, 2, ..., n, ...).
    :param lower_radius Lower bound of range.
    :param upper_radius Upper bound of range.
    :param zipcode Zipcode we want metadata for.
    :return Dataframe containing zip of interest in first column, surrounding zips respectively in second column
    """
    # grab list of zips
    zip_url = 'https://www.zip-codes.com/zip-code-radius-finder.asp?zipmileslow={lower_radius}&zipmileshigh={upper_radius}&zip1={zipcode}'
    zip_grab = r.get(zip_url.format(lower_radius=lower_radius, upper_radius=upper_radius, zipcode=base_zipcode))
    zip_regex_string = 'zip1={zipcode}&zip2=(\d+)"'.format(zipcode=base_zipcode)
    zips_surrounding = re.findall(zip_regex_string, zip_grab.text)

    if len(zips_surrounding) == 0:
        raise ValueError("couldn't find surrounding zips")

    # make dataframe
    zips_surrounding_as_rows = list()
    zip_range_string = 'Zip_within_{upper_radius}_miles'.format(upper_radius=upper_radius)
    for zipcode in zips_surrounding:
        zip_dict = {'Zip': base_zipcode,
                    zip_range_string: zipcode}
        zips_surrounding_as_rows.append(pd.DataFrame(zip_dict, index=range(1)))

    return pd.concat(zips_surrounding_as_rows).reset_index(drop=True)


def zips_in_county(state, county):
    """
    Grabs metadata for all zipcodes in desired state and county combo.
    :param state Zipcode we want metadata for.
    :param county Upper bound of range.
    :return Dataframe containing zip of interest in first column, surrounding zips respectively in second column
    """
    county_output_cols = ['zips', 'city', 'county']
    county_regex_strings = ['zip-code/(\d+)/zip',
                            'city/{state}-(\w+).asp"'.format(state=state).lower(),
                            '{state}-{county}.asp">(\w+)</a>'.format(state=state, county=county).lower()]

    county_url = "https://www.zip-codes.com/search.asp?fld-state={state}&fld-county={county}"
    county_grab = r.get(county_url.format(state=state, county=county))
    county_regex = dict(zip(county_output_cols, county_regex_strings))

    # grab data for each key and make dataframe
    county_output = list()
    for key, regex in county_regex.items():
        county_key = re.findall(regex, county_grab.text)
        if not key == 'zips': 
            county_key = [e.title() for e in county_key]
        county_output.append(county_key)

    county_dataframe = pd.DataFrame(dict(zip(county_output_cols, county_output)))
    county_dataframe['state'] = state.upper()
    
    final_cols = ['city', 'state', 'county', 'zips']
    return county_dataframe[final_cols]