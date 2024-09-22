#!/usr/bin/env python3
import os

import aws_cdk as cdk
from aws_cdk import Aspects
from cdk_nag import AwsSolutionsChecks, NagSuppressions

from project_configs.helper import set_tags
from project_configs.deployment_configs import tags, env_client_prd_account, props, env_client_devsecops_account, \
    props_root, env_client_prd_root_account
from src.cdkv2_manage_identity_center_pipeline import ManageIAMIdentityCenterPipelineStack



app = cdk.App()

sso_stack_pipe = ManageIAMIdentityCenterPipelineStack(app, "ManageIAMIdentityCenterPipelineStack",
                                                      stack_name="ManageIAMIdentityCenterPipelineStack",
                                                      props=props,
                                                      env_client_prd_account=env_client_prd_account,
                                                      props_root=props_root,
                                                      env_client_root_account=env_client_prd_root_account,
                                                      env=env_client_devsecops_account,
                                                      source_repository= props["source_repository"])


Aspects.of(app).add(AwsSolutionsChecks())
NagSuppressions.add_stack_suppressions(sso_stack_pipe, [
    {"id": "AwsSolutions-IAM4", "reason": "Custom IAM policy is required for this use case"},
    {"id": "AwsSolutions-S1", "reason": "Server access logging is not required for this bucket"},
    {"id": "AwsSolutions-SMG4", "reason":  "Secrets Manager rotation is not required for this use case"},
     {"id": "AwsSolutions-IAM5", "reason": "Custom IAM policy is required for this use case"},
    {"id": "AwsSolutions-KMS5", "reason": "Custom KMS key is required for this use case"},
    {"id": "AwsSolutions-SNS2", "reason": "SNS encryption is not required for this use case"},
    {"id": "AwsSolutions-SNS3", "reason": "SNS encryption is not required for this use case"},
    {"id": "AwsSolutions-L1", "reason": "The non-container Lambda function is not  managed directly"}


])

set_tags(sso_stack_pipe, tags=tags)
app.synth()
