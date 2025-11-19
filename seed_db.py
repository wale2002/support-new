# # seed_db.py — Run locally with: python seed_db.py
# from pymongo import MongoClient
# from dotenv import load_dotenv
# import os

# load_dotenv()

# client = MongoClient(os.getenv("MONGO_URI"))
# db = client.get_default_database()
# collection = db.complaints

# # Clear old data (remove this line if you want to append)
# collection.delete_many({})

# paths = {
#     "data/banking_complaints.txt": "banking",
#     "data/escrow_complaints.txt": "escrow",
#     "data/general_complaints.txt": "general",
#     "data/merchant_complaints.txt": "merchant",
#      "data/security_complaints.txt": "security"

# }

# total = 0
# for filepath, category in paths.items():
#     if not os.path.exists(filepath):
#         print(f"Warning: {filepath} not found — skipping")
#         continue
#     with open(filepath, "r", encoding="utf-8") as f:
#         for line in f:
#             text = line.strip()
#             if text:
#                 collection.insert_one({"text": text, "category": category})
#                 total += 1

# print(f"Success: {total} complaints uploaded to MongoDB!")
# print("You can now delete the 'data/' folder from your repo")


from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import requests
import re
from datetime import datetime
from typing import List

# Load environment variables from .env
load_dotenv()

app = FastAPI(title="AI Support Classifier")

# -------------------------------
# Environment variables
# -------------------------------
MONGO_URI = os.getenv("MONGO_URI")
OKEYMETA_TOKEN = os.getenv("OKEYMETA_TOKEN")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI not found in environment variables")
if not OKEYMETA_TOKEN:
    raise RuntimeError("OKEYMETA_TOKEN not found in environment variables")

# -------------------------------
# MongoDB setup
# -------------------------------
client = MongoClient(MONGO_URI)
db = client["complaints_db"]  # Explicitly specify database name
complaints = db.complaints

# -------------------------------
# OkeyMeta setup
# -------------------------------
BASE_URL = "https://api.okeymeta.com.ng/api/ssailm/model/okeyai3.0-vanguard/okeyai"

def ask_okey(prompt: str) -> str:
    """
    Sends a prompt to OkeyMeta API and returns the response text.
    """
    url = f"{BASE_URL}?input={requests.utils.quote(prompt)}"
    headers = {"Authorization": f"Bearer {OKEYMETA_TOKEN}"}
    r = requests.get(url, headers=headers, timeout=60)
    data = r.json()
    return (data.get("output") or data.get("response") or "").strip()

# -------------------------------
# Pydantic models
# -------------------------------
class ComplaintIn(BaseModel):
    complaint: str

class ComplaintOut(BaseModel):
    classification: str
    solution: str

class ComplaintList(BaseModel):
    id: str
    complaint: str
    classification: str
    solution: str
    timestamp: datetime

# -------------------------------
# Helper functions
# -------------------------------
def get_recent_examples():
    """
    Fetches 12 random complaints from the DB to use as examples in the prompt.
    """
    cursor = complaints.aggregate([{ "$sample": { "size": 12 } }])
    examples = []
    for doc in cursor:
        cat = doc.get("classification", doc.get("category", "general")).capitalize()
        comp = doc.get("complaint", doc.get("text", ""))
        if comp:
            examples.append(f"{cat}: {comp}")
    return "\n".join(examples) if examples else "No examples yet."

# -------------------------------
# Routes
# -------------------------------
@app.post("/classify", response_model=ComplaintOut)
async def classify_complaint(payload: ComplaintIn):
    if not payload.complaint.strip():
        raise HTTPException(400, "Complaint cannot be empty")

    examples = get_recent_examples()

    prompt = f"""
You are an expert Nigerian customer support agent.

Classify the complaint as one of "banking", "escrow", "general", "merchant", or "security" ONLY.
Then give a short, polite, professional reply in Nigerian English.

Recent examples:
{examples}

New complaint:
{payload.complaint}

Respond exactly in this format:
Classification: banking or escrow or general or merchant or security
Reply: your response here
"""

    response = ask_okey(prompt)

    # Extract classification
    allowed_classifications = ["banking", "escrow", "general", "merchant", "security"]
    cat_match = re.search(r"Classification:\s*(\w+)", response, re.I)
    classification = cat_match.group(1).lower() if cat_match else "general"
    if classification not in allowed_classifications:
        classification = "general"

    # Extract reply
    reply = response.split("Reply:", 1)[-1].strip() if "Reply:" in response else response

    # Save to MongoDB
    complaints.insert_one({
        "complaint": payload.complaint,
        "classification": classification,
        "solution": reply,
        "timestamp": datetime.utcnow()
    })

    return ComplaintOut(classification=classification, solution=reply)

@app.get("/complaints", response_model=List[ComplaintList])
async def list_complaints(limit: int = Query(10, ge=1, le=100)):
    """
    List recent complaints, sorted by timestamp descending.
    """
    cursor = complaints.find().sort("timestamp", -1).limit(limit)
    result = []
    for doc in cursor:
        result.append({
            "id": str(doc["_id"]),
            "complaint": doc.get("complaint", doc.get("text", "")),
            "classification": doc.get("classification", doc.get("category", "general")),
            "solution": doc.get("solution", ""),
            "timestamp": doc.get("timestamp", datetime.utcnow())
        })
    return result

@app.get("/stats")
async def get_stats():
    """
    Get complaint counts by classification.
    """
    pipeline = [
        {"$group": {"_id": {"$ifNull": ["$classification", "$category"]}, "count": {"$sum": 1}}}
    ]
    results = list(complaints.aggregate(pipeline))
    stats = {doc["_id"] or "unknown": doc["count"] for doc in results}
    return stats

@app.get("/health")
def health():
    """
    Health check endpoint.
    """
    count = complaints.count_documents({})
    return {"status": "healthy", "complaints_in_db": count, "model": "OkeyMeta"}