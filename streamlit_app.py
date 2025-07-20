#include PyPDF2

import streamlit as st
import PyPDF2
from openai import OpenAI
import os
import pandas as pd
import pptx_generator
import doc_processor

# Show title and description.

st.set_page_config(page_title="AI prototyping", layout="wide")

st.title("📄 AI prototyping")

selected_model ="o4-mini"
#selected_model ="o3-mini"
#selected_model ="o3"

def prepare_download(dict_to_use, include_article=True, presentation_title="NIS2 asessment", template='template-NIS2.pptx'):

    report = pptx_generator.create_presentation_report_findings(presentation_title, "Draft report", dict_to_use, include_requirement_text=include_article, custom_template=template)

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


def add_assessment_checkboxes(streamlit_object):

    streamlit_object.write("Pelase select options:")
    selection_implementation_summary = streamlit_object.checkbox("Implementation summary")
    selection_observations = streamlit_object.checkbox("Observations")
    selection_risks = streamlit_object.checkbox("Risks (Important - observations MUST be selected)")
    selection_applicability = streamlit_object.checkbox("Include requirement text in responses?")
    selection_27002 = streamlit_object.checkbox("Include ISO 27002 guidance when drafting observations?")
    streamlit_object.write("NOTE: the assessment is ONLY perofrmed agaisnt ISO27001 Annex A and (optional) ISO27002")


def add_ISMS_area_selector(stramlit_object):

    object_to_return = stramlit_object.selectbox(
    "Please select area under review:",
    ("Information & Communications Security",
    "Organization of Information Security",
    "Asset Management",
    "Access Control",
    "Supplier Relationships",
    "Information Security Incident Management",
    "Business Continuity Management",
    "Compliance",
    "Cryptography",
    "Human Resource Security",
    "Operations Security",
    "Physical and Environmental Security",
    "System Acquisition, Development and Maintenance"),
    )

    return object_to_return

def add_NIS2_area_selector(stramlit_object):

    object_to_return = stramlit_object.selectbox(
    "Please select area under review:",
    ("1. POLICY ON THE SECURITY OF NETWORK AND INFORMATION SYSTEMS",
        "2. RISK MANAGEMENT POLICY",
        "3. INCIDENT HANDLING",
        "4. BUSINESS CONTINUITY AND CRISIS MANAGEMENT",
        "5. SUPPLY CHAIN SECURITY",
        "6. SECURITY IN NETWORK AND INFORMATION SYSTEMS ACQUISITION, DEVELOPMENT AND MAINTENANCE",
        "7. POLICIES AND PROCEDURES TO ASSESS THE EFFECTIVENESS OF CYBERSECURITY RISK MANAGEMENT MEASURES",
        "9. CRYPTOGRAPHY",
        "10. HUMAN RESOURCES SECURITY",
        "11. ACCESS CONTROL",
        "12. ASSET MANAGEMENT",
        "13. ENVIRONMENTAL AND PHYSICAL SECURITY",
        "Article 23"),
    )

    return object_to_return


def template_uploader():

    return 0



def text_preprocessing():

    directory = os.fsencode("NIS2-breakdown")

    part_2_response_article =[]
    part_2_response_AISummary =[]
    part_2_response_AIFindings = []
    part2_response_AIRisks = []
    pptx_generator_input = []

    return 0

add_selectbox = st.sidebar.selectbox(
    "Please select use-case",
    ("Document reviewer", "Duplicate checker", 
     "Discount validation", "NIS2 assessment support", "ISO27k assessment support", "CRA assessment support", "chat")
)

presentation_template = st.sidebar.file_uploader(
    "Upload report template (pptx or ppt)", accept_multiple_files=False, type=[".pptx", ".ppt"]
)


# Using "with" notation
with st.sidebar:

    # Ask user for their OpenAI API key via `st.text_input`.
    # Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
    # via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
    openai_api_key = st.text_input("API Key", type="password")
    
    # st.image("https://upload.wikimedia.org/wikipedia/commons/1/15/Deloitte_Logo.png")

client = OpenAI(api_key=openai_api_key)

if not openai_api_key:
    st.info("Please add API key to continue.", icon="🗝️")


elif add_selectbox=="Document reviewer":

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


#=================================
#NIS2
#=================================
elif add_selectbox=="NIS2 assessment support":


    st.write("Select areas in-scope or click FULL SCOPE below")
    control_group = add_NIS2_area_selector(st)
    selection_full_scope = st.checkbox("FULL SCOPE")
    
    # Intializing checkboxes
    st.write("Select reporting options:")
    selection_implementation_summary = st.checkbox("Implementation summary")
    selection_observations = st.checkbox("Observations")
    selection_risks = st.checkbox("Risks (Important - observations MUST be selected)")
    selection_applicability = st.checkbox("Include requirement text in responses?")
    st.write("NOTE: the assessment is ONLY performed against ENISA guidelines and article 23")

    # Collecting basic info about the organization
    st.write("Enter basic information about the organization:")
    Industry = st.text_input(
    "Industry:",
    placeholder="....")

    HQ_location = st.text_input(
    "HQ location:",
    placeholder="Enter country of HQ")
    
    No_of_sites = st.text_input(
    "No of sites operating under the same ISMS:",
    placeholder="Enter the number of sites")

    Locations_of_sites = st.text_input(
    "Locations of sites in-scope for this assessment:",
    placeholder="Enter locations (countries only) of all sites (e.g. Germany, Austria, Italy)")
    
    # Initializing default responses
    LLM_reply_applicability = "applicability not requested"
    LLM_reply_summary = "summary not requested"
    LLM_reply_findings = "observations not requested"
    LLM_reply_risks = "risks not requested"

    # Text field to input notes
    notes = st.text_area(
        "Meeting notes:",
        placeholder="Enter your notes here")
    

    if st.button("Process"):

        st.write(f" **Assessment summary**")

        full_NIS2_w_ENISA = doc_processor.read_document_w_categories("NIS2-breakdown", "enisa.txt", delims=["£", "$"], strip_new_line = True,  char_to_strip="")
 

        if selection_full_scope:
            
            selected_category =[]

            for area in full_NIS2_w_ENISA:
                
                selected_category.append([ full_NIS2_w_ENISA[area][0][0], full_NIS2_w_ENISA[area][0][1] ])

        else:
            selected_category = full_NIS2_w_ENISA[control_group]

        part_2_response_article =[]
        part_2_response_AISummary =[]
        part_2_response_AIFindings = []
        part2_response_AIRisks = []
        pptx_generator_input = []


        for file in selected_category:

            article_title = file[0]
            article_text = file[1]

            part_2_response_article.append(article_title)

            if selection_implementation_summary:

                message1 = [
                {
                    "role": "developer",
                    "content": f"""You are a cybersecurity audit assistant perfroming an assessment against requirements of EU directive NIS2. I will provide with 2 inputs:
                    1. Requirements of the ENISA (European Union Agency for Cybersecurity) guidance on how the NIS2 Directive should be implemented.
                    2. Notes from the audit.
                    Reply with a short and formal summary of how the requirement is implemented based on the notes provided.
                    When replying, follow these rules:
                    1. Do not repeat instructions.
                    2. Do not repeat requirements.
                    4. Use only the information provided in the notes, do not include any additional context.
                    5. Maximum 200 words.
                    6. Do not use bullet points, write as a one paragraph.
                    7. If the information provided in the notes does not cover all requirements of the article, make it clear in a section called "Missing information:".
                    \n---\n
                    Input 1 (Requirements): \n---\n {article_title} {article_text} \n---\n
                    Input 2 (Notes):  \n---\n {notes}""",
                }
                ]

                LLM_reply_summary = openAI_processor(message1, selected_model)

            part_2_response_AISummary.append(LLM_reply_summary)

            if selection_observations:

                message2 = [
                {
                    "role": "developer",
                    "content": f"""You are a cybersecurity audit assistant perfroming an assessment against requirements of EU directive NIS2. I will provide with 2 inputs:
                    1. Requirements of the ENISA (European Union Agency for Cybersecurity) guidance on how the NIS2 Directive should be implemented.
                    2. Notes from the audit.
                    Reply with a list of potential findings. Clearly state if the information provided is insufficient to conclude whether there is a finding, and propose follow-up questions.
                    When replying, follow these rules:
                    1. Do not repeat instructions.
                    2. Only use the information from notes relevant to this requirement. Ignore irrelevant notes.
                    3. Do not provide an implementation summary.
                    4. Do not include risks or recommendations, only observations.
                    5. Only include issues that are explicitly mentioned in the notes.
                    6. If the implementation is not mentioned or the information is insufficient in the notes, do not assume it is a finding. Reply with "more information needed to conclude".
                    100 words maximum per finding.
                    \n---\n
                    Input 1 (Requirement): \n---\n {article_title} {article_text} \n---\n
                    Input 2 (Notes):  \n---\n {notes}""",
                }
                ]

                LLM_reply_findings = openAI_processor(message2, selected_model)


            part_2_response_AIFindings.append(LLM_reply_findings)

            if selection_risks:

                message3 = [
                {
                    "role": "developer",
                    "content": f"""You are a cybersecurity audit assistant. I will provide with 2 inputs:
                    1. Requirements of the ENISA (European Union Agency for Cybersecurity) guidance on how the NIS2 Directive should be implemented.
                    2. Audit findings
                    You need to write risk statements for the provided findings. When replying, follow these rules:
                    1. Do not repeat instructions.
                    2. If the finding only references the fact that the information is missing or insufficent reply with "No specific risks - more infortmation needed".
                    2. Only use the information from findings. 
                    3. Do not include follow-up questions or next steps, only write risk statements.
                    4. Reply with 100 words maximum for each risk.
                    5. Apply good practice for writing IT risk statements by explaining why each risk is important.
                    \n---\n
                    Input 1 (requirement): \n---\n {article_title} {article_text} \n---\n
                    Audit findings:  \n---\n {LLM_reply_findings}""",
                }
                ]

                LLM_reply_risks = openAI_processor(message3, selected_model)

            part2_response_AIRisks.append(LLM_reply_risks)

            pptx_temp_storage = [article_title, article_text, LLM_reply_summary, LLM_reply_findings, LLM_reply_risks]
            pptx_generator_input.append(pptx_temp_storage)

        part_2_response = pd.DataFrame()
        part_2_response['Summary'] = part_2_response_AISummary
        part_2_response['Potential findings'] = part_2_response_AIFindings
        part_2_response['Risks'] = part2_response_AIRisks    
        part_2_response.index = part_2_response_article

        st.dataframe(part_2_response, height=1500, row_height=400)

        st.download_button(
            label="Download draft report",
            data=prepare_download(pptx_generator_input, include_article=selection_applicability, presentation_title="NIS2 asessment"),
            file_name="ISMS-generated-draft-report.pptx",
            icon=":material/download:",
            key=2
        )



#=================================
#ISO 27001:2022 assessment support
#=================================
elif add_selectbox=="ISO27k assessment support":

    control_group = add_ISMS_area_selector(st)
    
    # Intializing checkboxes
    st.write("Pelase select options:")
    selection_implementation_summary = st.checkbox("Implementation summary")
    selection_observations = st.checkbox("Observations")
    selection_risks = st.checkbox("Risks (Important - observations MUST be selected)")
    selection_applicability = st.checkbox("Include requirement text in responses?")
    selection_27002 = st.checkbox("Include ISO 27002 guidance when drafting observations?")
    st.write("NOTE: the assessment is ONLY perofrmed agaisnt ISO27001 Annex A and (optional) ISO27002")

    # Collecting basic info about the organization
    st.write("Enter basic information about the organization:")
    Industry = st.text_input(
    "Industry:",
    placeholder="....")

    HQ_location = st.text_input(
    "HQ location:",
    placeholder="Enter country of HQ")
    
    No_of_sites = st.text_input(
    "No of sites operating under the same ISMS:",
    placeholder="Enter the number of sites")

    Locations_of_sites = st.text_input(
    "Locations of sites in-scope for this assessment:",
    placeholder="Enter locations (countries only) of all sites (e.g. Germany, Austria, Italy)")
    
    # Initializing default responses
    LLM_reply_applicability = "applicability not requested"
    LLM_reply_summary = "summary not requested"
    LLM_reply_findings = "observations not requested"
    LLM_reply_risks = "risks not requested"

    # Text field to input notes
    notes = st.text_area(
        "Meeting notes:",
        placeholder="Enter your notes here")
    

    if st.button("Process"):

        st.write(f" **Assessment summary**")

        full_anenx_A = doc_processor.read_document_w_categories("ISO27k", "AnnexA.txt", delims=["£", "@"], strip_new_line = True,  char_to_strip="#")
        guidance = doc_processor.read_document_w_categories("ISO27k", "Guidance.txt", delims=["#"], strip_new_line = True, char_to_strip="@") #new

        selected_category = full_anenx_A[control_group]

        part_2_response_article =[]
        part_2_response_AISummary =[]
        part_2_response_AIFindings = []
        part2_response_AIRisks = []
        pptx_generator_input = []

        for file in selected_category:

            article_title = file[0]
            article_text = file[1]
            guidance_text = guidance[article_title][0][0]

            part_2_response_article.append(article_title)

            if selection_implementation_summary:

                message1 = [
                {
                    "role": "developer",
                    "content": f"""You are a cybersecurity audit assistant. I will provide with 2 inputs:
                    1. ISO 27001:2022 requirement to audit against.
                    2. Notes from the audit.
                    Reply with a short and formal summary of how the requirement is implemented based on the notes provided.
                    When replying, follow these rules:
                    1. Do not repeat instructions.
                    2. Do not repeat requirements.
                    4. Use only the information provided in the notes, do not include any additional context.
                    5. Maximum 200 words.
                    6. Do not use bullet points, write as a one paragraph.
                    7. If the information provided in the notes does not cover all requirements of the article, make it clear in a section called "Missing information:".
                    \n---\n
                    Input 1 (article): \n---\n {article_title} {article_text} \n---\n
                    Input 2 (Notes):  \n---\n {notes}""",
                }
                ]

                LLM_reply_summary = openAI_processor(message1, selected_model)

            part_2_response_AISummary.append(LLM_reply_summary)

            if selection_observations and selection_27002: #with ISO 27002

                message2 = [
                {
                    "role": "developer",
                    "content": f"""You are a cybersecurity audit assistant. I will provide with 3 inputs:
                    1. ISO 27001:2022 requirement to audit against.
                    2. ISO 27002:2022 guidance on how to implement ISO 27001:2022.
                    2. Notes from the audit.
                    Reply with a list of potential findings. Clearly state if the information provided is insufficient to conclude if there is a finding and propose follow-up questions.
                    When replying, follow these rules:
                    1. Do not repeat instructions.
                    2. Only use the information from notes relevant to this requirement. Ignore irrelevant notes.
                    3. Do not provide an implementation summary.
                    4. Do not include risks or recommendations, only observations.
                    5. Only include issues that are explicitly mentioned in the notes.
                    6. If the implementation is not mentioned or the information is insufficient in the notes, do not assume it is a finding. Reply with "more information needed to conclude".
                    100 words maximum per finding.
                    \n---\n
                    Input 1 (Requirement): \n---\n {article_title} {article_text} \n---\n
                    Input 2 (Guidance):  \n---\n {guidance_text} \n---\n
                    Input 3 (Notes):  \n---\n {notes}""",
                }
                ]

                LLM_reply_findings = openAI_processor(message2, selected_model)

            else: #without ISO27002

                message2 = [
                {
                    "role": "developer",
                    "content": f"""You are a cybersecurity audit assistant. I will provide with 2 inputs:
                    1. ISO 27001:2022 requirement to audit against.
                    2. Notes from the audit.
                    Reply with a list of potential findings. Clearly state if the information provided is insufficient to conclude if there is a finding and propose follow-up questions.
                    When replying, follow these rules:
                    1. Do not repeat instructions.
                    2. Only use the information from notes relevant to this requirement. Ignore irrelevant notes.
                    3. Do not provide an implementation summary.
                    4. Do not include risks or recommendations, only observations.
                    5. Only include issues that are explicitly mentioned in the notes.
                    6. If the implementation is not mentioned or the information is insufficient in the notes, do not assume it is a finding. Reply with "more information needed to conclude".
                    100 words maximum per finding.
                    \n---\n
                    Input 1 (Requirement): \n---\n {article_title} {article_text} \n---\n
                    Input 2 (Notes):  \n---\n {notes}""",
                }
                ]

                LLM_reply_findings = openAI_processor(message2, selected_model)

                
            part_2_response_AIFindings.append(LLM_reply_findings)

            if selection_risks:

                message3 = [
                {
                    "role": "developer",
                    "content": f"""You are a cybersecurity audit assistant. I will provide with 2 inputs:
                    1. ISO 27001:2022 requirement to audit against.
                    2. Audit findings
                    You need to write risk statements for the provided findings. When replying, follow these rules:
                    1. Do not repeat instructions.
                    2. If the finding only references the fact that the information is missing or insufficent reply with "No specific risks - more infortmation needed".
                    2. Only use the information from findings. 
                    3. Do not include follow-up questions or next steps, only write risk statements.
                    4. Reply with 100 words maximum for each risk.
                    5. Apply good practice for writing IT risk statements by explaining why each risk is important.
                    \n---\n
                    Input 1 (requirement): \n---\n {article_title} {article_text} \n---\n
                    Audit findings:  \n---\n {LLM_reply_findings}""",
                }
                ]

                LLM_reply_risks = openAI_processor(message3, selected_model)

            part2_response_AIRisks.append(LLM_reply_risks)

            pptx_temp_storage = [article_title, article_text, LLM_reply_summary, LLM_reply_findings, LLM_reply_risks]
            pptx_generator_input.append(pptx_temp_storage)

        part_2_response = pd.DataFrame()
        part_2_response['Summary'] = part_2_response_AISummary
        part_2_response['Potential findings'] = part_2_response_AIFindings
        part_2_response['Risks'] = part2_response_AIRisks    
        part_2_response.index = part_2_response_article

        st.dataframe(part_2_response, height=1500, row_height=400)

        st.download_button(
            label="Download draft report",
            data=prepare_download(pptx_generator_input, include_article=selection_applicability, presentation_title="ISO 27001:2022 annex A asessment"),
            file_name="ISMS-generated-draft-report.pptx",
            icon=":material/download:",
            key=2
        )


#=================================
#CRA assessment support
#=================================
elif add_selectbox=="CRA assessment support":

    control_group = st.selectbox(
    "Please select area under review:",
    ("Article 14",
    "Annex I part II")
    )

    # Intializing checkboxes
    st.write("Pelase select options:")
    selection_implementation_summary = st.checkbox("Implementation summary")
    selection_observations = st.checkbox("Observations")
    selection_risks = st.checkbox("Risks (Important - observations MUST be selected)")
    selection_applicability = st.checkbox("Include requirement text in responses?")

    # Collecting basic info about the organization
    st.write("Enter basic information about the organization:")
    Industry = st.text_input(
    "Industry:",
    placeholder="....")

    HQ_location = st.text_input(
    "HQ location:",
    placeholder="Enter country of HQ")
    
    No_of_sites = st.text_input(
    "No of sites operating under the same ISMS:",
    placeholder="Enter the number of sites")

    Locations_of_sites = st.text_input(
    "Locations of sites in-scope for this assessment:",
    placeholder="Enter locations (countries only) of all sites (e.g. Germany, Austria, Italy)")
    
    # Initializing default responses
    LLM_reply_summary = "summary not requested"
    LLM_reply_findings = "observations not requested"
    LLM_reply_risks = "risks not requested"

    # Text field to input notes
    notes = st.text_area(
        "Meeting notes:",
        placeholder="Enter your notes here")
    

    if st.button("Process"):

        st.write(f" **Assessment summary**")

        full_CPA_text = doc_processor.read_document_w_categories("CRA", "reg-text.txt", delims=["#","£","@"], strip_new_line = True)
   
        selected_category = full_CPA_text[control_group]

        part_2_response_article =[]
        part_2_response_AISummary =[]
        part_2_response_AIFindings = []
        part2_response_AIRisks = []
        pptx_generator_input = []

        for file in selected_category:

            article_title = file[0]
            article_text = file[1]
            guidance_text = file[2]

            part_2_response_article.append(article_title)

            if selection_implementation_summary:

                message1 = [
                {
                    "role": "developer",
                    "content": f"""You are a cybersecurity audit assistant. I will provide with 2 inputs:
                    1. Requirement of the EU regulation 2024/2847 (Cyber Resilience Act) to audit against.
                    2. Audit guidance.
                    3. Notes from the audit.
                    Reply with a short and formal summary of how the requirement is implemented based on the notes provided. If the information is sufficient, incldue how guidance are addressed, else, do not mention the guidance.
                    When replying, follow these rules:
                    1. Do not repeat instructions.
                    2. Do not repeat requirements or guidance.
                    4. Only include the notes relevant for this requirement in the summary. Do not include any additional context. Do not include irrelevant notes.
                    5. Maximum 200 words.
                    6. Do not use bullet points, write as a one paragraph.
                    7. If the information provided in the notes does not cover all requirements of the article, make it clear in a section called "Missing information:".
                    \n---\n
                    Input 1 (article): \n---\n {article_title} {article_text} \n---\n
                    Input 2 (audit guidance): \n---\n {guidance_text} \n---\n
                    Input 3 (Notes):  \n---\n {notes}""",
                }
                ]

                LLM_reply_summary = openAI_processor(message1, selected_model)

            part_2_response_AISummary.append(LLM_reply_summary)

            if selection_observations:

                message2 = [
                {
                    "role": "developer",
                    "content": f"""You are a cybersecurity audit assistant. I will provide with 4 inputs:
                    1. Requirement of the EU regulation 2024/2847 (Cyber Resilience Act) to audit against.
                    2. Audit guidance.
                    3. General information about the company being audited.
                    4. Overview of how this requirement is implemented.
                    You need to review the implementaion overview (input 4) and decide if there is sufficient inforamtion to conclude on how the requirement is implemented.
                    When replying use the following scenarios:
                    1. If the information provided is insufficient to conclude how the requirements are implemented, reply with "more information needed to conclude" and propose follow-up questions.
                    2. If the information provided is sufficient to conclude and the implementation is aligned with the requirements and guidance, reply with "no issues."
                    3. If the information provided is sufficient to conclude, but the implementation is not fully aligned with the requirements or guidance, write a formal issue statement explaining exactly what is missing. Provide the exact citation from the requirement.
                    When replying, follow these rules:
                    1. Do not repeat instructions. 
                    2. Only use the information from notes relevant for this requirement.
                    3. Do not provide implementation summary. 
                    4. Only include issues that are explicitly mentioned in the overview.
                    5. 200 words maximum per finding.
                    \n---\n
                    Input 1 (Requirement): \n---\n {article_title} {article_text} \n---\n
                    Input 2 (audit guidance): \n---\n {guidance_text} \n---\n
                    Input 3 (Information about the company being audited): Operating in {Industry} industry, headquarters in {HQ_location} with {No_of_sites} of remote sites in {Locations_of_sites}  \n---\n
                    Input 4 (Implementation overview):  \n---\n {notes}""",
                }
                ]

                LLM_reply_findings = openAI_processor(message2, selected_model)
                
            part_2_response_AIFindings.append(LLM_reply_findings)

            if selection_risks:

                message3 = [
                {
                    "role": "developer",
                    "content": f"""You are a cybersecurity audit assistant. I will provide findings from the audit against EU regulation 2024/2847 (Cyber Resilience Act) {article_title}
                    You need to write risk statements for the provided findings. When replying, follow these rules:
                    1. Do not repeat instructions.
                    2. If the finding only references the fact that the information is missing or insufficient, reply with "No specific risks - more information needed".
                    2. Only use the information from findings. 
                    3. Do not include follow-up questions or next steps, only write risk statements or "No specific risks - more information needed".
                    4. Reply with 100 words maximum for each risk.
                    5. Apply good practice for writing IT risk statements by explaining why each risk is important and what it can lead to.
                    \n---\n
                    Audit findings:  \n---\n {LLM_reply_findings}""",
                }
                ]

                LLM_reply_risks = openAI_processor(message3, selected_model)

            part2_response_AIRisks.append(LLM_reply_risks)

            pptx_temp_storage = [article_title, article_text, LLM_reply_summary, LLM_reply_findings, LLM_reply_risks]
            pptx_generator_input.append(pptx_temp_storage)

        part_2_response = pd.DataFrame()
        part_2_response['Summary'] = part_2_response_AISummary
        part_2_response['Potential findings'] = part_2_response_AIFindings
        part_2_response['Risks'] = part2_response_AIRisks    
        part_2_response.index = part_2_response_article

        st.dataframe(part_2_response, height=1500, row_height=400)

        st.download_button(
            label="Download draft report",
            data=prepare_download(pptx_generator_input, include_article=selection_applicability, presentation_title="EU regulation 2024/2847 (CRA) asessment"),
            file_name="CRA-generated-draft-report.pptx",
            icon=":material/download:",
            key=2                                                           
        )

#=================================
#CRA assessment support
#=================================
elif add_selectbox=="chat":

    # Set a default model
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = selected_model

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)


    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

else:
    st.write("Not yet implemented")