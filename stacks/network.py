from constructs import Construct
from aws_cdk import (
    CfnOutput,
    Tags,
    Stack,
    aws_ec2 as ec2
)

class NetworkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.Vpc(self, "Vpc",
                    ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
                    nat_gateways=1,
                    max_azs=2,
                    subnet_configuration=[
                        ec2.SubnetConfiguration(
                            subnet_type=ec2.SubnetType.PUBLIC,
                            name="PublicSubnet", 
                            cidr_mask=24,
                        ),
                        ec2.SubnetConfiguration(
                            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                            name="PrivateSubnet", 
                            cidr_mask=24,
                        ),
                    ],
                    
        )