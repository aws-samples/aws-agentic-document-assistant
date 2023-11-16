# Agentic Documents Assistant

The Agentic Documents Assistant is an LLM assistant that provides users with easy access to information and insights stored accross their business documents, through natural conversations and question answering.
It supports answering factual questions by retrieving information directly from documents using semantic search with the popular RAG design pattern.
Additionally, it answers analytical questions by translating user questions into SQL queries and running them against a database of entities extracted from the documents with a batch process.
It is also able to answer complex multi-step questions by combining different tools and data sources using an LLM agent design pattern.

## Key Features

- Semantic search to augment response generation with relevant documents
- Structured metadata extraction and SQL queries for analytical reasoning
- An agent built with the Reason and Act (ReAct) instruction format that determines whether to use search or SQL to answer questions.

## Architecture Overview

The following architecture diagrams depicts the design of the solution.

![Architecture of the agentic AI documents assistant on AWS ](assets/agentic-documents-assistant-on-aws.png)

## Getting Started

Follow the insturctions below to setup the solution on your account.

### Prerequisites

- An AWS account
- Setup CDK:
    - We recommend using a [Cloud9 environment](https://docs.aws.amazon.com/cloud9/latest/user-guide/tutorial-create-environment.html) to install the cdk app.
    - Alternatively, you can install CDK in an other environment with the [documentation instructions](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html#getting_started_prerequisites).

### Installation

To install the solution in your AWS account:

1. Clone this repository.
2. Install the backend [CDK app](https://docs.aws.amazon.com/cdk/v2/guide/home.html), as follows:
    1. Go inside the `backend` folder.
    2. Run `npm install` to install the dependencies.
    3. If you have never used CDK in the current account and region, run [bootstrapping](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html) with `npx cdk bootstrap`.
    4. Run `npx cdk deploy` to deploy the stack.
3. To install the streamlit-ui:
    1. We recommend cloning this repository into a [SageMaker Studio Environment](https://docs.aws.amazon.com/sagemaker/latest/dg/onboard-quick-start.html).
    2. Then, inside the `frontend/streamlit-ui` folder, run `bash run-streamlit-ui.sh`.
    3. Click on the link with the format below to open the demo:
    ```https://{domain_id}.studio.{region}.sagemaker.aws/jupyter/default/proxy/{port_number}/```
4. run the SageMaker Pipeline, defined in the `data-pipelines/run-data-pipelines.ipynb` notebook, to process the input pdf documents and prepare the SQL table and the semantic search index used by the LLM assistant.

### Clean up

To remove the resources of the solution:

1. Remove the backend stack by running `npx cdk destroy`.
2. Remove the SageMaker Studio Domain if you no longer need it.

## Authors

The authors of this asset are:

* Mohamed Ali Jamaoui: Solution designer/Core maintainer.
* Giuseppe Hannen: Extensive contribution to the structured metadata extraction module.
* Laurens ten Cate: Contributed to extending the agent with SQL tool and early streamlit UI deployments.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## References

* [Best practices for working with AWS Lambda functions](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html).
* [Langchain custom LLM agents](https://python.langchain.com/docs/modules/agents/how_to/custom_llm_agent)

## License

This library is licensed under the MIT-0 License. See the LICENSE file.
