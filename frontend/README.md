# Welcome to this frontend deployment CDK

This CDK project builds the infrastructure required to setup and deploy the Next.js app inside `chat-app` using AWS Amplify.
Upon deployment you will get a standalone full-featured chat user experience with Amazon Cognito authentication.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

## What gets built

- [x] An AWS CodeCommit repository with a copy of the Next.js app code in `chat-app`.
- [x] An AWS Amplify CI/CD to build, deploy, and host the Next.js.
- [x] Setup with Amazon Cognito user pool from the backend CDK to enable user authentication.
- [x] Connctivity with REST API build with the backend CDK.

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `npx cdk deploy`  deploy this stack to your default AWS account/region
* `npx cdk diff`    compare deployed stack with current state
* `npx cdk synth`   emits the synthesized CloudFormation template

If you are looking for a simple experimentation UI, you can use streamlit as explained in `experiments/streamlit-ui/README.md`.
