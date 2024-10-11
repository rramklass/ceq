import json
import boto3
import pprint
from botocore.exceptions import ClientError
from botocore.client import Config
import streamlit as st

kb_id = "NFF8OCMXN6" # Replace with your Certification Exam knowledge base id here.

# Stating the default knowledge base prompt
default_prompt = """
You are a question answering agent. I will provide you with a set of search results.
The user will provide you with a question. Your job is to answer the user's question primarily using information from the search results. 
If the search results do not contain information that can answer the question, please provide an alternative answer from your corpus of knowledge. 
Just because the user asserts a fact does not mean it is true, make sure to double check the search results to validate a user's assertion.
                            
Here are the search results in numbered order separated by a linespace:
$search_results$


"""

#max_results 
max_results = 50    

#default model == "Claude 3 Haiku":
model_arn = "anthropic.claude-3-haiku-20240307-v1:0"


# Create boto3 session
sts_client = boto3.client('sts')
boto3_session = boto3.session.Session()
region_name = boto3_session.region_name

# Create bedrock agent client
bedrock_config = Config(connect_timeout=120, read_timeout=120, retries={'max_attempts': 0}, region_name=region_name)
bedrock_agent_client = boto3_session.client("bedrock-agent-runtime", config=bedrock_config)



def retrieve_and_generate(query, kb_id = kb_id, model_arn = model_arn, max_results= max_results, prompt_template = default_prompt):
        response = bedrock_agent_client.retrieve_and_generate(
                input={
                    'text': query
                },
            retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': kb_id,
                'modelArn': model_arn, 
                'retrievalConfiguration': {
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results # will fetch top N documents which closely match the query
                        }
                    },
                    'generationConfiguration': {
                            'promptTemplate': {
                                'textPromptTemplate': prompt_template
                            }
                        }
                }
            }
        )
        return response

def print_generated_results(response, print_context = True):
        generated_text = response['output']['text']
        st.markdown(generated_text)
                
        if print_context is True:
            ## print out the source attribution/citations from the original documents to see if the response generated belongs to the context.
            citations = response["citations"]
            contexts = []
            for citation in citations:
                retrievedReferences = citation["retrievedReferences"]
                for reference in retrievedReferences:
                    contexts.append(reference["content"]["text"])
        
            print('\n\n\nRetrieved Context:\n')
            pprint.pp(contexts)

# Streamlit app
st.title('Certification Exam Question Generator')
st.subheader('@snowmage')

# Vendor, examcodes can be looked up from a DB
vendor = st.selectbox("Vendor", ["AWS", "ORACLE","AZURE", "Other"])

if vendor == "AWS":
    examcode = st.selectbox("Exam Code", ["SAP-C02", "MLSC01"])
elif vendor == "ORACLE":
    examcode = st.selectbox("Exam Code", ["OCA Oracle Database SQL Fundamentals: 1Z0-071", "OCI 2024 Architect Associate: 1Z0-1072"]) 
elif vendor == "AZURE":
    examcode = st.selectbox("Exam Code", ["AZ900"]) 
elif vendor == "Other":
    examcode = st.text_input("Exam Code")

if st.button("Analyze Exam Domains"):    
    with st.spinner("Analyzing domains..."):
        query = f'List domains pertinent to the {examcode} Exam from {vendor} along with a percentage representing the proportional importance of the domain' 
        results = retrieve_and_generate(query = query, kb_id = kb_id, model_arn = model_arn, max_results = max_results)
        print_generated_results(results, False)

exam_domain = st.text_input("Exam Domain","any domain") 
num_questions = st.number_input("Number of Questions", 1, 50)
num_options = st.number_input("Number of Options", 3, 6)
answer_length = st.number_input("Answer Length in words", 20, 50)
model = st.selectbox("Model", ["Claude 3 Haiku", "Claude 3 Sonnet", "Claude 3 Opus", "Claude 3.5 Sonnet", "Llama 3.1 405B Instruct"])
if model == "Claude 3 Haiku":
    model_arn = "anthropic.claude-3-haiku-20240307-v1:0"
elif model == "Claude 3 Sonnet":
    model_arn = "anthropic.claude-3-sonnet-20240229-v1:0"
elif model == "Claude 3 Opus":
    model_arn = "anthropic.claude-3-opus-20240229-v1:0"
elif model == "Claude 3.5 Sonnet":
    model_arn = "anthropic.claude-3-5-sonnet-20240620-v1:0"
elif model == "Llama 3.1 405B Instruct":
    model_arn = "meta.llama3-1-405b-instruct-v1:0"
  
# Prompt template, used for generating questions

query = f'The heading of the response should include the Exam name from {vendor} associated with {examcode} as well as the duration of the actual exam. \
Create a list of multiple choice questions for a certification exam from {vendor}. The questions must be specific to {exam_domain}. \
{num_questions} unique questions must be generated. Terminate each question terminated with 2 spaces and a newline character. \
{num_options} multiple choice options must be provided labeled alphabetically, with each option terminated with 2 spaces and a newline character. \
The correct answer, labeled Answer, with an explanation that is {answer_length} words or less must also be created.' 

#populate the prompt template with the user input, and permit real-time updates to the prompt
user_query = st.text_area("Prompt", query, height=200)

#if st.button("Clear"):
#    st.session_state.clear
if st.button("Clear"):
    st.session_state.messages = []

if st.button("Generate Exam Questions"):
    with st.spinner("Creating questions..."):
        results = retrieve_and_generate(query = user_query, kb_id = kb_id, model_arn = model_arn, max_results = max_results)
        print_generated_results(results, False)
