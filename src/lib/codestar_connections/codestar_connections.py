from aws_cdk import (
    aws_codestarconnections as codestar_connections,
    Stack,
    CfnOutput,
    RemovalPolicy,
    Duration
)
from constructs import Construct


class CodeStarConnectionsStack(Construct):
    def __init__(self, scope: Construct, construct_id: str, props: dict) -> None:
        super().__init__(scope, construct_id)

        # Create a CodeStar Connection
        self.connection = codestar_connections.CfnConnection(
            self,
            "CodeStarConnection",
            connection_name=props["connection_name"],
            provider_type=props["provider_type"]
        )

        # Add a CfnOutput to display the Connection ARN
        CfnOutput(
            self,
            "ConnectionArn",
            value=self.connection.ref,
            description="The ARN of the CodeStar Connection"
        )
