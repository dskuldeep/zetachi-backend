from pymongo import MongoClient

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

def update_json_in_collection(collection_name, json_doc):
    collection = db[collection_name]
    result = collection.update_one({"id": json_doc["id"]}, {"$set": json_doc})
    if result.matched_count > 0:
        print(f"Document with id {json_doc['id']} updated in collection {collection_name}")
    else:
        print(f"No document found with id {json_doc['id']} in collection {collection_name}")

def list_all_jsons(collection_name):
    collection = db[collection_name]
    documents = collection.find({}, {'id':1, 'title':1})
    result = [{'id':doc['id'], 'title':doc['title']} for doc in documents]
    return result




# create_collection("Kuldeep-Paul")
# document = {
#   "id": "sample2",
#   "fileName": "Sample",
# }

# add_json_to_collection("Kuldeep-Paul", document)

# results = fetch_json_from_collection("Kuldeep-Paul", query={"id": "sample2"})
# print(results)