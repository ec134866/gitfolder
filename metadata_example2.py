# You can use this script to login to the Tableau Server or Tableau Online using Tableau REST API and Tableau Server Client library,
# get the list of all workbook owners, and export it as a .csv file.

import getpass, argparse, logging
import tableauserverclient as TSC
import pandas as pd

# Creates arguments which a user needs to enter to login to the server.

parser = argparse.ArgumentParser()
parser.add_argument("--logging-level", "-l", choices=['debug','info','error'],
                    default='error')
parser.add_argument("--site_id", "-i", required=True)
parser.add_argument("--site_url", "-s", required=True,
                    help='url in the format "https://SITE_URL" where SITE_URL is the URL of your Tableau server')

login_mutual_exclusion = parser.add_mutually_exclusive_group(required=True)
login_mutual_exclusion.add_argument("--username", "-u")
login_mutual_exclusion.add_argument("--token_name", '-n')

args = parser.parse_args()

# Sets logging level based on the user's input or uses the default 'error' level

logging_level = getattr(logging, args.logging_level.upper())
logging.basicConfig(level = logging_level)


site_id = args.site_id
print("Site ID is ", site_id)
site_url = args.site_url
print("Site URL is ", site_url)

# Updates the REST API's version to the most recent one, depending on the user's server version
server = TSC.Server(site_url, use_server_version=True)

# Authenticating the user based on their server's username and password
if args.username:
    username = args.username
    password = getpass.getpass("Input your password: ")
    tableau_auth = TSC.TableauAuth(username,password,site_id)
    server.auth.sign_in(tableau_auth)
    print("Logged in to the server {} as a user {}.".format(site_url,username))

# Authenticating the user based on their server's Personal Access Token
else:
    token_name = args.token_name
    personal_access_token = input("Input your Personal Access Token: ")
    tableau_auth = TSC.PersonalAccessTokenAuth(token_name=token_name,
                                               personal_access_token=personal_access_token,
                                               site_id=site_id)
    server.auth.sign_in_with_personal_access_token(tableau_auth)
    print("Logged in to the server {} with the token {}.".format(site_url,args.token_name))

# Gets information about all workbooks on the server as well as gets information about a workbook's owner based on the
# owner id.

all_workbooks, pagination_item = server.workbooks.get()
workbook_data = [{"workbook_name": workbook.name,
                      "size": workbook.size,
                      "created_at":workbook.created_at,
                      "owner_id":workbook.owner_id,
                      "owner_name": server.users.get_by_id(workbook.owner_id).name}
                     for workbook in all_workbooks]

# Creates a dataframe with the data about workbooks and export it as a .csv file.

df = pd.DataFrame.from_dict(workbook_data)
print(df)
df.to_csv("list_workbooks.csv", index=False)
print("CSV file was saved to the same folder as this script.")

# Logs out of the server

server.auth.sign_out()
print('Logged out of the server {}'.format(site_url))