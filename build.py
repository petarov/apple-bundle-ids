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
import requests
from bs4 import BeautifulSoup
import hashlib

LOCALES = ["en-us", "de-de"]
LOCALE_NAMES = ["English", "Deutsch"]
DEFAULT_LOCALE = "en-us"

SRC_README = "tpl.README.md"
SRC_APPS_PLACEHOLDER = '%%APPS%%'
SRC_APPSCOUNT_PLACEHOLDER = '%%APPS_COUNT%%'
SRC_TIMESTAMP_PLACEHOLDER = '%%BUILD_TIMESTAMP%%'
SRC_VERSION_PLACEHOLDER = '%%VERSION%%'
SRC_LOGO_PLACEHOLDER = '%%LOGO_PATH%%'
SRC_L10N_LINKS_PLACEHOLDER = '%%L10N_LINKS%%'

L10N_FOLDER = 'localized'
DIST_FOLDER = 'dist'
DIST_README = 'README.md'
DIST_JSON = 'apple-bundle-ids.json'
DIST_CSV = 'apple-bundle-ids.csv'

def download_apps(locales, force, cur_lock):
    print ('Downloading apps ...')
    locale_to_apps = {}
    publish_date = None

    for locale in locales:
        url = 'https://support.apple.com/{}/guide/deployment/depece748c41/web'.format(locale)
        print ('|--locale: {} ({})'.format(locale, url))
        
        html_contents = requests.get(url, allow_redirects=True)
        soup = BeautifulSoup(html_contents.text, 'html.parser')
        
        table = soup.select_one('table[data-type="Multicolumn"]')
        rows = table.find_all('tr')
        apps = []

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 2: ## Skip header row
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

        if locale == "en-us": ## Note! this always assumes english
            rows = soup.find_all('footer')
            for row in rows:
                publish_date = row.text.strip()
                if publish_date.startswith('Published'):
                    publish_date = publish_date.split(":", 1)[1].strip()

                    ## It's bad practice to just sys.exit here, but it's a simple
                    ## script and it makes sense to stop downloading data ASAP
                    if encode_lock(publish_date) == cur_lock and not force:
                        print ('No changes found: update skipped')
                        sys.exit(0)

                    break

        locale_to_apps[locale] = apps

    if not publish_date:
        raise Exception('No publish date <footer> found')        

    return locale_to_apps, publish_date

def dist_json(apps, output_path):
    print ('|--Saving json: ', output_path)
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
    print ('|--Saving csv: ', output_path)
    with open(output_path, 'w') as outfile:
        outfile.write("Name,BundleID,Icon\n")
        for app in apps:
            outfile.write("{0},{1},\"{2}\"\n".format(
                app[0], # Icon
                app[1], # Name
                app[2]  # Bundle ID
            ))

def dist_readme(apps, template, output_path):
    print ('|--Saving markdown: ', output_path)

    app_contents = ''
    for app in apps:
        line = '| ![App Icon]({0}) | {1} |  {2}'.format(app[2], app[0], app[1]) 
        line += "\n"
        app_contents += line

    with open(output_path, 'w') as output:
        template = template.replace(SRC_APPS_PLACEHOLDER, app_contents)
        template = template.replace(SRC_APPSCOUNT_PLACEHOLDER, str(len(apps)))
        output.write(template)

def encode_lock(token):
    return hashlib.md5(token.encode()).hexdigest()

def create_lock(token, output_path):
    print ('Generating lock ...')
    with open(output_path, 'w') as output:
        output.write(encode_lock(token))

def load_lock(lock_path):
    if not os.path.exists(lock_path):
        return None

    with open(lock_path, 'r') as f:
        return f.read()

#############################################################################
# Main
if __name__ == "__main__":
    try:
        force_download = False
        if len(sys.argv) > 1:
            force_download = sys.argv[1] == '--force'

        cur_path = os.path.dirname(os.path.realpath(__file__))
        lock_path = os.path.join(cur_path, 'build.lock')

        ## Peload package.json
        with open(os.path.join(cur_path, 'package.json')) as json_file:
            package_json = json.load(json_file)

        ## Preload README template
        with open(os.path.join(cur_path, SRC_README), 'r') as template:
            readme_template = template.read()
            readme_template = readme_template.replace(SRC_VERSION_PLACEHOLDER, 
                package_json['version'])
            today = datetime.today()
            readme_template = readme_template.replace(SRC_TIMESTAMP_PLACEHOLDER,
                today.strftime('%b %d, %Y at %H:%M'))

        ## Download apps from Apple
        locale_to_apps, publish_date = download_apps(locales=LOCALES, 
                                                     force=force_download,
                                                     cur_lock=load_lock(lock_path))

        ## Generate dist folder contents and localizations
        for locale, apps in locale_to_apps.items():
            print ('Generating locale: ', locale)

            prefix = locale + '_'
            dist_json(apps, os.path.join(cur_path, DIST_FOLDER, prefix + DIST_JSON))
            dist_csv(apps, os.path.join(cur_path, DIST_FOLDER, prefix + DIST_CSV))
            
            tpl = readme_template.replace(SRC_LOGO_PLACEHOLDER, '../')
            tpl = tpl.replace(SRC_L10N_LINKS_PLACEHOLDER, '')
            dist_readme(apps, tpl, os.path.join(cur_path, L10N_FOLDER, prefix + DIST_README))

        ## Create default README.md
        print ('Generating defaults ...')
        tpl = readme_template.replace(SRC_LOGO_PLACEHOLDER, '')
        l10n_links = ''
        for i, locale in enumerate(LOCALES):
            l10n_links += '[{}]({})'.format(LOCALE_NAMES[i], 
                os.path.join(L10N_FOLDER, locale + '_' + DIST_README))
            if i < len(LOCALES) - 1:
                l10n_links += ' | '
        tpl = tpl.replace(SRC_L10N_LINKS_PLACEHOLDER, l10n_links)
        dist_readme(apps, tpl, os.path.join(cur_path, DIST_README))

        ## Create last-update hash-lock
        create_lock(publish_date, lock_path)

        print ('Done.')
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        print ("[ERROR] {0}".format(e))