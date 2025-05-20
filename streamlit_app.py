#include PyPDF2

import streamlit as st
import PyPDF2
from openai import OpenAI

# Show title and description.
st.title("📄 AI prototyping")



add_selectbox = st.sidebar.selectbox(
    "Please select use-case",
    ("Document reviewer", "Duplicate checker", 
     "Discount validation", "Auditor", "Assessment support", )
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


if add_selectbox=="Auditor":

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    framework = st.selectbox(
    "Please select the standard or framework in scope:",
    ("EU Directive 2022/2555 (NIS2)"),
    )

    topic = st.selectbox(
    "Please select chapter:",
    ("Chapter 4 - CYBERSECURITY RISK-MANAGEMENT MEASURES AND REPORTING OBLIGATIONS", "Chapter 5 - JURISDICTION AND REGISTRATION"),
    )

    if (topic == "Chapter 4 - CYBERSECURITY RISK-MANAGEMENT MEASURES AND REPORTING OBLIGATIONS"):
        regulatory_text_file = "NIS2-ch4"
    else:
        regulatory_text_file = "NIS2-ch5"
    """
    with open(regulatory_text_file,"rb") as f:
        NIS2 = f.read()
    """
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

        assistant = client.beta.assistants.create(
            name="Audit assistant",
            instructions="""You are an expert audit assistant specialising in cybersecurity. Auditing a company with the following characteristics:
                    Operating in the {Industry} industry, 
                    head office located in {HQ_location}, 
                    {No_of_sites} manufacturing sites located in: {Locations_of_sites} .""",
            model="gpt-4o",
            tools=[{"type": "file_search"}],
        )

        # Create a vector store caled "Financial Statements"
        vector_store = client.beta.vector_stores.create(name="Legal text")

        # Ready the files for upload to OpenAI
        file_paths = ["NIS2-ch4.txt", "NIS2-ch5.txt"]
        file_streams = [open(path, "rb") for path in file_paths]

        # Use the upload and poll SDK helper to upload the files, add them to the vector store,
        # and poll the status of the file batch for completion.
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
        )

        # You can print the status and the file counts of the batch to see the result of this operation.
        st.write(file_batch.status)
        st.write(file_batch.file_counts)

        # Process the uploaded file and question.
        # document = uploaded_file.read().decode()

        assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        )

        message_file = client.files.create(
        file=open("NIS2-ch4.txt", "rb"), purpose="assistants"
        )

        thread = client.beta.threads.create()

        message1 = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"""I will provide notes from my audit.
                Reply with a coherent and easy to ready summary how requirements of each article are implemented. Group by article. Do not include articles with insufficient information to conclude. Do not include articles with no information provided. 
                Do not repeat instructions. \n---\n
                Notes:  \n---\n {notes}""",
            attachments= [{ "file_id": message_file.id, "tools": [{"type": "file_search"}] }]
        )

        message2 = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"""I will provide notes from my audit.
                Reply with a list of follow-up questions to ask in order to cover all requirements of {topic}. Group all questions by article. 
                Do not repeat instructions. \n---\n
                Notes:  \n---\n {notes}""",
            attachments= [{ "file_id": message_file.id, "tools": [{"type": "file_search"}] }]
        )

        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Please address the user as Jane Doe. The user has a premium account."
        )

        if run.status == 'completed': 
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            st.write(messages)
        else:
            st.write(run.status)




elif add_selectbox=="Assessment support":


    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    framework = st.selectbox(
    "Please select the standard or framework in scope:",
    ("EU Directive 2022/2555 (NIS2)"),
    )

    topic = st.selectbox(
    "Please select chapter:",
    ("Chapter 4 - CYBERSECURITY RISK-MANAGEMENT MEASURES AND REPORTING OBLIGATIONS", "Chapter 5 - JURISDICTION AND REGISTRATION"),
    )

    if (topic == "Chapter 4 - CYBERSECURITY RISK-MANAGEMENT MEASURES AND REPORTING OBLIGATIONS"):
        regulatory_text_file = "NIS2-ch4"
    else:
        regulatory_text_file = "NIS2-ch5"


    # framework = NIS2 #overwriting while leaving the textbox in

    with open(regulatory_text_file,"r") as f:
        NIS2 = f.read()

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
                "1. Summary" - A coherent and easy to ready summary how requirements of each article are implemented. Group by article. Do not include articles with insufficient information to conclude. Do not include articles with no information provided. 
                "2. Follow-up questions" - a list of follow-up questions to ask in order to cover all requirements of {topic}. Group all questions by article. 
                "3. Potential findings" - list of potential issues with refernece to the clause from {topic}. Only include findings explicitly mentioned in the notes. When writing findings add exact quote from the requirement, explain why is it a finding and propose questions to ask in order to validate.
                Do not repeat instructions. Only use the text provided. \n---\n
                Input 1 (Directive): \n---\n {NIS2} \n---\n
                Input 2 (Notes):  \n---\n {notes}""",
            }
        ]

        # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model="o3",
            messages=messages,
            stream=True,
        )

        st.write("Response:")

        # Stream the response to the app using `st.write_stream`.
        st.write_stream(stream)

else:
    st.write("Not yet implemented")