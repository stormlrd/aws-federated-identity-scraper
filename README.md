# aws-federated-identity-scraper

This script will **scrape** your roles from AWS Identity Center and create a AWS CLI v2 config file of each account / role as a profile for you. The script filters out roles containing "ReadOnly" or "Catalog" and generates both AWS CLI and Steampipe configurations.

# Usage:
1. Clone this repository
2. Open the aws_cli_primary_profile_example, tweak the configuration to your SSO and primary account/role then save it for use when first logging in
3. Copy & paste the aws_cli_primary_profile_example contents into your .aws\config file to set up your "primary" profile
4. Edit the `scrape_identities.py` file and update the configuration variables at the top of the script
5. Login to AWS SSO using aws sso login --profile primary
6. Execute the script using py scrape_identities.py
7. Transfer contents of generated/awscli_config.new into your .aws\config file

The script will also generate a Steampipe configuration file in the generated folder.

Enjoy a long life.

# Configuration
The script now contains configuration variables at the top of the file that you need to update before running:

```python
# CONFIGURATION - MODIFY THESE VALUES BEFORE RUNNING THE SCRIPT
SSO_START_URL = "your_sso_start_url"  # e.g., "https://my-sso-portal.awsapps.com/start"
SSO_REGION = "your_sso_region"        # e.g., "ap-southeast-2"
AWS_REGION = "your_region"            # e.g., "ap-southeast-2"
OUTPUT_FORMAT = "your_output_format"  # e.g., "json"
```

The script will check if these values have been updated and will exit with an error message if they haven't been changed from their default values.

# Dependencies
The script relies on a couple of things:

1. That you have set up a profile called primary for your primary login into AWS IAM Identity Center
2. That you have already logged on AWS SSO using **aws sso login --profile primary**
3. That you have updated the configuration variables at the top of the script
4. That the initial primary role you've specified has permissions to read from AWS IAM identity center using list_account_roles() & list_accounts()
5. That you have aws cli v2 installed, python3 installed and boto3 library installed for python

The initial login to aws sso requires that you have set up at least one profile in your config file for the aws cli. refer to the usage instructions.

# Troubleshooting:

## Session Token Issues
If you get this error:

```
botocore.errorfactory.UnauthorizedException: An error occurred (UnauthorizedException) when calling the ListAccounts operation: Session token not found or invalid
```

Do an `aws sso login --profile primary` again. The token has expired. I tried to write a check for this but there is a bug in the timestamp that the AWS CLI v2 writes out.

## Missing SSO Cache Directory
If you see:

```
FileNotFoundError: [Errno 2] No such file or directory: '~/.aws/sso/cache'
```

This means you haven't logged in with AWS SSO before or the cache directory is missing. Run `aws sso login --profile primary` to create the necessary cache files.

## Invalid JSON in Cache Files
If you encounter:

```
json.decoder.JSONDecodeError: Expecting value: line X column Y
```

The SSO cache files might be corrupted. Try running `aws sso logout --profile primary` followed by `aws sso login --profile primary` to regenerate the cache files.

## Permission Issues
If you see:

```
botocore.exceptions.ClientError: An error occurred (AccessDeniedException) when calling the ListAccounts operation: User is not authorized to perform action
```

The primary profile you're using doesn't have sufficient permissions to list accounts or roles. Make sure your primary profile has the necessary permissions to access AWS IAM Identity Center.

## AWS CLI Not Installed or Not in PATH
If you get:

```
FileNotFoundError: [Errno 2] No such file or directory: 'aws'
```

The AWS CLI is not installed or not in your system PATH. Install the AWS CLI v2 and ensure it's accessible from your command line.

## Python Version Compatibility
This script requires Python 3.6 or later. If you're getting syntax errors or unexpected behavior, check your Python version with:

```
python --version
```

## Missing Primary Profile
If you see:

```
Profile 'primary' not found in AWS CLI configuration. Exiting...
```

You need to create a primary profile in your AWS CLI configuration file (~/.aws/config). Use the aws_cli_primary_profile_example as a template.

## File Permission Issues
If you encounter:

```
PermissionError: [Errno 13] Permission denied: 'generated/steampipe_sp_conf.json'
```

The script doesn't have permission to write to the generated directory. Check your file permissions and ensure you have write access to the directory where the script is running.

## Special Characters in Account Names
If account names contain special characters that cause issues in profile names, you might need to modify the script to handle these characters appropriately.

## Network Connectivity Issues
If you're experiencing timeouts or connection errors when running AWS CLI commands, check your network connectivity and ensure you can reach AWS services.

## SSO Browser Authentication Failures
If the SSO login process opens a browser but fails to authenticate:

```
Failed to open the SSO authorization page
```

Try manually opening the SSO URL in your browser, or check if your default browser is properly configured. You may also need to clear browser cookies related to AWS SSO.

## Too Many Accounts or Roles
If you have a large number of AWS accounts or roles and encounter:

```
HTTPSConnectionPool(host='...', port=443): Max retries exceeded
```

The script might time out. Try increasing the timeout values in your AWS CLI configuration or modify the script to process accounts in smaller batches.

## JSON Parsing Errors in AWS CLI Output
If you see:

```
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes
```

The AWS CLI output might be malformed. Check your AWS CLI configuration, especially the output format setting.

## Missing Required Python Libraries
If you encounter:

```
ModuleNotFoundError: No module named 'boto3'
```

Install the required Python libraries:

```
pip install boto3
```

## AWS SSO Session Expiration
If your AWS SSO session expires during script execution, you might see various authentication errors. Run `aws sso login --profile primary` again to refresh your session.

## Account Names with Spaces
If account names with spaces cause issues in the generated profiles, the script already handles this by removing spaces, but you might need to adjust this behavior if it causes conflicts.

## Duplicate Profile Names
If you have multiple accounts with the same name (after space removal), you might end up with duplicate profile names. Consider modifying the script to include account IDs in profile names to ensure uniqueness.

## AWS CLI Configuration File Format Issues
If the script generates a configuration file that causes errors when used with AWS CLI:

```
configparser.ParsingError: Source contains parsing errors
```

Check the generated file for any formatting issues and ensure it follows the AWS CLI configuration file format.

## Steampipe Configuration Issues
If the generated Steampipe configuration doesn't work correctly, verify that the format matches what Steampipe expects. You might need to adjust the template used in the script.
