from aws_cdk import (
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codestarnotifications as codenote,
    CfnOutput,
    aws_ssm as ssm,
    aws_iam as iam,
aws_lambda_event_sources as event_sources,
    Aws
)

from constructs import Construct
from ..manual_approval.manual_approval_teams_integration import LambdaManualApprove

class SnsCodeStarNotifications(Construct):

    def __init__(self, scope: Construct, construct_id: str, repository: codecommit.IRepository = None,
                 pipeline: codepipeline.IPipeline =None,
                 project_name: str = None,
                 emails: list = None,
                 teams_integration: bool = False,
                 not_repo: bool = True,

                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.topic = sns.Topic(self, f"SnsCodeStarNotifications{project_name}",
                               topic_name=f"SnsCodeStarNotifications{project_name}",
                               display_name=f"SnsCodeStarNotifications{project_name}"
                               )
        if emails is not None:
            for email in emails:
                self.topic.add_subscription(subscriptions.EmailSubscription(email))

        topic_policy = sns.TopicPolicy(
            self, "TopicPolicy", topics=[self.topic])

        topic_policy.document.add_statements(iam.PolicyStatement(
            sid="AWSCodeStarNotifications_publish",
            effect=iam.Effect.ALLOW,
            principals=[iam.ServicePrincipal(
                "codestar-notifications.amazonaws.com"), ],
            actions=["sns:Publish"],
            resources=[self.topic.topic_arn],
            conditions={
                "StringEquals": {

                    "aws:SourceAccount": Aws.ACCOUNT_ID
                }
            }
        ))

        CfnOutput(self, "topic", value=self.topic.topic_name)

        self.parameter_sns = ssm.StringParameter(self, f"ParameterStore_sns_SnsCodeStarNotifications{project_name}",
                                                 parameter_name=f"ParameterStore_sns_SnsCodeStarNotifications{project_name}",
                                                 description=f"ParameterStore_sns_SnsCodeStarNotifications{project_name}",
                                                 string_value=self.topic.topic_arn)

        # Teams Integration
        if teams_integration:
            if pipeline is not None:
                pipeline.notify_on_any_manual_approval_state_change("ManualNotificationRequired", enabled=True,
                                                                    target=self.topic)
                pipeline.notify_on_any_stage_state_change("StageChange", enabled=True,
                                                                    target=self.topic)
                self.func_teams=LambdaManualApprove(self,"NotificationsLambda",project_name=project_name)
                self.func_teams.function.add_event_source(source= event_sources.SnsEventSource(self.topic))