from constructs import Construct
from aws_cdk import (
    Stage
)

from  ..cdkv2_manage_identity_center_stack  import ManageIAMIdentityCenterStack

class PipelineStageProd(Stage):

    def __init__(self, scope: Construct, id: str,props: list = None,  **kwargs):
        super().__init__(scope, id, **kwargs)

        ManageIAMIdentityCenterStack(self, "SdlfSsoStack", props=props)