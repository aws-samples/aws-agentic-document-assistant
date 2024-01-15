import * as amplify from '@aws-cdk/aws-amplify-alpha';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as codecommit from 'aws-cdk-lib/aws-codecommit';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as iam from 'aws-cdk-lib/aws-iam';
import path = require('path');

export class AmplifyChatuiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // -------------------------------------------------------------------------
    // Load SSM parameter that stores the Lambda function name

    const cognito_user_pool_id_parameter = ssm.StringParameter.valueForStringParameter(
      this, "/AgenticLLMAssistant/cognito_user_pool_id"
    );

    const cognito_user_pool_client_id_parameter = ssm.StringParameter.valueForStringParameter(
      this, "/AgenticLLMAssistant/cognito_user_pool_client_id"
    );

    // SSM parameter holding Rest API URL
    const agent_api_parameter = ssm.StringParameter.valueForStringParameter(
      this, "/AgenticLLMAssistant/agent_api"
    );

    // -------------------------------------------------------------------------

    // create a new repository and initialize it with the chatui nextjs app source code.
    // https://docs.aws.amazon.com/cdk/api/v2/docs/aws-cdk-lib.aws_codecommit-readme.html
    const amplifyChatUICodeCommitRepo = new codecommit.Repository(this, 'NextJsGitRepository', {
      repositoryName: 'nextjs-amplify-chatui',
      description: 'A chatui with nextjs hosted on AWS Amplify.',
      code: codecommit.Code.fromDirectory(path.join(__dirname, '../chat-app'), 'main')
    });

    // from https://docs.aws.amazon.com/cdk/api/v2/docs/aws-amplify-alpha-readme.html
    const amplifyChatUI = new amplify.App(this, 'AmplifyChatUI', {
      autoBranchDeletion: true,
      sourceCodeProvider: new amplify.CodeCommitSourceCodeProvider(
        {repository: amplifyChatUICodeCommitRepo}),
      // enable server side rendering
      platform: amplify.Platform.WEB_COMPUTE,
      // https://docs.aws.amazon.com/amplify/latest/userguide/environment-variables.html#amplify-console-environment-variables
      environmentVariables: {
        // the following custom image is used to support Next.js 14, see links for details:
        // 1. https://aws.amazon.com/blogs/mobile/6-new-aws-amplify-launches-to-make-frontend-development-easier/
        // 2. https://github.com/aws-cloudformation/cloudformation-coverage-roadmap/issues/1299
        '_CUSTOM_IMAGE': 'amplify:al2023',
        'AMPLIFY_USERPOOL_ID': cognito_user_pool_id_parameter,
        'COGNITO_USERPOOL_CLIENT_ID': cognito_user_pool_client_id_parameter,
        'API_ENDPOINT': agent_api_parameter
      }
    });

    amplifyChatUI.addBranch('main', {stage: "PRODUCTION"});

  }
}
