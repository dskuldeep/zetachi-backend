import string
import random
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models import DocumentModel
import json
import time

async def generate_unique_id(db: AsyncSession) -> str:
    while True:
        unique_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        result = await db.execute(select(DocumentModel).filter(DocumentModel.id == unique_id))
        if result.scalar_one_or_none() is None:
            return str(unique_id)
        

def generate_sample_document(id):
    sample_document = {
        "id": id,
        "title": "Untitled",
        "content": {
            "time": int(time.time() * 1000),
            "blocks": [
                {
                    "type": "header",
                    "data": {
                        "level": 1,
                        "text": "Untitled"
                    }
                },
                {
                    "type": "paragraph",
                    "data": {
                        "text": "This is a paragraph in the sample document. You can include various types of content here."
                    }
                },
                {
                    "type": "list",
                    "data": {
                        "style": "unordered",
                        "items": [
                            "First item",
                            "Second item",
                            "Third item"
                        ]
                    }
                }
            ],
            "version": "0.0.1"
        }
    }
    return json.dumps(sample_document, indent=2)