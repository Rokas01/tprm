from langchain.text_splitter import RecursiveCharacterTextSplitter


def invoke_text_spliter(separators:list=None,chunk_size:int=1000,chunk_overlap:int=200,content:str=None):
    try:
        text_splitter = RecursiveCharacterTextSplitter( 
            separators=separators,
            chunk_size=chunk_size,  # The maximum size of your chunks
            chunk_overlap=chunk_overlap  # The maximum overlap between chunks
        )

        text_chunks = text_splitter.create_documents([content])
        return text_chunks
    except Exception as e:
        print(f"Having following issue in invoke_text_splitter method - {e}")