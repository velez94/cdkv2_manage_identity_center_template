import os

from aws_cdk import Environment
from .helper import load_yamls, load_policies
import isodate

# Load environment definitions
dirname = os.path.dirname(__file__)
props = (load_yamls(os.path.join(dirname, "./environment_options/environment_options_delegate.yaml")))[0]
props_root = (load_yamls(os.path.join(dirname, "./environment_options/environment_options_master.yaml")))[0]

env_client_prd_account = Environment(account=props['account_sso'], region=props['region_sso'])
env_client_prd_root_account = Environment(account=props_root['account_sso'], region=props_root['region_sso'])

env_client_devsecops_account = Environment(account=props['account_devsecops'], region=props['region_devsecops'])

# Convert Values
for ps in props['permissions_set']:
    ps['session_duration'] = isodate.duration_isoformat(isodate.Duration(hours=int(ps['session_duration'])))
    if  ps['policies_file'] != '':
        ps['inline_policies'] = load_policies(os.path.join(dirname,ps['policies_file']))

    elif ps['policies_file'] == '':
        ps['inline_policies'] = []

for ps in props_root['permissions_set']:
    ps['session_duration'] = isodate.duration_isoformat(isodate.Duration(hours=int(ps['session_duration'])))
    if  ps['policies_file'] != '':
        ps['inline_policies'] = load_policies(os.path.join(dirname,ps['policies_file']))

    elif ps['policies_file'] == '':
        ps['inline_policies'] = []


# load tags
tags = (load_yamls(os.path.join(dirname, "./environment_options/environment_options_master.yaml")))[1]['tags']

