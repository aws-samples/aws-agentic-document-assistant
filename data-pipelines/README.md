
We use SageMaker Processing Jobs and SageMaker Pipelines to implement the data pipelines of the solution, which includes:

* A SageMaker Processing job for orchestrating using Amazon Textract to extract data including tables from PDF documents.
* A SageMaker Processing job for Generating the semantic search index from input documents.
