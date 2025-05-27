#include PyPDF2

import streamlit as st
import PyPDF2
from openai import OpenAI
import os
import pandas as pd
import pptx_generator

# Show title and description.

st.set_page_config(page_title="AI prototyping", layout="wide")

st.title("📄 AI prototyping")

def prepare_download(dict_to_use, include_article=True):

    report = pptx_generator.create_presentation_report_findings("NIS2 assessment", "Draft report", dict_to_use, include_requirement_text=include_article)

    return report



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

    st.write("Pelase select options:")
    selection_applibability = st.checkbox("Applicability assessment")
    selection_implementation_summary = st.checkbox("Implementation summary")
    selection_observations = st.checkbox("Observations")
    selection_risks = st.checkbox("Risks (Important - observations MUST be selected)")
    selection_applicability = st.checkbox("Include requirement text in responses")


    if selection_observations == False and selection_risks == True:
        st.warning('Observations MUST be selected!', icon="⚠️")


    # Let the user upload a file via `st.file_uploader`.
    st.write("Enter basic information about the organization:")
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
    

    OpenAI_reply1 = "applicability not requested"
    OpenAI_reply2 = "summary not requested"
    OpenAI_reply3 = "observations not requested"
    OpenAI_reply4 = "risks not requested"

    # Ask the user for a question via `st.text_area`.
    notes = st.text_area(
        "Meeting notes:",
        placeholder="Enter your notes here")
    
    st.write(f" **Important: ** the assessment is only performed against articles 20, 21, 23 and 24 + applicability check against art.3 and art.26.")

    if st.button("Process"):

        regulatory_text_file = "NIS2-full.txt"
        # framework = NIS2 #overwriting while leaving the textbox in

        with open("NIS2-art26.txt","r") as f:
            NIS2 = f.read()


        if selection_applibability:

            message0 = [
                {
                    "role": "developer",
                    "content": f"""You are a legal assistant. I will provide 2 inputs:
                    1. Information about the company.
                    2. Two articles of the EU directive addressing its applicability.
                    Reply with if the directive is applicable for the company. Provide justificaiton. Do not repeat instructions. 
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

        if selection_implementation_summary or selection_observations or selection_risks:

            st.write(f" **2. Assessment summary**")

            directory = os.fsencode("NIS2-breakdown")

            part_2_response_article =[]
            part_2_response_AISummary =[]
            part_2_response_AIFindings = []
            part2_response_AIRisks = []
            pptx_generator_input = []

            for file in os.listdir(directory):
                filename = os.fsdecode(file)

                NIS2 = open(os.path.join("NIS2-breakdown", filename),'r')
                article_title = NIS2.readline().rstrip()
                article_text = NIS2.read()
                NIS2.close()

                part_2_response_article.append(article_title)

                if selection_implementation_summary:

                    message1 = [
                    {
                        "role": "developer",
                        "content": f"""You are a cybersecurity audit assistant. I will provide with 2 inputs:
                        1. Article form the EU directive to audit against.
                        2. Notes from the audit.
                        Reply with a coherent and easy to read summary of how requirements of this article are implemented based on the notes provided.
                        When replying, follow these rules:
                        1. Do not repeat instructions.
                        2. Do not repeat requirements.
                        4. Use only the information provided in the notes, do not include any additional context.
                        5. Maximum 200 words.
                        6. If the information provided in the notes does not cover all requirements of the article, make it clear in a section called "Missing information:".
                        \n---\n
                        Input 1 (article): \n---\n {article_title} {article_text} \n---\n
                        Input 2 (Notes):  \n---\n {notes}""",
                    }
                    ]

                    OpenAI_reply2 = openAI_processor(message1, selected_model)

                    #part_2_response_AISummary.append(OpenAI_reply2)

                part_2_response_AISummary.append(OpenAI_reply2)

                if selection_observations:

                    message2 = [
                    {
                        "role": "developer",
                        "content": f"""You are a cybersecurity audit assistant. I will provide with 2 inputs:
                        1. Article form the EU directive to audit against.
                        2. Notes from the audit.
                        Reply with a list of potential findings including citations of requirements. Clearly state if the information provided is insufficient to conclude and propose follow-up questions.
                        When replying, follow these rules:
                        1. Do not repeat instructions. 
                        2. Only use the information from notes relevant for each article. 
                        3. Do not provide implementation summary. 
                        4. Only include issues that are explicitly mentioned in the notes. 
                        5. If the implementation is not mentioned or inforamtion insufffienct in the notes, do not asume it is a finding, reply with "more information needed to conclude".
                        6. 100 words maximum per finding.
                        \n---\n
                        Input 1 (article): \n---\n {article_title} {article_text} \n---\n
                        Input 2 (Notes):  \n---\n {notes}""",
                    }
                    ]

                    OpenAI_reply3 = openAI_processor(message2, selected_model)

                part_2_response_AIFindings.append(OpenAI_reply3)

                if selection_risks:

                    message3 = [
                    {
                        "role": "developer",
                        "content": f"""You are a cybersecurity audit assistant. I will provide with 2 inputs:
                        1. Article form the EU directive to audit against.
                        2. Audit findings
                        You need to write risk statements for the provided findings. When replying, follow these rules:
                        1. Do not repeat instructions.
                        2. If the finding only references the fact that the information is missing or insufficent reply with "No specific risks - more infortmation needed".
                        2. Only use the information from findings. 
                        3. Do not include follow-up questions or next steps, only write risk statements.
                        4. Reply with 100 words maximum for each risk.
                        5. Apply good practice for writing IT risk statements by explaining why each risk is important.
                        \n---\n
                        Input 1 (article): \n---\n {article_title} {article_text} \n---\n
                        Audit findings:  \n---\n {OpenAI_reply3}""",
                    }
                    ]

                    OpenAI_reply4 = openAI_processor(message3, selected_model)

                part2_response_AIRisks.append(OpenAI_reply4)


                pptx_temp_storage = [article_title, article_text, OpenAI_reply2, OpenAI_reply3, OpenAI_reply4]
                #pptx_temp_storage = [article_title, article_text, OpenAI_reply2, OpenAI_reply3]
                pptx_generator_input.append(pptx_temp_storage)

            part_2_response = pd.DataFrame()
            part_2_response['Summary'] = part_2_response_AISummary
            part_2_response['Potential findings'] = part_2_response_AIFindings
            part_2_response['Risks'] = part2_response_AIRisks    
            part_2_response.index = part_2_response_article


            st.dataframe(part_2_response, height=1500, row_height=400)

            st.download_button(
                label="Download draft report",
                data=prepare_download(pptx_generator_input, include_article=selection_applicability),
                file_name="NIS2-generated-draft-report.pptx",
                icon=":material/download:",
            )

else:
    st.write("Not yet implemented")