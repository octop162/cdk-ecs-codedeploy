#!/usr/bin/env python3

import subprocess

import aws_cdk as cdk
from stacks.application import ApplicationStack
from stacks.network import NetworkStack
from stacks.repository import RepositoryStack
from stacks.deployment import DeploymentStack

app = cdk.App()

# zip
subprocess.run(
    "zip -j assets/deploy-out.zip assets/deploy/*",
    shell=True,
)

network_stack = NetworkStack(app, 'network-stack')
repository_stack = RepositoryStack(app, 'repository-stack')
application_stack = ApplicationStack(app, 'application-stack', vpc=network_stack.vpc)
deployment_stack = DeploymentStack(
    app, 
    'deployment-stack',
    service=application_stack.service,
    blue_target_group=application_stack.target,
    green_target_group=application_stack.test_target,
    main_listener=application_stack.listener,
    test_listener=application_stack.test_listener,
)

app.synth()



