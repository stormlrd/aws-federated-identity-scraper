# Define keywords to filter out roles
keywords_to_filter = ["ReadOnly", "Catalog"]

import os
import json
import configparser
import subprocess
from pathlib import Path
from datetime import datetime

def clear_screen():
    # Clear the screen based on the OS
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def list_files():
    cache_dir = os.path.expanduser("~/.aws/sso/cache")
    files = os.listdir(cache_dir)
    files = [os.path.join(cache_dir, file) for file in files]
    files = [(file, os.path.getmtime(file)) for file in files if os.path.isfile(file)]
    files.sort(key=lambda x: x[1], reverse=True)
    return files

def get_sso_access_token():
    files = list_files()
    if not files:
        raise FileNotFoundError("No SSO cache files found.")
    
    newest_file = files[0][0]
    with open(newest_file, 'r') as f:
        cache_data = json.load(f)
    
    if 'accessToken' not in cache_data:
        raise KeyError("accessToken not found in the cache file.")
    
    return cache_data['accessToken']

def check_profile_exists(profile_name):
    aws_config_file = os.path.expanduser("~/.aws/config")
    config = configparser.ConfigParser()
    config.read(aws_config_file)
    return f"profile {profile_name}" in config.sections()

def role_matches_keywords(role_name, keywords):
    return any(keyword.lower() in role_name.lower() for keyword in keywords)

#################################################
# MAIN
#################################################
version = "1.00"
# clear the screen
clear_screen()

# print banner
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print(f"scrape_identities v {version}")
print("Author: Paul Dunlop")
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
print ("Roles to filter: ", keywords_to_filter)

# Check if the 'primary' profile exists
if not check_profile_exists("primary"):
    print("Profile 'primary' not found in AWS CLI configuration. Exiting...")
    exit()

# ensure the profile is logged out so we can log in and get json file wiht a latest time stamp
print("logging out of primary profile...")
subprocess.run(['aws', 'sso', 'logout', '--profile', 'primary'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# then initiate the login 
print("logging into primary profile...")
subprocess.run(['aws', 'sso', 'login', '--profile', 'primary'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# then get the access token
print("getting access token from most recent json file in sso cache folder")
accesstoken = get_sso_access_token()

print("Discovering accounts in AWS...")
# Run AWS CLI command to get account list
aws_cli_command = ["aws", "sso", "list-accounts", "--profile", "primary", "--max-results", "999", "--access-token", accesstoken]
accountList_process = subprocess.run(aws_cli_command, capture_output=True, text=True)
accountList_output = accountList_process.stdout
accounts = json.loads(accountList_output)

# make the generated folder
# Define the name of the folder to be created
folder_name = "generated"

# Get the current working directory
current_directory = os.getcwd()

# Construct the full path of the new folder
folder_path = os.path.join(current_directory, folder_name)

# Create the generated folder
try:
    os.makedirs(folder_path, exist_ok=True)
    print(f"Folder '{folder_name}' created successfully in {current_directory}.")
except Exception as e:
    print(f"An error occurred while creating the folder: {e}")

# Loop through each account in the account list and get the roles
config = configparser.ConfigParser()
config_file_path = "generated/awscli_config.new"

# remove the steampipe config file first
if os.path.exists("generated/steampipe_sp_conf.json"):
    os.remove('generated/steampipe_sp_conf.json') # get rid of any pre-existing files

# open a new one
file = open("generated/steampipe_sp_conf.json","w")
aws_all = "" # tracking var

print("Scraping your roles per account...")
for account in accounts["accountList"]:
    accountId = account["accountId"]
    aws_cli_command = f"aws sso list-account-roles --max-results 999 --profile primary --account-id {accountId} --access-token {accesstoken}"
    roles_output = subprocess.check_output(aws_cli_command, shell=True)
    roles = json.loads(roles_output)

    temp_account_name = account["accountName"].replace(" ", "")
    for role in roles["roleList"]:
        temp_role_name = role["roleName"]
        if role_matches_keywords(temp_role_name, keywords_to_filter):
            continue  # Skip roles that match the filter keywords

        temp_role_accountId = role["accountId"]
        section_name = f"profile {temp_account_name}-{temp_role_name}"
        sp_section_name = "connection \"aws_" + temp_account_name.replace("-","_") + "_" + temp_role_name.replace("-","_") + "\" {\n" 
        config[section_name] = {
            'sso_start_url': 'your_sso_start_url',
            'sso_region': 'your_sso_region',
            'sso_account_id': temp_role_accountId,
            'sso_role_name': temp_role_name,
            'region': 'your_region',
            'output': 'your_output_format'
        }

        file.write(sp_section_name)
        file.write('\tplugin  = \"aws\"\n')
        line = "\tprofile = \"" + temp_account_name + "-" + temp_role_name + "\"\n" 
        file.write(line)
        file.write('\tregions = ["*"]\n')
        file.write('}\n\n')

        if aws_all == "":
            aws_all = aws_all + "\"aws_" + temp_account_name.replace("-","_") + "_" + temp_role_name.replace("-","_") + "\""
        else:
            aws_all = aws_all + ",\"aws_" + temp_account_name.replace("-","_") + "_" + temp_role_name.replace("-","_") + "\""

# write out the final aggregator for the search path for steampipe
file.write("connection \"all_aws\" {\n")
file.write('\tplugin  = \"aws\"\n')
file.write('\ttype = \"aggregator\"\n')
file.write('\tconnections = ['+aws_all+']\n')
file.write('}\n\n')

if os.path.exists("generated/awscli_config.new"):
    os.remove('generated/awscli_config.new') # get rid of any pre-existing files
with open('generated/awscli_config.new', 'w') as configfile:
    config.write(configfile)

file.close()
print("\nFinished.\n\nnew config files for aws cli and steampipe in the generated folder.")