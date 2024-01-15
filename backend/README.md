
# Welcome to your CDK TypeScript project

This is a CDK app to setup the backend infrastructure of **aws agentic assistant**, written in TypeScript.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## What gets built

- [x] An AWS Lambda container, with Amazon Bedrock client, to serve as the orchestrator (i.e agent executor).
- [x] An Amazon DynamoDB table to store the ongoing chat history.
- [x] A REST API with Amazon API Gateway to connect the serverless backend to clients.
- [x] An AWS Cognito user pool to authenticate users to the REST API and the frontend app.
- [x] AWS SSM parameters for all the solution configurations.
- [x] [Least-privilege](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege) IAM permissions.
- [x] A VPC with public, private and isolated subnets to ensure the security and efficiency of the solution.
- [x] An Amazon Aurora PostgreSQL database used for both semantic search and SQL querying.
- [x] A security group with configured access to the database, used by Amazon SageMaker Processing Jobs for data ingestion.
- [x] An IAM managed policy to grant SageMaker Jobs the right permissions.

## Useful commands

* `npx cdk deploy`      deploy this stack to your default AWS account/region
* `npx cdk diff`        compare deployed stack with current state
* `npx cdk synth`       emits the synthesized CloudFormation template
* `npx cdk destroy`     destroys the deployed stack.
