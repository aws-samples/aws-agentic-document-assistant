#!/usr/bin/env node

import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { AssistantBackendStack } from '../lib/assistant-backend-stack';

const app = new cdk.App();

new AssistantBackendStack(app, 'AssistantBackendStack', {
  /* The next line to specialize this stack for the AWS Account
   * and Region that are implied by the current CLI configuration. */
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
  description: 'AWS Agentic documents assistant (uksb-1tupboc44)'
});
