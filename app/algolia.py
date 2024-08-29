from algoliasearch.search_client import SearchClient
import os
from pymongo import MongoClient
import dotenv
from bson import ObjectId

# dotenv.load_dotenv()

CONNECTION_STRING = "mongodb+srv://kuldeep-zetachi:24670290@zetachi.jzugb3e.mongodb.net/?retryWrites=true&w=majority&appName=Zetachi"

mongo_client = MongoClient(CONNECTION_STRING)
mongo_db = mongo_client['Zetachi']
ALGOLIA_APP_ID = os.getenv("ALGOLIA_APP_ID")
ALGOLIA_API_KEY = os.getenv("ALGOLIA_API_KEY")

client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)

def get_user_index(user_email: str):
    return client.init_index(user_email)

def sync_document_to_algolia(collection_name, document):
    # Convert ObjectId to string for all fields in the document
    for key, value in document.items():
        if isinstance(value, ObjectId):
            document[key] = str(value)


    # Trim the document to fit within the size limit
    trimmed_document = {
        'objectID': document['id'],
        'title': document.get('title', 'Default Title'), 
        # Add other necessary fields, but avoid large text fields
    }
    # print(trimmed_document)
    
    index = get_user_index(collection_name)
    index.save_object(trimmed_document)  # Sync to Algolia

def delete_document_from_algolia(user_email: str, document_id: str):
    index = get_user_index(user_email)
    index.delete_object(document_id)


def sync_all_documents_to_algolia():
    collections = mongo_db.list_collection_names()
    # print(collections)
    for collection_name in collections:
        collection = mongo_db[collection_name]
        documents = collection.find()
        for doc in documents:
            sync_document_to_algolia(collection_name, doc)  # Sync to Algolia

#function to sync all documents to algolia
# sync_all_documents_to_algolia()
