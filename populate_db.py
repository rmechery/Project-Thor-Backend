from langchain_community.vectorstores import SupabaseVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_community.document_loaders import DirectoryLoader, JSONLoader
from supabase.client import Client, create_client
from langchain_text_splitters import MarkdownTextSplitter
import getpass
import os
from dotenv import load_dotenv
import json

load_dotenv()

if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

#loader = DirectoryLoader('./isoscraper/data2/markdown/', glob="*.md")

def metadata_func(record: dict, metadata: dict) -> dict:
    metadata["name"] = record.get("name")
    metadata["section"] = record.get("section")
    metadata["url"] = record.get("url")
    metadata["content_type"] = record.get("content_type")

    return metadata

loader = JSONLoader(
    file_path='./data/tariff_output_6.json',
    jq_schema=".[]",
    content_key="content",
    text_content=False,
    metadata_func=metadata_func
)

docs = loader.load()
for doc in docs:
    doc.metadata['llm_provider'] = "openai"
    doc.metadata['model'] = "text-embedding-3-small"
    if 'source' in doc.metadata:
        doc.metadata['source'] = doc.metadata['url'] 

markdown_splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = markdown_splitter.split_documents(docs)

docs_json = [
    json.loads(doc.json()) for doc in chunks
]
with open('md_docs_data.json', 'w') as jsonl_file:
    json.dump(docs_json, jsonl_file, indent=4)

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

supabase_client: Client = create_client(supabase_url, supabase_key)
vector_store = SupabaseVectorStore.from_documents(
    chunks,
    embeddings,
    client=supabase_client,
    table_name="documents",
    query_name="match_documents",
)