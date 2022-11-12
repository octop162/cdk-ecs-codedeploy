from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ecr as ecr,
)

class RepositoryStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ecr.Repository(self, "AppRepository", repository_name='app-repository')
