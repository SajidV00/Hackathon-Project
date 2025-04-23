import csv
import json
from collections import defaultdict
from langchain.prompts import PromptTemplate
import json
from langchain_anthropic import ChatAnthropic
from langchain.schema import HumanMessage
import os
import time
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from pathlib import Path
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
            obj={}
            for column in ['RC', 'Result_Text']:
                value = row[column].strip()
                if value and column == "RC":
                    json_data = read_json_file(value)
                    if json_data:
                        #print(f"\nContents of {value}.json:")
                        #print(json.dumps(json_data, indent=2))
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
        inputs_text = "\n\n".join([f"Input {i+1}:\n{txt}" for i, txt in enumerate(input_list)])
        prompt = batch_template.format(inputs=inputs_text, output=output)
        batched_prompts.append({
            "prompt": prompt,
            "expected_output": output
        })
    
    return batched_prompts

def build_test_prompt_rag(prompt,testing_json, vectorstore, k=2):
    query_str = json.dumps(testing_json, indent=2)

    # Retrieve k most relevant examples
    similar_docs = vectorstore.similarity_search(query_str, k=k)

    # Extract examples
    context_examples = "\n\n".join(doc.page_content for doc in similar_docs)

    # Create final prompt
    return f"""{context_examples}

Now, based on the above examples, interpret the following input and produce the expected output.{prompt}

Input:
{query_str}
→ Final Output:"""
def RAGImplementation(batched_prompts):
    docs = [
        Document(page_content=batch["prompt"], metadata={"expected_output": batch["expected_output"]})
        for batch in batched_prompts
    ]

    # Use embedding model for similarity search
    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Create vector store
    vectorstore = FAISS.from_documents(docs, embedding_model)
    return vectorstore


def testing(prompt,testing_json,vectorstore):
    prompt = build_test_prompt_rag(prompt,testing_json, vectorstore, k=2)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        api_key = "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"
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0 , anthropic_api_key=api_key)
    # Call Claude
    response = llm.invoke([HumanMessage(content=prompt)])
    return response

vectorStore = None
def updateToDateRAGDB():
    global vectorStore
    if vectorStore is None:
        print("Building vector store...")
        mergingInputJsonWithRC()
        batched_prompts = batchMaking()
        vectorStore = RAGImplementation(batched_prompts)
        print("Vector store ready.")
    else:
        print("Vector store already initialized.")


def testingJsonWithClaude(prompt):
    testing_json=read_json_file("RC-2025-5")
    return testing(prompt,testing_json,vectorStore)

updateToDateRAGDB()
