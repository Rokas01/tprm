#include PyPDF2

import streamlit as st
import PyPDF2
from openai import OpenAI
import os
import pandas as pd

# Show title and description.

st.set_page_config(page_title="AI prototyping", layout="wide")

st.title("📄 AI prototyping")


def openAI_processor(prompt, model_to_use):

    stream = client.chat.completions.create(
        model=model_to_use,
        messages=prompt,
        stream=False,
    )

    choices = stream .choices
    chat_completion = choices[0]
    content = chat_completion.message.content

    return content



add_selectbox = st.sidebar.selectbox(
    "Please select use-case",
    ("Document reviewer", "Duplicate checker", 
     "Discount validation", "DO NOT USE", "NIS2 assessment support", )
)

# Using "with" notation
with st.sidebar:

    # Ask user for their OpenAI API key via `st.text_input`.
    # Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
    # via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
    openai_api_key = st.text_input("API Key", type="password")
    
    # st.image("https://upload.wikimedia.org/wikipedia/commons/1/15/Deloitte_Logo.png")

if not openai_api_key:
    st.info("Please add API key to continue.", icon="🗝️")

elif add_selectbox=="Document reviewer":

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    uploaded_file = st.file_uploader(
        "Upload a document (PDF only!)", type=("pdf")
    )

    # Let the user upload a file via `st.file_uploader`.

    # Ask the user for a question via `st.text_area`.
    question1 = st.text_area(
        "Question 1:",
        placeholder="Enter text here. Question 1 is mandatory",
        disabled=not uploaded_file,
    )
    question2 = st.text_area(
        "Question 2:",
        placeholder="Enter text here. Question 2 is mandatory",
        disabled=not uploaded_file,
    )

    page_number = st.number_input(
        "pages to process", value=None, step=1, placeholder="Type a number..."
    )
    st.write("No of pages to be processed:  ", page_number)

 
    if uploaded_file and question1 and question2 and st.button("Process"):

        # Process the uploaded file and question.
        # document = uploaded_file.read().decode()

        reader = PyPDF2.PdfReader(uploaded_file)
        reader_output = []
        for i in range(page_number):
            page = reader.pages[i]
            reader_output.append(page.extract_text ())

        document = ';'.join(reader_output)

        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {question1, question2}",
            }
        ]
        print("debug: ",question1)

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            stream=True,
        )

        st.write("Response:")

        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)

elif add_selectbox=="Discount validation":

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    uploaded_file_contract = st.file_uploader(
        "Upload a contract/agreement (PDF only!)", type=("pdf")
    )

    uploaded_file_finance = st.file_uploader(
        "Upload applied discounts ( format: {contract ID; vendor; product/service description; amount; discount applied})", type=("csv, txt")
    )

    page_number = st.number_input(
        "Contract pages to process", value=None, step=1, placeholder="Enter a number..."
    )
    st.write("No of pages to be processed:  ", page_number)

 
    if uploaded_file_contract and uploaded_file_finance and page_number and st.button("Process"):

        #Process the uploaded file and question.
        discounts = uploaded_file_finance.read().decode()

        reader = PyPDF2.PdfReader(uploaded_file_contract)
        reader_output = []
        for i in range(page_number):
            page = reader.pages[i]
            reader_output.append(page.extract_text ())

        document = ';'.join(reader_output)

        with open('prompt.txt', 'r') as file:
            prompt = file.read().replace('\n', '')

        messages = [
            {
                "role": "user",
                "content": prompt + f"Contract: {document} \n\n---\n\n Discounts: {discounts} P",
            }
        ]

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model="o3",
            messages=messages,
            stream=True,
        )

        st.write("========Output========")

        # Stream the response to the app using `st.write_stream`.
        st.write(stream)



elif add_selectbox=="NIS2 assessment support":

    selected_model ="o4-mini"

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    framework = st.selectbox(
    "Please select the standard or framework in scope:",
    ("EU Directive 2022/2555 (NIS2)"),
    )


    # Let the user upload a file via `st.file_uploader`.

    Industry = st.text_input(
    "Industry:",
    placeholder="....")

    HQ_location = st.text_input(
    "HQ location:",
    placeholder="Enter country of HQ")
    
    No_of_sites = st.text_input(
    "No of manufacturing sites in scope for this assessment:",
    placeholder="Enter the number of sites within EU")

    Locations_of_sites = st.text_input(
    "Locations of manufacturing sites in-scope for this assessment:",
    placeholder="Enter locations (countries only) of all sites (e.g. Germany, Austria, Italy)")
    

    # Ask the user for a question via `st.text_area`.
    notes = st.text_area(
        "Meeting notes:",
        placeholder="Enter your notes here")
    
    st.write(f" **Important: ** the assessment is only performed agaisnt articles 20, 21, 23 and 24 + applicability against art.3 and art.26.")

    if notes and st.button("Process"):

        regulatory_text_file = "NIS2-full.txt"
        # framework = NIS2 #overwriting while leaving the textbox in

        with open("NIS2-art26.txt","r") as f:
            NIS2 = f.read()


        message0 = [
            {
                "role": "developer",
                "content": f"""You are a legal assistant. I will provide 2 inputs:
                1. Information about the company.
                2. Two articles of the EU directive addressing its applicability.
                Reply with a formal commentary if the directive is applicable for the company. Provide justificaiton. Do not repeat instructions. 
                If the information provided is insufficient to conclude provide a list of follow-up questions.
                Input 1 (Company data): 
                1.1 Operating in the {Industry} industry, 
                1.2 head office located in {HQ_location}, 
                2.3 {No_of_sites} manufacturing sites located in: {Locations_of_sites} .
                Input 2 (articles): \n---\n {NIS2} \n---\n"""
            }
        ]

        OpenAI_reply1 = openAI_processor(message0, selected_model)

        st.write(f" **1. Overview and applicability**")
        st.write(OpenAI_reply1)

        st.write(f" **2. Assessment summary**")

        directory = os.fsencode("NIS2-breakdown")

        part_2_response_article =[]
        part_2_response_AISummary =[]
        part_2_response_AIFindings = []

        for file in os.listdir(directory):
            filename = os.fsdecode(file)

            NIS2 = open(os.path.join("NIS2-breakdown", filename),'r')
            article_title = NIS2.readline()
            article_text = NIS2.read()
            NIS2.close()

            part_2_response_article.append(article_title)

            message1 = [
            {
                "role": "developer",
                "content": f"""You are a cybersecurity audit assistant. I will provide with 2 inputs:
                1. Article form the EU directive to audit against.
                2. Notes from the audit.
                Reply with a coherent and easy to read summary of how requirements of this article are implemented.
                Do not repeat instructions. Do not repeat requirements. Only use the information provided in notes notes relevant for each article.
                \n---\n
                Input 1 (article): \n---\n {article_title} {article_text} \n---\n
                Input 2 (Notes):  \n---\n {notes}""",
            }
            ]

            OpenAI_reply2 = openAI_processor(message1, selected_model)

            part_2_response_AISummary.append(OpenAI_reply2)
            #part_2_response_AISummary.append(article_text)


            message2 = [
            {
                "role": "developer",
                "content": f"""You are a cybersecurity audit assistant. I will provide with 2 inputs:
                1. Article form the EU directive to audit against.
                2. Notes from the audit.
                Reply with a a list of potential findings including citations of requirements. Clearly state if the information provided is insufficient to conclude and propose follow-up questions.
                Do not repeat instructions. Only use the information from notes relevant for each article. Do not provide implementation summary.
                \n---\n
                Input 1 (article): \n---\n {article_title} {article_text} \n---\n
                Input 2 (Notes):  \n---\n {notes}""",
            }
            ]

            OpenAI_reply3 = openAI_processor(message2, selected_model)
            part_2_response_AIFindings.append(OpenAI_reply3)
            #part_2_response_AIFindings.append(article_text)

        part_2_response = pd.DataFrame()
        part_2_response['Summary'] = part_2_response_AISummary
        part_2_response['Potential findings'] = part_2_response_AIFindings
        part_2_response.index = part_2_response_article

        st.dataframe(part_2_response, height=1500, row_height=400)


else:
    st.write("Not yet implemented")