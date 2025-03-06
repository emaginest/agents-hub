#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv
from aws_cdk import App
from stack import AihubApiStack

# Load CDK environment variables from cdk/.env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

app = App()

AihubApiStack(
    app,
    "AihubApiStack",
    env={
        "account": os.environ.get("CDK_DEFAULT_ACCOUNT"),
        "region": os.environ.get("CDK_DEFAULT_REGION", "us-west-2"),
    },
)

app.synth()
