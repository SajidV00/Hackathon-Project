import csv
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Add the *project root* to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.extract_jira_data import extract_jira_data
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()
finalResult = []


def read_json_file(file_name):
    base_dir = Path(__file__).resolve().parent
    file_path = base_dir.parent / "data" / f"{file_name}.json"

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Invalid JSON in: {file_path}")
    return None


def mergingInputJsonWithRC():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, '../RC_Data.csv')
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            obj = {}
            for column in ['RC', 'Result_Text']:
                value = row[column].strip()
                if value and column == "RC":
                    json_data = read_json_file(value)
                    if json_data:
                        # print(f"\nContents of {value}.json:")
                        # print(json.dumps(json_data, indent=2))
                        obj["inputText"] = json_data
                elif column == "Result_Text":
                    obj["expectedOutput"] = row[column]
            finalResult.append(obj)


def batchMaking():
    grouped = defaultdict(list)
    for ex in finalResult:
        grouped[ex["expectedOutput"]].append(ex["inputText"])

    # Prompt template for a batch (few-shot style)
    batch_template = PromptTemplate(
        input_variables=["inputs", "output"],
        template="""You are an expert system that interprets error logs and result summaries to produce human-readable technical explanations.  
    Use the examples below to learn the format.

    {inputs}

    → Final Output:
    {output}
    """
    )

    # Format batches
    batched_prompts = []
    for output, input_list in grouped.items():
        # Format all inputs in this batch
        inputs_text = "\n\n".join([f"Input {i + 1}:\n{txt}" for i, txt in enumerate(input_list)])
        prompt = batch_template.format(inputs=inputs_text, output=output)
        batched_prompts.append({
            "prompt": prompt,
            "expected_output": output
        })

    return batched_prompts


def build_test_prompt_rag(prompt, testing_json, vectorstore, k=2):
    query_str = json.dumps(testing_json, indent=2)

    # Retrieve k most relevant examples
    similar_docs = vectorstore.similarity_search(query_str, k=k)

    # Extract examples
    context_examples = "\n\n".join(doc.page_content for doc in similar_docs)

    # Create final prompt
    return f"""{context_examples}

Now, based on the above examples, interpret the following input and produce the expected output. Generate release notes in the established format and write the entire document in a professional, business-oriented tone.{prompt}

Input:
{query_str}
→ Final Output:"""


vectorStore = None

RELEASE_FAISS_PATH = "faiss_release_store"


# Chunking logic
def chunk_release_documents(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=60000, chunk_overlap=6000)
    return splitter.split_documents(docs)


# Save FAISS
def create_and_save_release_faiss(docs, save_path=RELEASE_FAISS_PATH):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(docs, embeddings)
    vectorstore.save_local(save_path)


# Load FAISS
def load_release_vectorstore(path=RELEASE_FAISS_PATH):
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)


def updateToDateRAGDB():
    global vectorStore
    if vectorStore is None:
        print("Loading release vector store...")
        try:
            vectorStore = load_release_vectorstore()
            print("Loaded from disk.")
        except Exception as e:
            print("Could not load from disk. Building fresh...")
            mergingInputJsonWithRC()
            batched_prompts = batchMaking()
            docs = [
                Document(page_content=batch["prompt"], metadata={"expected_output": batch["expected_output"]})
                for batch in batched_prompts
            ]
            # chunked_docs = chunk_release_documents(docs)
            create_and_save_release_faiss(docs)
            vectorStore = load_release_vectorstore()
            print("Vector store built and saved.")
    else:
        print("Vector store already initialized.")


def testing(prompt, testing_json, vectorstore):
    prompt = build_test_prompt_rag(prompt, testing_json, vectorstore, k=2)
    api_key = os.getenv('ANTHROPIC_API_TOKEN')
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0, anthropic_api_key=api_key)
    # Call Claude
    response = llm.invoke([HumanMessage(content=prompt)])
    return response


def testingJsonWithClaude(release_name, prompt):
    updateToDateRAGDB()
    extract_jira_data(release_name)
    testing_json = read_json_file(release_name)
    response = testing(prompt, testing_json, vectorStore)
    save_markdown_to_file(response.content)
    return response


def save_markdown_to_file(markdown_content: str, filename="release.md", folder="data"):
    file_path = Path(folder) / filename
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(markdown_content)
