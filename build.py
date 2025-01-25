#!/usr/bin/env python3
# coding: utf-8
# pylint: disable=C0111
# pylint: disable=C0103
# pylint: disable=C0330

from __future__ import print_function
from datetime import datetime
import os
import sys
import traceback
import json
from operator import itemgetter
import requests
from bs4 import BeautifulSoup
import multiprocessing
from multiprocessing.pool import ThreadPool

LOCALES = ["en-us", "de-de"]
DEFAULT_LOCALE = "en-us"

SRC_MARKDOWN_FILE = "tpl.README.md"
SRC_APPS_PLACEHOLDER = '%%APPS%%'
SRC_APPSCOUNT_PLACEHOLDER = '%%APPS_COUNT%%'
SRC_TIMESTAMP_PLACEHOLDER = '%%BUILD_TIMESTAMP%%'
SRC_VERSION_PLACEHOLDER = '%%VERSION%%'
SRC_LOGO_PLACEHOLDER = '%%LOGO_PATH%%'

L10N_FOLDER = 'localized'
DIST_FOLDER = 'dist'
DIST_README = 'README.md'
DIST_JSON = 'apple-bundle-ids.json'
DIST_CSV = 'apple-bundle-ids.csv'

def download_apps(locales):
    print ('Downloading apps ...')
    locale_to_apps = {}

    for locale in locales:
        url = 'https://support.apple.com/{}/guide/deployment/depece748c41/web'.format(locale)
        print ('|--Downloading apps locale: {} ({})'.format(locale, url))
        
        html_contents = requests.get(url, allow_redirects=True)
        soup = BeautifulSoup(html_contents.text, 'html.parser')
        
        table = soup.select_one('table[data-type="Multicolumn"]')
        rows = table.find_all('tr')
        apps = []

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 2: ## skip header row
                continue
            td1 = cols[0]
            img_tag = td1.find('img')
            img_src = img_tag['src'] if img_tag else 'Not found'
            p_tag = td1.find('p')
            app_name = td1.find('p').text.strip() if p_tag else 'Not found'
            td2 = cols[1]
            p_tag = td2.find('p')
            bundle_id = p_tag.text.strip() if p_tag else 'No bundle ID found'

            apps.append([app_name, bundle_id, img_src])

        locale_to_apps[locale] = apps

    return locale_to_apps

def dist_json(apps, output_path):
    print ('Saving json: ', output_path)
    json_data = []
    for app in apps:
        obj = {
            'name': app[0],
            'bundle_id': app[1],
            'img_src': app[2],
        }
        json_data.append(obj)

    with open(output_path, 'w') as outfile:
        json.dump(json_data, outfile, indent=2, ensure_ascii=False)

def dist_csv(apps, output_path):
    print ('Saving csv: ', output_path)
    with open(output_path, 'w') as outfile:
        outfile.write("Name,BundleID,Icon\n")
        for app in apps:
            outfile.write("{0},{1},\"{2}\"\n".format(
                app[0], # icon
                app[1], # name
                app[2]  # bundle id
            ))

def dist_readme(apps, template, output_path):
    print ('Saving Markdown: ', output_path)

    app_contents = ''
    for app in apps:
        line = '| ![App Icon]({0}) | {1} |  {2}'.format(app[2], app[0], app[1]) 
        line += "\n"
        app_contents += line

    with open(output_path, 'w') as output:
        template = template.replace(SRC_APPS_PLACEHOLDER, app_contents)
        template = template.replace(SRC_APPSCOUNT_PLACEHOLDER, str(len(apps)))
        output.write(template)

#############################################################################
# Main
if __name__ == "__main__":
    try:
        cur_path = os.path.dirname(os.path.realpath(__file__))

        # preload package.json
        with open(os.path.join(cur_path, 'package.json')) as json_file:
            package_json = json.load(json_file)

        # preload README template
        with open(os.path.join(cur_path, SRC_MARKDOWN_FILE), 'r') as template:
            readme_template = template.read()
            readme_template = readme_template.replace(SRC_VERSION_PLACEHOLDER, 
                package_json['version'])
            today = datetime.today()
            readme_template = readme_template.replace(SRC_TIMESTAMP_PLACEHOLDER,
                today.strftime('%b %d, %Y at %H:%M'))

        locale_to_apps = download_apps(LOCALES)

        for locale, apps in locale_to_apps.items():
            print ('|--Saving apps for locale: ', locale)

            prefix = locale + '_'
            dist_json(apps, os.path.join(cur_path, DIST_FOLDER, prefix + DIST_JSON))
            dist_csv(apps, os.path.join(cur_path, DIST_FOLDER, prefix + DIST_CSV))
            
            tpl = readme_template.replace(SRC_LOGO_PLACEHOLDER, '../')
            dist_readme(apps, tpl, os.path.join(cur_path, L10N_FOLDER, prefix + DIST_README))
            
        tpl = readme_template.replace(SRC_LOGO_PLACEHOLDER, '' )   
        dist_readme(apps, tpl, os.path.join(cur_path, DIST_README))

        print ('Done.')
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print ("[ERROR] {0}".format(e))