# aws-federated-identity-scraper

This script will **scrape** your roles from AWS Identity Center and create a AWS CLI v2 config file of each account / role as a profile for you. The script filters out roles containing "ReadOnly" or "Catalog" and generates both AWS CLI and Steampipe configurations.

# Usage:
1. Clone this repository
2. Open the aws_cli_primary_profile_example, tweak the configuration to your SSO and primary account/role then save it for use when first logging in
3. Copy & paste the aws_cli_primary_profile_example contents into your .aws\config file to set up your "primary" profile
4. Login to AWS SSO using aws sso login --profile primary
5. Execute the script using py scrape_identities.py
6. Transfer contents of generated/awscli_config.new into your .aws\config file

The script will also generate a Steampipe configuration file in the generated folder.

Enjoy a long life.

# Hardcoded Configuration
The script now contains hardcoded values at line 171 that you need to update before running:

1. In `scrape_identities.py`, update the following hardcoded values in the `config[section_name]` dictionary:
   - `sso_start_url`: Your SSO portal URL (e.g., "https://my-sso-portal.awsapps.com/start")
   - `sso_region`: Your SSO region (e.g., "ap-southeast-2")
   - `region`: Your preferred AWS region (e.g., "ap-southeast-2")
   - `output`: Your preferred output format (e.g., "json")

# Dependencies
The script relies on a couple of things:

1. That you have set up a profile called primary for your primary login into AWS IAM Identity Center
2. That you have already logged on AWS SSO using **aws sso login --profile primary**
3. That you have updated the hardcoded configuration values in the script
4. That the initial primary role you've specified has permissions to read from AWS IAM identity center using list_account_roles() & list_accounts()
5. That you have aws cli v2 installed, python3 installed and boto3 library installed for python

The initial login to aws sso requires that you have set up at least one profile in your config file for the aws cli. refer to the usage instructions.

# TroubleShooting:
If you get this error:

	*botocore.errorfactory.UnauthorizedException: An error occurred (UnauthorizedException) when calling the ListAccounts operation: Session token not found or invalid*

do an aws sso login again. the token has expired. I tried to write a check for this but there is a bug in the timestamp that the AWS CLI v2 writes out.
