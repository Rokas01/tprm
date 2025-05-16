#include PyPDF2

import streamlit as st
from openai import OpenAI
from PyPDF2 import PdfReader

# Show title and description.
st.title("📄 AI prototyping")



add_selectbox = st.sidebar.selectbox(
    "Please select use-case",
    ("Document reviewer", "Duplicate checker", 
     "Discount validation", "Assessment support")
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

        reader = PdfReader(uploaded_file)
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

        reader = PdfReader(uploaded_file_contract)
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


elif add_selectbox=="Assessment support":

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    with open("NIS2","r") as f:
        NIS2 = f.read()

    framework = st.selectbox(
    "Please select the standard or framework in scope:",
    ("EU Directive 2022/2555 (NIS2)"),
    )

    framework = NIS2 #overwriting while leaving the textbox in

    topic = st.selectbox(
    "Please select chapter:",
    ("Chapter 4 - CYBERSECURITY RISK-MANAGEMENT MEASURES AND REPORTING OBLIGATIONS", "Chapter 5 - JURISDICTION AND REGISTRATION"),
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
        placeholder="Enter youyr notes here")
    

    if notes and st.button("Process"):

        # Process the uploaded file and question.
        # document = uploaded_file.read().decode()

        messages = [
            {
                "role": "user",
                "content": f"""You are an expert auditor specialising in EU regulations. Auditing a company with the following characteristics:
                Operating in the {Industry} industry, 
                head office located in {HQ_location}, 
                {No_of_sites} manufacturing sites located in: {Locations_of_sites} .
                The directive is only applicable for EU-based entities, however they can rely in services provided from outside the EU.
                I will provide two inputs: 
                1. Text of an EU directive to audit against. 
                2. Notes from the audit. 
                Reply with three points: 
                1. "Summary" - A coherent and easy to ready summary how requirements of each article are implemented. Group by article. Exclude articles with insufficient information to conclude.
                2. "Follow-up questions" - a list of follow-up questions to ask in order to cover all requirements of {topic}. Group all questions by article. 
                3. "Potential findings" - list of potential issues with refernece to the clause from {topic}. Only include findings explicitly mentioned in the notes. When writing findings add exact quote from the requirement, explain why is it a finding and propose questions to ask in order to validate.
                Do not repeat instructions. Only use the text provided. \n---\n
                Input 1 (Directive): \n---\n {NIS2} \n---\n
                Input 2 (Notes):  \n---\n {notes}""",
            }
        ]

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model="o4-mini",
            messages=messages,
            stream=True,
        )

        st.write("Response:")

        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)

else:
    st.write("Not yet implemented")