from pymongo import MongoClient
from typing import Dict, Any
from .algolia import delete_document_from_algolia, sync_document_to_algolia

CONNECTION_STRING = "mongodb+srv://kuldeep-zetachi:24670290@zetachi.jzugb3e.mongodb.net/?retryWrites=true&w=majority&appName=Zetachi"
client = MongoClient(CONNECTION_STRING)
db = client['Zetachi']

def create_collection(collection_name):
    if collection_name in db.list_collection_names():
        print(f"Collection '{collection_name}' already exists.")
    else:
        db.create_collection(collection_name)
        print(f"Collection '{collection_name}' created.")

def add_json_to_collection(collection_name: str, doc: dict):
    collection = db[collection_name]
    existing_doc = collection.find_one({"id": doc["id"]})
    if existing_doc is None:
        # Set the objectID for Algolia
        collection.insert_one(doc)
        print(f"Document added to collection {collection_name}")
        sync_document_to_algolia(collection_name, doc)  # Sync to Algolia
    else:
        print(f"Document with id {doc['id']} already exists in the collection {collection_name}")

def fetch_json_from_collection(collection_name, query=None):
    collection = db[collection_name]
    if query is None:
        query = {}
    documents = collection.find(query)
    return list(documents)

def update_json_in_collection(collection_name: str, doc: dict):
    # Get the collection
    collection = db[collection_name]
    
    # Ensure doc contains the necessary 'id' field
    document_id = doc.get("id")
    if not document_id:
        raise ValueError("Document ID is required for update operations.")    
    # Perform the update operation
    result = collection.update_one({"id": document_id}, {"$set": doc})
    
    # Check if the update was successful
    if result.matched_count > 0:
        if result.modified_count > 0:
            print(f"Document with id {document_id} updated successfully in collection {collection_name}.")
        else:
            print(f"Document with id {document_id} was found but not modified in collection {collection_name}.")
    else:
        print(f"No document found with id {document_id} in collection {collection_name}.")

def list_all_jsons(collection_name):
    collection = db[collection_name]
    documents = collection.find({}, {'id': 1, 'title': 1})
    result = [{'id': doc['id'], 'title': doc['title']} for doc in documents]
    return result

def fetch_doc_by_id(collection_name, doc_id) -> Dict[str, Any]:
    results = fetch_json_from_collection(collection_name=collection_name, query={"id": doc_id})
    if not results:
        print(f"No document found with id {doc_id} in collection {collection_name}.")
        return {}
    results = results[0]
    results.pop('_id')
    print(results)
    return results

def delete_json_from_collection(collection_name: str, doc_id: str):
    collection = db[collection_name]
    result = collection.delete_one({"id": doc_id})
    if result.deleted_count > 0:
        delete_document_from_algolia(collection_name, doc_id)  # Sync to Algolia
        return f"Document Deleted with id: {doc_id} in collection {collection_name}"
    else:
        return "No Document Found to be deleted."

def update_doc_title(collection_name: str, doc_id: str, new_title: str):
    collection = db[collection_name]
    result = collection.update_one({"id": doc_id}, {"$set": {"title": new_title}})
    # Update the document in Algolia when the title changes
    doc = fetch_doc_by_id(collection_name, doc_id)
    sync_document_to_algolia(collection_name, doc)  # Sync to Algolia

    # Check if the update was successful
    if result.matched_count > 0:
        if result.modified_count > 0:
            print(f"Document with id {doc_id} updated successfully with new title in collection {collection_name}.")
        else:
            print(f"Document with id {doc_id} was found but the title was not modified in collection {collection_name}.")
    else:
        print(f"No document found with id {doc_id} in collection {collection_name}.")
