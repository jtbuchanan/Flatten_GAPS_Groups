prefix = "Group Name Starts With"

import httplib2
import os

from apiclient.discovery import build
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/admin.directory.group'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Nested Group Sync'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'admin-directory_v1-NestedGroupSync.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print 'Storing credentials to' + credential_path
    return credentials


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('admin', 'directory_v1', http=http)

    # Find all groups that start with prefix
    results = service.groups().list(domain='logentries.com',
                                    maxResults=None).execute()
    all_groups = results.get('groups')
    t_groups_to_query = []

    for t_group in all_groups:
        if t_group['name'].startswith(prefix):
            t_groups_to_query.append(t_group['email'])

    print "These are the top level " + prefix + " groups: "
    print str(t_groups_to_query)

    for current_tgroup in t_groups_to_query:
        current_top_group_users = get_nested_group_members(service,
                                                           current_tgroup)

        ''' For each user returned in current_top_group_users add
            to current_tgroup '''
        for myuser in current_top_group_users:
            add_user_to_group(service, myuser['email'], current_tgroup)

        current_top_group_users = []


def get_nested_group_members(service, grpToQuery, target=None):
    if target is None:
        target = []

    nested_groups = []
    grpToQuery_results = service.members().list(groupKey=grpToQuery,
                                                pageToken=None,
                                                maxResults=None).execute()
    all_group_members = grpToQuery_results.get('members', [])

    for member in all_group_members:
        if member['type'] == 'GROUP':
            if member not in nested_groups:
                nested_groups.append(member)
        else:
            target.append(member)

    if len(nested_groups):
        for group in nested_groups:
            get_nested_group_members(service, group['email'], target)

    return target


def add_user_to_group(service, user, group):
    request_body = {'email': user,
                    'role': 'MEMBER'
                    }

    try:
        response = service.members().insert(groupKey=group,
                                            body=request_body).execute()
        print "##########################################"
        print response
        print " "
        print 'added ' + user + ' to group ' + group
        print "##########################################"
    except Exception, e:
        print "User: " + user + " already a member of " + group + ". Cont.."
        pass


if __name__ == '__main__':
    main()
