import json
import os

import boto3
import yaml
from aws_cdk import Tags

dirname = os.path.dirname(__file__)
# Set tags Function
def set_tags(stack, tags):
    """
    Args:
        stack -- stack object for assigning tags
        tags -- array of tags for all resources
    Returns:
        None
    """

    for t in tags:
        Tags.of(stack).add(key=t['key'], value=t['value'])


# Function to load manifests
def load_yamls(path_manifest):
    """
    Args:
       path_manifest -- Path for yaml file

    Returns:
        yamltjson -- json load definitions

    """
    #  Upload manifest file
    with open(path_manifest) as manifest:
        yamltjson = list(yaml.safe_load_all(manifest))
    return yamltjson


# Function for read and load bootstrap commands
def load_policies(file):
    """Load policies json

   Args:
       file -- absolute path for json policies

    Returns:
        policy -- policy list on bootstrap file

    """
    with open(file) as f2:
        policies = json.load(f2)
    # print(commands)
    return policies

