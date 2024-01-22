# stage 1: build the lambda layer
FROM --platform=linux/x86_64 public.ecr.aws/lambda/python:3.9 AS builder

# Copy requirements.txt
COPY requirements.txt /tmp/

# Install the specified packages with --no-cache-dir
# to avoid increasing the container size with caching within the container.
RUN  pip install --force-reinstall --no-cache-dir \
    -r /tmp/requirements.txt -t /build/python

# Install 'zip' utility (Amazon Linux uses yum)
RUN yum install -y zip

# Create the ZIP file for the Lambda layer
RUN cd /build/python && zip -r /opt/bedrock_layer.zip .

# Stage 2: Build the Lambda function
FROM --platform=linux/x86_64 public.ecr.aws/lambda/python:3.9

# Copy the Lambda layer artifacts from the builder stage
COPY --from=builder /opt/bedrock_layer.zip /opt/
COPY --from=builder /build/python /opt/python

# Copy function code
ADD agent-executor-lambda ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "handler.lambda_handler" ]
