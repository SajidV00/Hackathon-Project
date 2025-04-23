import json
from collections import defaultdict
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

JIRA_DOMAIN = 'smartoci.atlassian.net'
EMAIL = 'talqeen.ahmad@vroozi.com'
API_TOKEN = 'ATATT3xFfGF0iT9TMX5uO3qBSsRsRwrWdjfvEnnPsn5R0gtoIh4_TmumkS3XZ5PAtcUZSsBJGFoiPdQln4edat9jt1fBPEksIXn_MXHZebfoQlVIbsKoveHMWvvHT-biflfHbZm2Mjem5Lboq8akKwncNoiHEphaC8IhAzbbla__pvPR7J2_DT4=66ACB0F8'
PAGE_SIZE = 50
EPIC_LINK_FIELD_ID = 'customfield_11400'
URL = f'https://{JIRA_DOMAIN}/rest/api/3/search'

AUTH = HTTPBasicAuth(EMAIL, API_TOKEN)
HEADERS = {
    'Accept': 'application/json'
}
parent_issue_ids = []


def extract_plain_text_from_adf(adf):
    if not adf or 'content' not in adf:
        return ''

    text_chunks = []

    def walk(node):
        if isinstance(node, dict):
            if node.get('type') == 'text':
                text_chunks.append(node.get('text', ''))
            for child in node.get('content', []):
                walk(child)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(adf.get('content'))
    return ' '.join(text_chunks).strip()


def execute_jira_query(query):
    raw_issues_response = []
    start_at = 0
    while True:
        query['startAt'] = start_at
        response = requests.get(URL, headers=HEADERS, params=query, auth=AUTH)
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code} - {response.text}")
            raise Exception(response.text)
        data = response.json()
        issues = data.get('issues', [])
        if not issues:
            break
        raw_issues_response.extend(issues)
        start_at += PAGE_SIZE
        if start_at >= data.get('total', 0):
            break

    result = []
    for raw_issue in raw_issues_response:
        key = raw_issue['key']
        fields = raw_issue['fields']
        issue_type = fields.get('issuetype', {}).get('name')
        summary = fields.get('summary')
        status = fields.get('status', {}).get('name')
        assignee = fields.get('assignee', {}).get('displayName') if fields.get('assignee') else 'Unassigned'
        created = fields.get('created')
        description = extract_plain_text_from_adf(fields.get('description'))

        result.append({
            'key': key,
            'summary': summary,
            'description': description,
            'status': status,
            'assignee': assignee,
            'created': created,
            'issue_type': issue_type,
            'parent_id': fields.get(EPIC_LINK_FIELD_ID)
        })

    return result


def add_parent_issues_info(existing_tickets_data):
    query = {
        'jql': f'issuekey in ({",".join(parent_issue_ids)})',
        'maxResults': 50,
        'fields': 'summary,status,assignee,created,description'
    }
    api_data = execute_jira_query(query)
    items = {item['key']: item for item in api_data}
    for element in existing_tickets_data:
        epic_key = element['epic']['key']
        if epic_key in items:
            api_item = items[epic_key]
            element['epic'].update({
                'summary': api_item.get('summary'),
                'description': api_item.get('description'),
                'status': api_item.get('status'),
                'assignee': api_item.get('assignee'),
                'created': api_item.get('created')
            })


def extract_jira_data(rc_name):
    query = {
        'jql': f'fixversion = {rc_name} ORDER BY created DESC',
        'maxResults': PAGE_SIZE,
        'fields': f'summary,status,assignee,created,description,{EPIC_LINK_FIELD_ID},issuetype'
    }
    grouped_issues = defaultdict(list)
    epics_info = {}

    all_issues = execute_jira_query(query)
    for issue in all_issues:
        if issue['issue_type'].lower() == 'epic':
            issue['released_in_current_rc'] = True
            epics_info[issue['key']] = issue
        else:
            epic_key = issue['parent_id']
            if epic_key:
                grouped_issues[epic_key].append(issue)
                parent_issue_ids.append(epic_key)
            else:
                grouped_issues['No Epic'].append(issue)

    final_output = []

    for epic_key, children in grouped_issues.items():
        epic = epics_info.get(epic_key, {'key': epic_key, 'released_in_current_rc': False})
        final_output.append({
            'epic': epic,
            'issues': children
        })

    add_parent_issues_info(final_output)

    folder_path = Path("./data")
    folder_path.mkdir(parents=True, exist_ok=True)
    output_file_name = f'{folder_path}/{rc_name}.json'
    with open(output_file_name, 'w') as f:
        json.dump(final_output, f, indent=2)

    print(f"Grouped {len(all_issues)} issues under {len(final_output)} epics. Saved to '{output_file_name}'")
