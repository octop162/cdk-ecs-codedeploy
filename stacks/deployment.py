from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    aws_codedeploy as codedeploy,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_ecr as ecr,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_iam as iam,
)


class DeploymentStack(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            service: ecs.FargateService,
            blue_target_group: elbv2.ApplicationTargetGroup,
            green_target_group: elbv2.ApplicationTargetGroup,
            main_listener: elbv2.ApplicationListener,
            test_listener: elbv2.ApplicationListener,
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ecs_application = codedeploy.EcsApplication(self, "CodeDeployApplication",
                                                    application_name="MyApplication"
                                                    )

        # service
        ecs_deployment_group = codedeploy.EcsDeploymentGroup(
            self, "BlueGreenDG",
            application=ecs_application,
            service=service,
            blue_green_deployment_config=codedeploy.EcsBlueGreenDeploymentConfig(
                blue_target_group=blue_target_group,
                green_target_group=green_target_group,
                listener=main_listener,
                test_listener=test_listener,
                deployment_approval_wait_time=Duration.minutes(30),
                termination_wait_time=Duration.minutes(30),
            ),
            deployment_config=codedeploy.EcsDeploymentConfig.ALL_AT_ONCE,
        )

        # pipeline
        pipeline = codepipeline.Pipeline(self, "MyPipeline")

        # source
        ecr_repository = ecr.Repository.from_repository_name(
            self,
            'Repository',
            repository_name='app-repository',
        )
        ecr_output = codepipeline.Artifact()
        ecr_action = codepipeline_actions.EcrSourceAction(
            action_name="ECR",
            repository=ecr_repository,
            image_tag="latest",
            output=ecr_output,
        )
        bucket = s3.Bucket(
            self,
            'Bucket',
            versioned=True,
        )
        s3_deployment.BucketDeployment(
            self, 'S3Deployment',
            sources=[s3_deployment.Source.asset('assets/')],
            destination_bucket=bucket,
        )
        s3_output = codepipeline.Artifact()
        s3_action = codepipeline_actions.S3SourceAction(
            action_name="S3",
            bucket=bucket,
            bucket_key='deploy-out.zip',
            output=s3_output,
        )
        pipeline.add_stage(
            stage_name="Source",
            actions=[ecr_action, s3_action],
        )

        # deploy role
        # deploy_role = iam.Role(self, "DeployRole",
        #     assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com"),
        #     managed_policies=iam.ManagedPolicy.from_aws_managed_policy_name(
        #         "service-role/AWSLambdaBasicExecutionRole"
        #     )
        # )

        # deploy
        code_deploy_ecs_deploy_action = codepipeline_actions.CodeDeployEcsDeployAction(
            action_name="actionName",
            deployment_group=ecs_deployment_group,
            # app_spec_template_input=s3_output,
            app_spec_template_file=s3_output.at_path('appspec.yml'),
            # task_definition_template_input=s3_output,
            task_definition_template_file=s3_output.at_path('taskdef.json'),
            container_image_inputs=[codepipeline_actions.CodeDeployEcsContainerImageInput(
                input=ecr_output,
                task_definition_placeholder="IMAGE1_NAME"
            )],
        )
        pipeline.add_stage(
            stage_name="Deploy",
            actions=[code_deploy_ecs_deploy_action]
        )
