from textwrap import wrap
from pymongo import MongoClient
from typing import Dict, Any, List
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
import os
from dotenv import load_dotenv

CONNECTION_STRING = "mongodb+srv://kuldeep-zetachi:24670290@zetachi.jzugb3e.mongodb.net/?retryWrites=true&w=majority&appName=Zetachi"

client = MongoClient(CONNECTION_STRING)
db = client['Zetachi']

# Initialize SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate and store embeddings in MongoDB with chunking
def generate_and_store_embeddings(collection_name: str, chunk_size: int = 500, query=None):
    collection = db[collection_name]
    if query is None:
        query = {}
    raw_documents = collection.find(query)

    langchain_docs = []
    for doc in raw_documents:
        page_content = str(doc.get("content", "") )
        metadata = {k: v for k, v in doc.items() if k != "content"}
        langchain_docs.append(Document(page_content=page_content, metadata=metadata))

    documents = langchain_docs


    for doc in documents:
        content = doc.page_content
        
        # Skip non-string or empty content
        if not isinstance(content, str) or not content.strip():
            print(f"Skipping document with ID {doc.metadata['_id']} due to invalid content.")
            continue
        
        # Split content into chunks
        content_chunks = wrap(content, chunk_size)
        
        # Generate embeddings for each chunk
        embeddings = [model.encode(chunk).tolist() for chunk in content_chunks]
        
        # Average the embeddings to get a single vector representation
        average_embedding = np.mean(embeddings, axis=0).tolist()
        
        # Update the document with the generated embedding
        collection.update_one({"_id": doc.metadata["_id"]}, {"$set": {"embedding": average_embedding}})
        print(f"Updated document with ID {doc.metadata['_id']} with its embedding.")


# Sample Embedding Run
# generate_and_store_embeddings(collection_name="testuser3@example.com", query={"id": 'BTMjcsQqoz5st8Ms'})

# Vector search using FAISS
import faiss

def vector_search(query: str, collection_name: str, top_k: int = 5):
    collection = db[collection_name]

    # Generate the embedding for the user's query
    query_embedding = model.encode(query)

    # Retrieve all stored embeddings from the collection
    all_embeddings = []
    all_documents = []
    for doc in collection.find({"embedding": {"$exists": True}}):
        all_embeddings.append(doc["embedding"])
        all_documents.append(doc)

    # Convert embeddings to a numpy array
    all_embeddings = np.array(all_embeddings).astype('float32')

    # Use FAISS to perform similarity search
    index = faiss.IndexFlatL2(all_embeddings.shape[1])
    index.add(all_embeddings)
    distances, indices = index.search(np.array([query_embedding]).astype('float32'), top_k)

    # Retrieve the top_k most relevant documents
    relevant_docs = [all_documents[i] for i in indices[0]]

    return relevant_docs

# Generating answers with vector search using LangChain and LLM
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
import os
from dotenv import load_dotenv

def generate_answer_with_vector_search(user_query: str, collection_name: str, top_k: int = 5):
    # Perform vector search to retrieve relevant documents
    relevant_docs = vector_search(user_query, collection_name, top_k)
    
    load_dotenv()
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
    
    ai_model="llama3-8b-8192"
    temperature=0.5
    max_tokens=1024

    # Convert these documents to LangChain's Document format
    langchain_docs = [Document(page_content=str(doc["content"]), metadata={k: v for k, v in doc.items() if k != "content"}) for doc in relevant_docs]

    # Initialize the LLM
    llm = ChatGroq(model=ai_model, temperature=temperature, max_tokens=max_tokens)
    
    # Define a simple QA chain
    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template='''You are Zeta AI, a helpful assistant. Built by Zetachi. Provided the following documents are made available to you.
                    \n\nBased on the provided documents you are to answer the following question. 
                    \n\nIn case the question is not relevant to the Documents mentioned, respond to the user politely and do not mention about the Documents. 
                    \n\nOnly mention about the documents if the User's question is relevant. Do not point out that the question is irrelevant.
                    \n\nDocuments: {context}
                    \n\nBe creative in your answers and answer the question from general knowledge if the context provided is insufficient.
                    \n\nQuestion: {question}
                    \n\nAnswer:''',
    )
    qa_chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt_template)

    # Prepare the context from the documents
    context = " ".join([doc.page_content for doc in langchain_docs])
    
    # Generate the answer using the relevant documents
    response = qa_chain.run({"input_documents": langchain_docs, "question": user_query})

    return response

# Example usage of the function
# output = generate_answer_with_vector_search(user_query="Can you tell me whats written in the document titled sample para?", collection_name="testuser3@example.com")
# print(output)

