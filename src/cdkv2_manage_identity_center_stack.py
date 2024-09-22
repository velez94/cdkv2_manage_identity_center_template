from aws_cdk import (
    Stack,
    CfnOutput,
    aws_sso as sso,

)
from constructs import Construct


class ManageIAMIdentityCenterStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, props: list = None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        permission_set = []
        self.permissions_set_id = []

        for p in props['permissions_set']:
            # print("For"+ p['name'] +"Value is" + str(len(p['managed_policies'])))
            if len(p['managed_policies']) == 0:

                ps = sso.CfnPermissionSet(self, p['name'],
                                          instance_arn=props['sso_instance_arn'],
                                          name=p['name'],
                                          description=p['description'],
                                          inline_policy=p['inline_policies'],
                                          session_duration=p['session_duration'],

                                          )


            elif len(p['inline_policies']) > 0 and len(p['managed_policies']) > 0:
                # print(p['managed_policies'])
                ps = sso.CfnPermissionSet(self, p['name'],
                                          instance_arn=props['sso_instance_arn'],
                                          name=p['name'],
                                          inline_policy=p['inline_policies'],
                                          session_duration=p['session_duration'],
                                          description=p['description'],
                                          managed_policies=p['managed_policies'],

                                          )
            elif len(p['inline_policies']) == 0 and len(p['managed_policies']) > 0:
                ps = sso.CfnPermissionSet(self, p['name'],
                                          instance_arn=props['sso_instance_arn'],
                                          name=p['name'],
                                          description=p['description'],
                                          managed_policies=p['managed_policies'],
                                          session_duration=p['session_duration'],

                                          )

            permission_set.append(ps)
            self.permissions_set_id.append(CfnOutput(self, id=f"PermissionSetId-{p['name']}",
                                                     value=ps.node.id,
                                                     description=f"PermissionSetId"))

            # Assign
            for a in p['assing_to']:
                # print(a)
                for t in a["target_ids"]:
                    cfn_assignment = sso.CfnAssignment(self, f"{p['name']}-CfnAssignment-{a['name']}-{t}",
                                                       instance_arn=props['sso_instance_arn'],
                                                       permission_set_arn=ps.attr_permission_set_arn,
                                                       principal_id=a['principal_id'],
                                                       principal_type=a['principal_type'],
                                                       target_id=t,  # a['target_id'],
                                                       target_type=a["target_type"]
                                                       )
