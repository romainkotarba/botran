import json
import os
import requests
import re


def load_config():
    """
    Loads a JSON configuration file
    :return: Parsed json file
    """

    cwd = os.path.dirname(__file__)
    config_file = os.path.join(cwd, 'bot-config.json')

    config = {}

    if os.path.isfile(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)

        print("Config file imported successfully")

    return config


def download_source(url):
    """
    Download a file from a provided URL
    :param url: URL of a file to download
    :return: Downloaded file name if success, None else.
    """

    headers = {'Accept': 'application/json'}
    requests.get(url)
    resp = requests.get(url, headers=headers, stream=True)
    file_name = os.path.basename(url)

    print("Start downloading: {}...".format(file_name))

    if resp.status_code != 200:
        print("Error downloading: {} {}".format(resp.status_code, resp.text))
        return

    with open(file_name, 'wb') as f:
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

    print("Successfully downloaded: {}".format(file_name))
    return file_name


def find_url_in_string(string):

    if type(string) != "string":
        return
    url_regex = '(?:(?:https?|ftp)://)(?:\S+(?::\S*)?@)?(?:(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]+-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:/[^\s]*)?'

    pattern = re.compile(url_regex, flags=re.IGNORECASE | re.DOTALL)
    matches = pattern.findall(string)
    return matches
