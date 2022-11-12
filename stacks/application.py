from aws_cdk import (
    Stack,
    aws_elasticloadbalancingv2 as elbv2,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecr as ecr,
)
from constructs import Construct


class ApplicationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECR
        ecr_repository = ecr.Repository.from_repository_name(
            self,
            'Repository',
            repository_name='app-repository',
        )

        # ECS
        cluster = ecs.Cluster(self, "EcsCluster", vpc=vpc)

        task_definition = ecs.FargateTaskDefinition(self, "TaskDef")

        container_app = task_definition.add_container(
            "app",
            image=ecs.ContainerImage.from_ecr_repository(ecr_repository),
            logging=ecs.LogDriver.aws_logs(stream_prefix='app')
        )
        container_app.add_port_mappings(
            ecs.PortMapping(
                container_port=80,
                protocol=ecs.Protocol.TCP,
            )
        )

        self.service = ecs.FargateService(
            self, "FargateService",
            cluster=cluster,
            task_definition=task_definition,
            deployment_controller={
                "type": ecs.DeploymentControllerType.CODE_DEPLOY
            }
        )

        # Load Balancer
        alb = elbv2.ApplicationLoadBalancer(
            self, "Alb",
            vpc=vpc,
            internet_facing=True,
        )

        self.listener = alb.add_listener(
            "Listener",
            port=80,
            open=True,
        )

        self.target = self.listener.add_targets(
            "ApplicationFleets",
            port=80,
            targets=[self.service]
        )

        self.test_listener = alb.add_listener(
            "TestListener",
            port=8080,
            open=True,
        )

        self.test_target = self.test_listener.add_targets(
            "TestApplicationFleets",
            port=80,
            targets=[self.service]
        )
