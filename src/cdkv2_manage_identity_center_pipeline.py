from aws_cdk import (
    Stack, CfnOutput,
    Environment,
    aws_codecommit as codecommit,
    pipelines,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager,
    aws_s3 as s3,
    SecretValue,
    RemovalPolicy,
    aws_codebuild as codebuild,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codepipeline as codepipeline,
)
from constructs import Construct

from .pipeline.pipeline_stage_prod import PipelineStageProd
from .lib.sns.sns_codestart_notifications import SnsCodeStarNotifications
from .lib.codestar_connections.codestar_connections import CodeStarConnectionsStack


class ManageIAMIdentityCenterPipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, props: dict = None,
                 props_root: dict = None,
                 env_client_prd_account: Environment = None,
                 env_client_root_account: Environment = None,
                 source_repository: str = None,

                 **kwargs) -> None:
        global reports_bucket
        super().__init__(scope, construct_id, **kwargs)
        # Pipeline artifacts
        source_output_impl = codepipeline.Artifact()
        source_actions = []
        in_put = ()
        # Create repository
        if source_repository == "codecommit":
            repository_name = props["repository_properties"].get('repository_name')
            if props["repository_properties"]["create_repository"] == "true":

                repo = codecommit.Repository(
                    self,
                    props["repository_properties"]["repository_name"],
                    repository_name=props["repository_properties"]["repository_name"],
                    description=props["repository_properties"]["description"],

                )
            else:
                repo = codecommit.Repository.from_repository_name(self, "repo", repository_name=repository_name)

            in_put = pipelines.CodePipelineSource.code_commit(repo, "master"),

        elif source_repository == "GitHub":

            # Create the CodeStar Connection using the custom construct
            connection_props = {
                "connection_name": f"Conn-{props['project_name'][0:24]}",
                "provider_type": props["source_repository"],
            }
            con = CodeStarConnectionsStack(self,
                                           construct_id="CodeStarConnection",
                                           props=connection_props)

            repo_config_props = props["github_repository"]

            source_actions.append(codepipeline_actions.CodeStarConnectionsSourceAction(
                action_name="GitHubSource",
                owner=repo_config_props["owner"],
                branch=repo_config_props["source_branch"],
                repo=repo_config_props["repo_name"],
                output=source_output_impl,
                connection_arn=con.connection.attr_connection_arn,
                code_build_clone_output=True

            ))

            in_put = pipelines.CodePipelineSource.connection(
                repo_string=f"{repo_config_props['owner']}/{repo_config_props['repo_name']}",
                branch=repo_config_props["source_branch"],
                connection_arn=con.connection.attr_connection_arn
            )

        secretsmanager.Secret(self, f"webhook_{props['project_name']}_channel",
                              description="WebHook Url for notifications security channel in microsoft teams",
                              secret_name=f"webhook_{props['project_name']}_channel",
                              secret_string_value=SecretValue.unsafe_plain_text(props["webhook_ops_channel"]))

        # Create reports bucket
        if props["create_reports_bucket"] == "True":
            reports_bucket = s3.Bucket(self, f"bucket_{props['reports_bucket']}",
                                       bucket_name=props['reports_bucket'],
                                       encryption=s3.BucketEncryption.S3_MANAGED,
                                       enforce_ssl=True,
                                       block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                                       versioned=True,
                                       removal_policy=RemovalPolicy.DESTROY
                                       )

        synth = pipelines.ShellStep(
            "Synth",

            input=in_put,
            commands=[
                "npm install -g aws-cdk",  # Installs the cdk cli on Codebuild
                "pip install -r requirements.txt",
                # Instructs Codebuild to install required packages
                "npx cdk synth",
            ]
        )

        pipeline = pipelines.CodePipeline(self, f"CDKPipeline-{props['project_name']}",
                                          self_mutation=True,
                                          cross_account_keys=True,
                                          synth=synth,
                                          pipeline_name=props['project_name'],

                                          )
        # Create wave

        deploy_wave = pipeline.add_wave("ParallelDeployment")

        # app_pipeline.app_pipeline.stages
        deploy_delegate = PipelineStageProd(self, "DeployProd", props=props, env=env_client_prd_account)
        # Create stage for root deployment
        deploy_root = PipelineStageProd(self, "DeployProdRoot", props=props_root, env=env_client_root_account)
        # deploy_delegate_stage = pipeline.add_stage(deploy_delegate)

        # Creating statement for run access Analyzer
        access_analyzer = iam.PolicyStatement(actions=["access-analyzer:ValidatePolicy"], effect=iam.Effect.ALLOW,
                                              resources=['*'])
        # Creating statement for artifact repository
        code_artifacts_auth = iam.PolicyStatement(
            actions=[
                "codeartifact:GetAuthorizationToken",
                "codeartifact:GetRepositoryEndpoint",
                "codeartifact:ReadFromRepository"
            ],
            effect=iam.Effect.ALLOW,
            resources=['*']

        )
        code_artifacts_sts = iam.PolicyStatement(
            actions=[
                "sts:GetServiceBearerToken",
            ],
            effect=iam.Effect.ALLOW,
            resources=['*'],

        )
        code_artifacts_read = iam.PolicyStatement(
            actions=[
                "codeartifact:DescribePackageVersion",
                "codeartifact:DescribeRepository",
                "codeartifact:GetPackageVersionReadme",
                "codeartifact:GetRepositoryEndpoint",
                "codeartifact:ListPackageVersionAssets",
                "codeartifact:ListPackageVersionDependencies",
                "codeartifact:ListPackageVersions",
                "codeartifact:ListPackages",
                "codeartifact:ReadFromRepository"
            ],
            effect=iam.Effect.ALLOW,
            resources=['*'],

        )

        s3_read_write = iam.PolicyStatement(
            actions=[
                "s3:GetObject*",
                "s3:GetBucket*",
                "s3:List*",
                "s3:DeleteObject*",
                "s3:PutObject",
                "s3:PutObjectLegalHold",
                "s3:PutObjectRetention",
                "s3:PutObjectTagging",
                "s3:PutObjectVersionTagging",
                "s3:Abort*"
            ],
            effect=iam.Effect.ALLOW,
            resources=[
                reports_bucket.bucket_arn,
                f"{reports_bucket.bucket_arn}/*"
            ],

        )
        # Steps
        validate_policies = pipelines.CodeBuildStep("ValidatePermissionSet",
                                                    role_policy_statements=[access_analyzer,
                                                                            code_artifacts_read,
                                                                            code_artifacts_auth,
                                                                            code_artifacts_sts,
                                                                            s3_read_write
                                                                            ],
                                                    build_environment=codebuild.BuildEnvironment(
                                                        build_image=codebuild.LinuxBuildImage.STANDARD_6_0
                                                    ),
                                                    commands=["ls -all",
                                                              "pip install validate-aws-policies",
                                                              "validate-aws-policies  -d project_configs/policies/ -c  -b $REPORTS_BUCKET -z -u "
                                                              ],
                                                    env={
                                                        "REPORTS_BUCKET": props['reports_bucket'],
                                                    }
                                                    )

        manual_approval = pipelines.ManualApprovalStep("PromoteToProd", comment="Validate policy to approval")
        # Define Dependency
        manual_approval.add_step_dependency(validate_policies)

        deploy_wave.add_pre(validate_policies)

        deploy_wave.add_pre(manual_approval)

        # Extend Wave
        deploy_wave.add_stage(stage=deploy_delegate)
        deploy_wave.add_stage(stage=deploy_root)
        # Create Notifications based on construct
        pipeline.build_pipeline()
        # Create Notifications for code commit

        self.sns_codestart = SnsCodeStarNotifications(self, "SnsCodeStarNotifications",
                                                      emails=[props['security_specialist_email'],
                                                              props['sys_ops_email'],
                                                              props['devsecops_email']],
                                                      project_name=props['project_name'],
                                                      teams_integration=True,
                                                      pipeline=pipeline.pipeline
                                                      )

        CfnOutput(self, "BucketARN", value=reports_bucket.bucket_arn, description="Reports Bucket ARN")
