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


def grab_all_pages(url, request_object):
    """ Grabs text for all pages in search. """
    check_pages = re.compile('Page 1 of (\d+)')
    html_text = request_object.text

    # throw text for each page into a list and then concat everything
    num_pages = int(check_pages.findall(html_text)[0])
    if num_pages > 1:
        grab_list = [html_text]
        new_page_url = url + '&pg={num}'
        for num in range(2, num_pages+1):
            new_grab = r.get(new_page_url.format(num=num))
            grab_list.append(new_grab.text)
        html_text = '\n'.join(grab_list)
    
    return html_text


def zips_within_radius(lower_radius, upper_radius, base_zipcode):
    """
    Grabs zipcodes within desired range of provided zipcode from zip-codes.com. Must be natural numbers for bounds (0, 1, 2, ..., n, ...).
    Note that the highest bound is capped at 30.
    :param lower_radius Lower bound of range.
    :param upper_radius Upper bound of range.
    :param zipcode Zipcode we want metadata for.
    :return Dataframe containing zip of interest in first column, surrounding zips respectively in second column
    """
    # grab list of zips
    zip_url = 'https://www.zip-codes.com/zip-code-radius-finder.asp?zipmileslow={lower_radius}&zipmileshigh={upper_radius}&zip1={zipcode}'
    zip_grab = r.get(zip_url.format(lower_radius=lower_radius, upper_radius=upper_radius, zipcode=base_zipcode))
    zip_regex = re.compile('zip1={zipcode}&zip2=(\d+)"'.format(zipcode=base_zipcode))
    zips_surrounding = zip_regex.findall(zip_grab.text)

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
    :param state State associated with county.
    :param county County of interest.
    :return Dataframe containing City, State, County, and Zips.
    """
    county_output_cols = ['zips', 'city', 'county']
    county_regex_strings = ['zip-code/(\d+)/zip',
                            'city/{state}-(\w+(?:-\w+)*).asp"'.format(state=state).lower(),
                            'county/{state}-(\w+(?:-\w+)*).asp"'.format(state=state).lower()]
    county_regex = dict(zip(county_output_cols, county_regex_strings))

    county_url = "https://www.zip-codes.com/search.asp?fld-state={state}&fld-county={county}"\
                  .format(state=state, county=county)
    county_grab = r.get(county_url)
    
    # check if we need to span multiple pages and concat all text as needed
    county_grab_text = grab_all_pages(county_url, county_grab)

    # grab data for each key and make dataframe
    county_output = list()
    for key, regex in county_regex.items():
        county_key = re.findall(regex, county_grab_text)
        if not key == 'zips': 
            county_key = [e.replace('-', ' ').title() for e in county_key]
        county_output.append(county_key)

    county_dataframe = pd.DataFrame(dict(zip(county_output_cols, county_output)))
    county_dataframe['state'] = state.upper()
    
    final_cols = ['city', 'state', 'county', 'zips']
    return county_dataframe[final_cols]


def zip_coordinates(base_zipcode):
    """ 
    Returns latitude and longitude for given zipcode.
    :param base_zipcode Zipcode of interest.
    :return Single-row dataframe consisting of coordinates.
    """
    # pull latitude and longitude
    zip_url = "https://www.zip-codes.com/zip-code/{base_zipcode}/zip-code-{base_zipcode}.asp"
    zip_grab = r.get(zip_url.format(base_zipcode=base_zipcode))
    zip_coordinates_regex = re.compile('class="info">[+-]?(\d+\.\d+)</td')
    zip_lat_lng = zip_coordinates_regex.findall(zip_grab.text)[:-1]

    # return single row dataframe for coordinates
    df_cols = ['Zip', 'Latitude', 'Longitude']
    df_row = [base_zipcode] + zip_lat_lng
    return pd.DataFrame(dict(zip(df_cols, df_row)), index=range(1))