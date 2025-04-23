import os

import markdown
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
CONFLUENCE_BASE_URL = 'https://smartoci.atlassian.net/wiki'
USERNAME = os.getenv('ATLASSIAN_USER_EMAIL')
API_TOKEN = os.getenv('ATLASSIAN_API_TOKEN')
SPACE_KEY = 'TS'
PARENT_PAGE_ID = 4421320706
MARKDOWN_FILE = '../data/release.md'


def openingRMFile():
    with open('/Users/sajidsaleem/Documents/Hackathon-Project/data/release.md', 'r', encoding='utf-8') as f:
        md_content = f.read()
        html_content = markdown.markdown(md_content)
        soup = BeautifulSoup(html_content, 'html.parser')
        confluence_body = str(soup)
        return confluence_body


def get_page_id(title):
    url = f'{CONFLUENCE_BASE_URL}/rest/api/content'
    params = {'title': title, 'spaceKey': SPACE_KEY}
    response = requests.get(url, auth=(USERNAME, API_TOKEN), params=params)
    results = response.json().get('results')
    return results[0]['id'] if results else None


def push_to_confluence(rc_name):
    confluence_body = openingRMFile()
    page_title = f'{rc_name} Release Notes'
    page_id = get_page_id(page_title)

    headers = {
        'Content-Type': 'application/json'
    }

    if page_id:
        version_url = f'{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}'
        version_info = requests.get(version_url, auth=(USERNAME, API_TOKEN)).json()
        current_version = version_info['version']['number']

        data = {
            "id": page_id,
            "type": "page",
            "title": page_title,
            "space": {"key": SPACE_KEY},
            "body": {
                "storage": {
                    "value": confluence_body,
                    "representation": "storage"
                }
            },
            "version": {"number": current_version + 1}
        }
        url = f'{CONFLUENCE_BASE_URL}/rest/api/content/{page_id}'
        response = requests.put(url, json=data, auth=(USERNAME, API_TOKEN), headers=headers)
        print("Page updated:", response.status_code)
    else:
        data = {
            "type": "page",
            "title": page_title,
            "space": {"key": SPACE_KEY},
            "body": {
                "storage": {
                    "value": confluence_body,
                    "representation": "storage"
                }
            }
        }
        if PARENT_PAGE_ID:
            data["ancestors"] = [{"id": PARENT_PAGE_ID}]
        url = f'{CONFLUENCE_BASE_URL}/rest/api/content/'
        response = requests.post(url, json=data, auth=(USERNAME, API_TOKEN), headers=headers)
        print("Page created:", response.status_code)
