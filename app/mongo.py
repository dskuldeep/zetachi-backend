from pymongo import MongoClient
from typing import Dict, Any

CONNECTION_STRING = "mongodb+srv://kuldeep-zetachi:24670290@zetachi.jzugb3e.mongodb.net/?retryWrites=true&w=majority&appName=Zetachi"

client = MongoClient(CONNECTION_STRING)
db = client['Zetachi']

def create_collection(collection_name):
    if collection_name in db.list_collection_names():
        print(f"Collection '{collection_name}' already exists.")
    else:
        db.create_collection(collection_name)
        print(f"Collection '{collection_name}' created.")


def add_json_to_collection(collection_name: str, json_doc: dict):
    collection = db[collection_name]
    if collection.find_one({"id": json_doc["id"]}) is None:
        collection.insert_one(json_doc)
        print(f"Document added to collection {collection_name}")
    else:
        print(f"Document with id {json_doc['id']} already exists in the collection {collection_name}")

def fetch_json_from_collection(collection_name, query=None):
    collection = db[collection_name]
    if query is None:
        query = {}
    documents = collection.find(query)
    return list(documents)

def update_json_in_collection(collection_name: str, json_doc: dict):
    # Get the collection
    collection = db[collection_name]
    
    # Ensure json_doc contains the necessary 'id' field
    document_id = json_doc.get("id")
    if not document_id:
        raise ValueError("Document ID is required for update operations.")
    
    # Perform the update operation
    result = collection.update_one({"id": document_id}, {"$set": json_doc})
    
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
    documents = collection.find({}, {'id':1, 'title':1})
    result = [{'id':doc['id'], 'title':doc['title']} for doc in documents]
    return result

def fetch_doc_by_id(collection_name, doc_id) -> Dict[str, Any]:
    results = fetch_json_from_collection(collection_name=collection_name, query={"id": doc_id})
    results = results[0]
    results.pop('_id')
    print(results)
    return results

def delete_json_from_collection(collection_name: str, doc_id: str):
    collection = db[collection_name]
    result = collection.delete_one({"id": doc_id})
    if result.deleted_count >0:
        Message = f"Document Deleted with id: {doc_id} in collection {collection_name}"
    else:
        Message = "No Document Found to be deleted."
    return Message


# create_collection("Kuldeep-Paul")
# document = {
#   "id": "sample2",
#   "fileName": "Sample",
# }

# add_json_to_collection("Kuldeep-Paul", document)

# results = fetch_json_from_collection("Kuldeep-Paul", query={"id": "sample2"})
# print(results)