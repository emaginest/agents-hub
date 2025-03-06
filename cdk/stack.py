from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_ec2 as ec2,
    aws_secretsmanager as secretsmanager,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_logs as logs,
    Duration,
    RemovalPolicy,
)
from constructs import Construct
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AihubApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC for Lambda
        vpc = ec2.Vpc(self, "AihubApiVpc", max_azs=2, nat_gateways=1)

        # Get existing secret
        secret = secretsmanager.Secret.from_secret_name_v2(
            self, "AihubSecret", f"{os.getenv('ENVIRONMENT', 'dev')}/aihub"
        )

        # Create Lambda function
        aihub_lambda = lambda_.Function(
            self,
            "AihubApiFunction",
            function_name=f"{os.getenv('ENVIRONMENT', 'dev')}-aihub-api",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="lambda_handler.handler",
            code=lambda_.Code.from_asset("deploy/lambda_deployment.zip"),
            timeout=Duration.seconds(30),
            memory_size=1024,
            tracing=lambda_.Tracing.ACTIVE,
            environment={
                "ENVIRONMENT": secret.secret_value_from_json(
                    "ENVIRONMENT"
                ).unsafe_unwrap(),
                "OPENAI_MODEL": secret.secret_value_from_json(
                    "OPENAI_MODEL"
                ).unsafe_unwrap(),
                "MAX_TOKENS": secret.secret_value_from_json(
                    "MAX_TOKENS"
                ).unsafe_unwrap(),
                "MAX_CONTEXT_DOCUMENTS": secret.secret_value_from_json(
                    "MAX_CONTEXT_DOCUMENTS"
                ).unsafe_unwrap(),
                "POSTGRES_HOST": secret.secret_value_from_json(
                    "POSTGRES_HOST"
                ).unsafe_unwrap(),
                "POSTGRES_PORT": secret.secret_value_from_json(
                    "POSTGRES_PORT"
                ).unsafe_unwrap(),
                "POSTGRES_DB": secret.secret_value_from_json(
                    "POSTGRES_DB"
                ).unsafe_unwrap(),
                "POSTGRES_USER": secret.secret_value_from_json(
                    "POSTGRES_USER"
                ).unsafe_unwrap(),
                "POSTGRES_PASSWORD": secret.secret_value_from_json(
                    "POSTGRES_PASSWORD"
                ).unsafe_unwrap(),
                "OPENAI_API_KEY": secret.secret_value_from_json(
                    "OPENAI_API_KEY"
                ).unsafe_unwrap(),
                "LANGFUSE_HOST": secret.secret_value_from_json(
                    "LANGFUSE_HOST"
                ).unsafe_unwrap(),
                "LANGFUSE_RELEASE": secret.secret_value_from_json(
                    "LANGFUSE_RELEASE"
                ).unsafe_unwrap(),
                "LANGFUSE_DEBUG": secret.secret_value_from_json(
                    "LANGFUSE_DEBUG"
                ).unsafe_unwrap(),
                "LANGFUSE_PUBLIC_KEY": secret.secret_value_from_json(
                    "LANGFUSE_PUBLIC_KEY"
                ).unsafe_unwrap(),
                "LANGFUSE_SECRET_KEY": secret.secret_value_from_json(
                    "LANGFUSE_SECRET_KEY"
                ).unsafe_unwrap(),
            },
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
        )

        # Grant DynamoDB permissions
        aihub_lambda.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:BatchGetItem",
                    "dynamodb:BatchWriteItem",
                    "dynamodb:ConditionCheckItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:DescribeTable",
                    "dynamodb:GetItem",
                    "dynamodb:GetRecords",
                    "dynamodb:GetShardIterator",
                    "dynamodb:PutItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    "dynamodb:UpdateItem",
                    "dynamodb:CreateTable",
                    "dynamodb:DeleteTable",
                    "dynamodb:ListTables",
                ],
                resources=[
                    f"arn:aws:dynamodb:{Stack.of(self).region}:{Stack.of(self).account}:table/{os.getenv('ENVIRONMENT', 'dev')}-*",
                    f"arn:aws:dynamodb:{Stack.of(self).region}:{Stack.of(self).account}:table/{os.getenv('ENVIRONMENT', 'dev')}-*/index/*",
                ],
            )
        )

        # Grant Lambda access to secrets
        secret.grant_read(aihub_lambda)

        # Create API Gateway with environment-specific stage
        api = apigateway.RestApi(
            self,
            "AihubApi",
            rest_api_name=f"{os.getenv('ENVIRONMENT', 'dev')}-aihub-api",
            description="API Gateway for Aihub Lambda function",
            deploy_options=apigateway.StageOptions(
                stage_name=os.getenv("ENVIRONMENT", "dev"),
                throttling_rate_limit=10,
                throttling_burst_limit=20,
            ),
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
            ),
        )

        # Add API Key requirement with environment-specific name
        api_key = api.add_api_key(
            "AihubApiKey",
            api_key_name=f"{os.getenv('ENVIRONMENT', 'dev')}-aihub-api-key",
        )

        # Create usage plan
        plan = api.add_usage_plan(
            "AihubApiUsagePlan",
            name=f"{os.getenv('ENVIRONMENT', 'dev')}-aihub-api-plan",
            throttle=apigateway.ThrottleSettings(rate_limit=10, burst_limit=20),
        )
        plan.add_api_stage(stage=api.deployment_stage)
        plan.add_api_key(api_key)

        # Create API Gateway integrations
        protected_integration = apigateway.LambdaIntegration(
            aihub_lambda,
            proxy=True,
            request_parameters={
                "integration.request.header.X-Api-Key": "method.request.header.x-api-key"
            },
            integration_responses=[
                apigateway.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": "'*'"
                    },
                ),
                apigateway.IntegrationResponse(
                    status_code="403",
                    selection_pattern=".*[Ff]orbidden.*",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": "'*'"
                    },
                ),
                apigateway.IntegrationResponse(
                    status_code="500",
                    selection_pattern=".*",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": "'*'"
                    },
                ),
            ],
        )

        public_integration = apigateway.LambdaIntegration(
            aihub_lambda,
            proxy=True,
            integration_responses=[
                apigateway.IntegrationResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": "'*'"
                    },
                ),
                apigateway.IntegrationResponse(
                    status_code="403",
                    selection_pattern=".*[Ff]orbidden.*",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": "'*'"
                    },
                ),
                apigateway.IntegrationResponse(
                    status_code="500",
                    selection_pattern=".*",
                    response_parameters={
                        "method.response.header.Access-Control-Allow-Origin": "'*'"
                    },
                ),
            ],
        )

        # Add routes
        api_resource = api.root.add_resource("api")
        v1_resource = api_resource.add_resource("v1")

        # Define common method responses
        common_responses = [
            apigateway.MethodResponse(
                status_code="200",
                response_parameters={
                    "method.response.header.Access-Control-Allow-Origin": True,
                },
            ),
            apigateway.MethodResponse(
                status_code="403",
                response_parameters={
                    "method.response.header.Access-Control-Allow-Origin": True,
                },
            ),
            apigateway.MethodResponse(
                status_code="500",
                response_parameters={
                    "method.response.header.Access-Control-Allow-Origin": True,
                },
            ),
        ]

        # RAG endpoints
        rag_resource = v1_resource.add_resource("rag")

        # Query endpoint
        query_resource = rag_resource.add_resource("query")
        query_resource.add_method(
            "POST",
            protected_integration,
            api_key_required=True,
            request_parameters={"method.request.header.x-api-key": True},
            method_responses=common_responses,
        )

        # Ingest endpoint
        ingest_resource = rag_resource.add_resource("ingest")
        ingest_resource.add_method(
            "POST",
            protected_integration,
            api_key_required=True,
            request_parameters={"method.request.header.x-api-key": True},
            method_responses=common_responses,
        )

        # Aria endpoints
        aria_resource = v1_resource.add_resource("aria")
        patient_resource = aria_resource.add_resource("patient")

        # Chat endpoint
        chat_resource = patient_resource.add_resource("chat")
        chat_resource.add_method(
            "POST",
            protected_integration,
            api_key_required=True,
            request_parameters={"method.request.header.x-api-key": True},
            method_responses=common_responses,
        )

        # Reformulate endpoint
        reformulate_resource = patient_resource.add_resource("reformulate")
        reformulate_resource.add_method(
            "POST",
            protected_integration,
            api_key_required=True,
            request_parameters={"method.request.header.x-api-key": True},
            method_responses=common_responses,
        )

        # History endpoint
        history_resource = patient_resource.add_resource("history")
        patient_id_resource = history_resource.add_resource("{patient_id}")
        patient_id_resource.add_method(
            "DELETE",
            protected_integration,
            api_key_required=True,
            request_parameters={"method.request.header.x-api-key": True},
            method_responses=common_responses,
        )

        # Health check endpoint
        health_resource = v1_resource.add_resource("health")
        health_resource.add_method(
            "GET",
            public_integration,
            api_key_required=False,
            method_responses=common_responses,
        )
