#!/bin/bash

port_number=8501

sudo yum install jq -y
echo "Installing the following pip dependencies"
cat requirements.txt
echo "..."
pip install -q -r requirements.txt

domain_id=$(jq -r ".DomainId" /opt/ml/metadata/resource-metadata.json)
echo
echo "Open the following link in a new tab to see the chatbot ui."
echo "https://${domain_id}.studio.${AWS_REGION}.sagemaker.aws/jupyter/default/proxy/${port_number}/"
echo
echo "Starting streamlit UI.."
streamlit run chatui.py --browser.gatherUsageStats False --browser.serverPort ${port_number}
