# # # from fastapi import FastAPI, HTTPException, Query
# # # from pydantic import BaseModel
# # # from pymongo import MongoClient
# # # from dotenv import load_dotenv
# # # import os
# # # import requests
# # # import re
# # # from datetime import datetime
# # # from typing import List

# # # load_dotenv()

# # # app = FastAPI(
# # #     title="AI Customer Support Classifier",
# # #     description="Modern English-speaking AI complaint classifier and auto-responder",
# # #     version="2.0.0"
# # # )

# # # # -------------------------------
# # # # Environment variables
# # # # -------------------------------
# # # MONGO_URI = os.getenv("MONGO_URI")
# # # OKEYMETA_TOKEN = os.getenv("OKEYMETA_TOKEN")

# # # if not MONGO_URI or not OKEYMETA_TOKEN:
# # #     raise RuntimeError("Missing MONGO_URI or OKEYMETA_TOKEN in .env")

# # # # -------------------------------
# # # # MongoDB setup
# # # # -------------------------------
# # # client = MongoClient(MONGO_URI)
# # # db = client["complaints_db"]
# # # complaints = db.complaints

# # # # -------------------------------
# # # # OkeyMeta API
# # # # -------------------------------
# # # BASE_URL = "https://api.okeymeta.com.ng/api/ssailm/model/okeyai3.0-vanguard/okeyai"

# # # def ask_okey(prompt: str) -> str:
# # #     url = f"{BASE_URL}?input={requests.utils.quote(prompt)}"
# # #     headers = {"Authorization": f"Bearer {OKEYMETA_TOKEN}"}
# # #     try:
# # #         r = requests.get(url, headers=headers, timeout=60)
# # #         r.raise_for_status()
# # #         data = r.json()
# # #         return (data.get("output") or data.get("response") or "").strip()
# # #     except Exception as e:
# # #         return f"Error contacting AI model: {str(e)}"

# # # # -------------------------------
# # # # Pydantic models
# # # # -------------------------------
# # # class ComplaintIn(BaseModel):
# # #     complaint: str

# # # class ComplaintOut(BaseModel):
# # #     classification: str
# # #     solution: str

# # # class ComplaintList(BaseModel):
# # #     id: str
# # #     complaint: str
# # #     classification: str
# # #     solution: str
# # #     timestamp: datetime

# # # # -------------------------------
# # # # Helper
# # # # -------------------------------
# # # def get_recent_examples() -> str:
# # #     cursor = complaints.aggregate([{"$sample": {"size": 12}}])
# # #     examples = []
# # #     for doc in cursor:
# # #         cat = (doc.get("classification") or doc.get("category") or "general").capitalize()
# # #         text = doc.get("complaint") or doc.get("text") or ""
# # #         if text:
# # #             examples.append(f"{cat}: {text}")
# # #     return "\n".join(examples) if examples else "No previous examples available."

# # # # -------------------------------
# # # # Routes
# # # # -------------------------------
# # # @app.post("/classify", response_model=ComplaintOut)
# # # async def classify_complaint(payload: ComplaintIn):
# # #     if not payload.complaint.strip():
# # #         raise HTTPException(status_code=400, detail="Complaint cannot be empty")

# # #     examples = get_recent_examples()

# # #     prompt = f"""
# # # You are a highly professional and polite English-speaking customer support agent.

# # # Classify the complaint into exactly one of these categories only:
# # # banking | escrow | general | merchant | security

# # # Then provide a short, empathetic, and professional response in clear Standard English.

# # # Recent examples:
# # # {examples}

# # # New complaint:
# # # {payload.complaint}

# # # Reply using this exact format (nothing else):
# # # Classification: banking or escrow or general or merchant or security
# # # Reply: your polite English response here
# # # """

# # #     response = ask_okey(prompt)

# # #     # Extract classification safely
# # #     allowed = {"banking", "escrow", "general", "merchant", "security"}
# # #     cat_match = re.search(r"Classification:\s*([a-zA-Z]+)", response, re.I)
# # #     classification = (cat_match.group(1).lower() if cat_match else "general")
# # #     classification = classification if classification in allowed else "general"

# # #     # Extract reply
# # #     reply = response.split("Reply:", 1)[-1].strip() if "Reply:" in response else response.strip()
# # #     if not reply:
# # #         reply = "Thank you for reaching out. We are looking into your issue and will resolve it as quickly as possible."

# # #     # Save to DB
# # #     complaints.insert_one({
# # #         "complaint": payload.complaint,
# # #         "classification": classification,
# # #         "solution": reply,
# # #         "timestamp": datetime.utcnow()
# # #     })

# # #     return ComplaintOut(classification=classification, solution=reply)


# # # @app.get("/complaints", response_model=List[ComplaintList])
# # # async def list_complaints(limit: int = Query(10, ge=1, le=100)):
# # #     cursor = complaints.find().sort("timestamp", -1).limit(limit)
# # #     result = []
# # #     for doc in cursor:
# # #         result.append({
# # #             "id": str(doc["_id"]),
# # #             "complaint": doc.get("complaint") or doc.get("text") or "",
# # #             "classification": doc.get("classification") or doc.get("category") or "general",
# # #             "solution": doc.get("solution") or "",
# # #             "timestamp": doc["timestamp"]
# # #         })
# # #     return result


# # # @app.get("/stats")
# # # async def get_stats():
# # #     pipeline = [
# # #         {"$group": {"_id": {"$ifNull": ["$classification", "$category"]}, "count": {"$sum": 1}}}
# # #     ]
# # #     stats = {item["_id"] or "unknown": item["count"] for item in complaints.aggregate(pipeline)}
# # #     return stats


# # # @app.get("/health")
# # # def health():
# # #     return {
# # #         "status": "healthy",
# # #         "complaints_in_db": complaints.count_documents({}),
# # #         "model": "OkeyMeta (English mode)",
# # #         "timestamp": datetime.utcnow().isoformat() + "Z"
# # #     }


# # from fastapi import FastAPI, HTTPException, Query
# # from pydantic import BaseModel
# # from pymongo import MongoClient
# # from dotenv import load_dotenv
# # import os
# # import requests
# # import re
# # from datetime import datetime
# # from typing import List, Optional

# # load_dotenv()

# # app = FastAPI(
# #     title="AI Customer Support Classifier",
# #     description="Professional English-speaking AI complaint classifier",
# #     version="2.1.0"
# # )

# # # Environment
# # MONGO_URI = os.getenv("MONGO_URI")
# # OKEYMETA_TOKEN = os.getenv("OKEYMETA_TOKEN")
# # if not MONGO_URI or not OKEYMETA_TOKEN:
# #     raise RuntimeError("Missing MONGO_URI or OKEYMETA_TOKEN")

# # # MongoDB
# # client = MongoClient(MONGO_URI)
# # db = client["complaints_db"]
# # complaints = db.complaints

# # # OkeyMeta API
# # BASE_URL = "https://api.okeymeta.com.ng/api/ssailm/model/okeyai3.0-vanguard/okeyai"

# # def ask_okey(prompt: str) -> str:
# #     url = f"{BASE_URL}?input={requests.utils.quote(prompt)}"
# #     headers = {"Authorization": f"Bearer {OKEYMETA_TOKEN}"}
# #     try:
# #         r = requests.get(url, headers=headers, timeout=60)
# #         r.raise_for_status()
# #         data = r.json()
# #         return (data.get("output") or data.get("response") or "").strip()
# #     except Exception:
# #         return "Sorry, we are experiencing technical difficulties. Please try again later."

# # # Models
# # class ComplaintIn(BaseModel):
# #     complaint: str

# # class ComplaintOut(BaseModel):
# #     classification: str
# #     solution: str

# # class ComplaintList(BaseModel):
# #     id: str
# #     complaint: str
# #     classification: str
# #     solution: str
# #     timestamp: datetime

# # # Helper
# # def get_recent_examples() -> str:
# #     cursor = complaints.aggregate([{"$sample": {"size": 12}}])
# #     examples = []
# #     for doc in cursor:
# #         cat = (doc.get("classification") or doc.get("category") or "general").capitalize()
# #         text = doc.get("complaint") or doc.get("text") or ""
# #         if text:
# #             examples.append(f"{cat}: {text}")
# #     return "\n".join(examples) if examples else "No previous examples."

# # # Routes
# # @app.post("/classify", response_model=ComplaintOut)
# # async def classify_complaint(payload: ComplaintIn):
# #     if not payload.complaint.strip():
# #         raise HTTPException(400, "Complaint cannot be empty")

# #     examples = get_recent_examples()

# #     prompt = f"""
# # You are a professional and polite English-speaking customer support agent.

# # Classify the complaint into exactly one category: banking | escrow | general | merchant | security

# # Then write a short, empathetic reply in clear Standard English.

# # Recent examples:
# # {examples}

# # New complaint:
# # {payload.complaint}

# # Reply in this exact format only:
# # Classification: banking or escrow or general or merchant or security
# # Reply: your polite English response
# # """

# #     response = ask_okey(prompt)

# #     allowed = {"banking", "escrow", "general", "merchant", "security"}
# #     cat_match = re.search(r"Classification:\s*([a-zA-Z]+)", response, re.I)
# #     classification = (cat_match.group(1).lower() if cat_match else "general")
# #     classification = classification if classification in allowed else "general"

# #     reply = response.split("Reply:", 1)[-1].strip() if "Reply:" in response else response.strip()
# #     if not reply:
# #         reply = "Thank you for contacting us. We are reviewing your issue and will resolve it shortly."

# #     complaints.insert_one({
# #         "complaint": payload.complaint,
# #         "classification": classification,
# #         "solution": reply,
# #         "timestamp": datetime.utcnow()
# #     })

# #     return ComplaintOut(classification=classification, solution=reply)


# # # ←←← FIXED ENDPOINT ←←←
# # @app.get("/complaints", response_model=List[ComplaintList])
# # async def list_complaints(limit: int = Query(10, ge=1, le=100)):
# #     cursor = complaints.find().sort("timestamp", -1).limit(limit)
# #     result = []
# #     for doc in cursor:
# #         # Safely get timestamp – fallback to now() if missing (old seeded data)
# #         ts = doc.get("timestamp")
# #         if ts is None:
# #             ts = datetime.utcnow()  # or doc.get("_id").generation_time if you prefer ObjectId time

# #         result.append({
# #             "id": str(doc["_id"]),
# #             "complaint": doc.get("complaint") or doc.get("text") or "",
# #             "classification": doc.get("classification") or doc.get("category") or "general",
# #             "solution": doc.get("solution") or "",
# #             "timestamp": ts
# #         })
# #     return result


# # @app.get("/stats")
# # async def get_stats():
# #     pipeline = [
# #         {"$group": {
# #             "_id": {"$ifNull": ["$classification", "$category"]},
# #             "count": {"$sum": 1}
# #         }}
# #     ]
# #     stats = {item["_id"] or "unknown": item["count"] for item in complaints.aggregate(pipeline)}
# #     return stats


# # @app.get("/health")
# # def health():
# #     return {
# #         "status": "healthy",
# #         "complaints_in_db": complaints.count_documents({}),
# #         "model": "OkeyMeta (English mode)",
# #         "timestamp": datetime.utcnow().isoformat() + "Z"
# #     }


# from fastapi import FastAPI, HTTPException, Query
# from pydantic import BaseModel
# from pymongo import MongoClient
# from dotenv import load_dotenv
# import os
# import requests
# import re
# from datetime import datetime
# from typing import List

# load_dotenv()

# app = FastAPI(
#     title="AI Customer Support Classifier",
#     description="Professional English AI complaint classifier & responder",
#     version="2.2.0"
# )

# # Environment
# MONGO_URI = os.getenv("MONGO_URI")
# OKEYMETA_TOKEN = os.getenv("OKEYMETA_TOKEN")
# if not MONGO_URI or not OKEYMETA_TOKEN:
#     raise RuntimeError("Missing required environment variables")

# # MongoDB
# client = MongoClient(MONGO_URI)
# db = client["complaints_db"]
# complaints = db.complaints

# # OkeyMeta API
# BASE_URL = "https://api.okeymeta.com.ng/api/ssailm/model/okeyai3.0-vanguard/okeyai"

# def ask_okey(prompt: str) -> str:
#     url = f"{BASE_URL}?input={requests.utils.quote(prompt)}"
#     headers = {"Authorization": f"Bearer {OKEYMETA_TOKEN}"}
#     try:
#         r = requests.get(url, headers=headers, timeout=60)
#         r.raise_for_status()
#         data = r.json()
#         return (data.get("output") or data.get("response") or "").strip()
#     except Exception:
#         return "We are currently experiencing technical issues. Please try again shortly."

# # Models
# class ComplaintIn(BaseModel):
#     complaint: str

# class ComplaintOut(BaseModel):
#     classification: str
#     solution: str

# class ComplaintList(BaseModel):
#     id: str
#     complaint: str
#     classification: str
#     solution: str
#     timestamp: datetime

# def get_recent_examples() -> str:
#     cursor = complaints.aggregate([{"$sample": {"size": 12}}])
#     examples = []
#     for doc in cursor:
#         cat = (doc.get("classification") or doc.get("category") or "general").capitalize()
#         text = doc.get("complaint") or doc.get("text") or ""
#         if text:
#             examples.append(f"{cat}: {text}")
#     return "\n".join(examples) if examples else "No previous examples."

# # ====================== ENDPOINTS ======================

# @app.post("/classify", response_model=ComplaintOut)
# async def classify_complaint(payload: ComplaintIn):
#     if not payload.complaint.strip():
#         raise HTTPException(400, "Complaint cannot be empty")

#     examples = get_recent_examples()

#     prompt = f"""
# You are a professional, polite English-speaking customer support agent.

# Classify into exactly one: banking | escrow | general | merchant | security
# Then write a short, clear, empathetic reply in Standard English.

# Recent examples:
# {examples}

# New complaint:
# {payload.complaint}

# Reply using only this format:
# Classification: banking or escrow or general or merchant or security
# Reply: your response here
# """

#     response = ask_okey(prompt)

#     allowed = {"banking", "escrow", "general", "merchant", "security"}
#     cat_match = re.search(r"Classification:\s*([a-zA-Z]+)", response, re.I)
#     classification = (cat_match.group(1).lower() if cat_match else "general")
#     classification = classification if classification in allowed else "general"

#     reply = response.split("Reply:", 1)[-1].strip() if "Reply:" in response else response.strip()
#     if not reply:
#         reply = "Thank you for contacting us. We are looking into your issue and will resolve it as soon as possible."

#     complaints.insert_one({
#         "complaint": payload.complaint,
#         "classification": classification,
#         "solution": reply,
#         "timestamp": datetime.utcnow()
#     })

#     return ComplaintOut(classification=classification, solution=reply)


# # FIXED: Only return complaints that actually have a solution
# @app.get("/complaints", response_model=List[ComplaintList])
# async def list_complaints(limit: int = Query(10, ge=1, le=100)):
#     pipeline = [
#         {"$match": {"solution": {"$exists": True, "$ne": "", "$ne": None}}},  # Only real replies
#         {"$sort": {"timestamp": -1}},
#         {"$limit": limit}
#     ]
    
#     result = []
#     for doc in complaints.aggregate(pipeline):
#         result.append({
#             "id": str(doc["_id"]),
#             "complaint": doc.get("complaint") or "",
#             "classification": doc.get("classification") or "general",
#             "solution": doc.get("solution") or "",
#             "timestamp": doc.get("timestamp") or datetime.utcnow()
#         })
#     return result


# @app.get("/stats")
# async def get_stats():
#     pipeline = [
#         {"$match": {"solution": {"$exists": True}}},  # Only count real classified complaints
#         {"$group": {"_id": "$classification", "count": {"$sum": 1}}}
#     ]
#     stats = {item["_id"] or "unknown": item["count"] for item in complaints.aggregate(pipeline)}
#     return stats


# @app.get("/health")
# def health():
#     total = complaints.count_documents({})
#     with_solution = complaints.count_documents({"solution": {"$exists": True, "$ne": None}})
#     return {
#         "status": "healthy",
#         "total_documents_in_db": total,
#         "complaints_with_solutions": with_solution,
#         "model": "OkeyMeta (English mode)",
#         "timestamp": datetime.utcnow().isoformat() + "Z"
#     }
# @app.get("/metrics")
# async def complaint_metrics():
#     """
#     Detailed analytics & metrics for complaint classifications
#     Perfect for dashboards, monitoring, or business reports
#     """
#     # Only count real processed complaints (with solution)
#     match_stage = {"solution": {"$exists": True, "$ne": None, "$ne": ""}}

#     pipeline = [
#         {"$match": match_stage},
#         {"$group": {
#             "_id": "$classification",
#             "count": {"$sum": 1},
#             "latest": {"$max": "$timestamp"},
#             "oldest": {"$min": "$timestamp"}
#         }},
#         {"$sort": {"count": -1}}
#     ]

#     results = list(complaints.aggregate(pipeline))

#     total_complaints = sum(r["count"] for r in results)
#     categories = {r["_id"] or "unknown": r for r in results}

#     # Today's stats
#     today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
#     today_pipeline = [
#         {"$match": {**match_stage, "timestamp": {"$gte": today_start}}},
#         {"$group": {"_id": "$classification", "count": {"$sum": 1}}}
#     ]
#     today_stats = {item["_id"]: item["count"] for item in complaints.aggregate(today_pipeline)}

#     # Top category
#     top_category = max(results, key=lambda x: x["count"])["_id"] if results else "none"
#     top_count = max((r["count"] for r in results), default=0)

#     metrics = {
#         "summary": {
#             "total_classified_complaints": total_complaints,
#             "unique_categories": len(results),
#             "top_complaint_type": top_category.capitalize(),
#             "top_complaint_count": top_count,
#             "percentage_of_top": round((top_count / total_complaints * 100), 1) if total_complaints > 0 else 0
#         },
#         "today": {
#             "complaints_today": sum(today_stats.values()),
#             "breakdown": {k.capitalize(): v for k, v in today_stats.items()}
#         },
#         "all_time_breakdown": {
#             cat.capitalize() if cat else "Unknown": {
#                 "count": categories[cat]["count"],
#                 "percentage": round((categories[cat]["count"] / total_complaints * 100), 2) if total_complaints > 0 else 0,
#                 "first_seen": categories[cat]["oldest"].strftime("%Y-%m-%d %H:%M UTC") if categories[cat]["oldest"] else None,
#                 "latest": categories[cat]["latest"].strftime("%Y-%m-%d %H:%M UTC")
#             }
#             for cat in categories
#         },
#         "generated_at": datetime.utcnow().isoformat() + "Z"
#     }

#     return metrics

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import requests
import re
from datetime import datetime
from typing import List

# Load environment variables (Render injects them automatically, .env only for local dev)
load_dotenv()

app = FastAPI(
    title="AI Customer Support Classifier",
    description="Professional English AI complaint classifier & responder",
    version="2.2.0"
)

# ====================== CONFIG ======================
MONGO_URI = os.getenv("MONGO_URI")
OKEYMETA_TOKEN = os.getenv("OKEYMETA_TOKEN")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable is required")
if not OKEYMETA_TOKEN:
    raise RuntimeError("OKEYMETA_TOKEN environment variable is required")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["complaints_db"]
complaints = db.complaints

# OkeyMeta API
BASE_URL = "https://api.okeymeta.com.ng/api/ssailm/model/okeyai3.0-vanguard/okeyai"


def ask_okey(prompt: str) -> str:
    url = f"{BASE_URL}?input={requests.utils.quote(prompt)}"
    headers = {"Authorization": f"Bearer {OKEYMETA_TOKEN}"}
    try:
        r = requests.get(url, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        return (data.get("output") or data.get("response") or "").strip()
    except Exception as e:
        print(f"OkeyMeta error: {e}")
        return "We are currently experiencing technical issues. Please try again shortly."


# ====================== Pydantic Models ======================
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


def get_recent_examples() -> str:
    cursor = complaints.aggregate([{"$sample": {"size": 12}}])
    examples = []
    for doc in cursor:
        cat = (doc.get("classification") or doc.get("category") or "general").capitalize()
        text = doc.get("complaint") or doc.get("text") or ""
        if text.strip():
            examples.append(f"{cat}: {text.strip()}")
    return "\n".join(examples) if examples else "No previous examples available."


# ====================== ROOT & HEALTH ======================
@app.get("/")
def root():
    return {"message": "AI Customer Support Classifier API is running!", "version": "2.2.0"}

@app.get("/health")
def health():
    total = complaints.count_documents({})
    with_solution = complaints.count_documents({"solution": {"$exists": True, "$ne": None, "$ne": ""}})
    return {
        "status": "healthy",
        "total_documents_in_db": total,
        "complaints_with_solutions": with_solution,
        "model": "OkeyMeta okeyai3.0-vanguard (English mode)",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


# ====================== ENDPOINTS ======================
@app.post("/classify", response_model=ComplaintOut)
async def classify_complaint(payload: ComplaintIn):
    if not payload.complaint or not payload.complaint.strip():
        raise HTTPException(status_code=400, detail="Complaint cannot be empty")

    examples = get_recent_examples()

    prompt = f"""
You are a professional, polite, English-speaking customer support agent for a fintech company.

Classify the complaint into exactly ONE of these categories (lowercase, no extra text):
banking | escrow | general | merchant | security

Then write a short, clear, empathetic reply in perfect Standard English.

Recent real examples:
{examples}

New complaint:
{payload.complaint.strip()}

Respond using ONLY this exact format (nothing else):
Classification: banking  (or escrow | general | merchant | security)
Reply: your polite response here
"""

    response = ask_okey(prompt)

    # Extract classification
    allowed = {"banking", "escrow", "general", "merchant", "security"}
    cat_match = re.search(r"Classification:\s*([a-zA-Z]+)", response, re.I)
    classification = (cat_match.group(1).lower() if cat_match else "general")
    classification = classification if classification in allowed else "general"

    # Extract reply
    reply = response.split("Reply:", 1)[-1].strip() if "Reply:" in response else response.strip()
    if not reply:
        reply = "Thank you for reaching out. We're looking into this and will resolve it shortly."

    # Save to MongoDB
    complaints.insert_one({
        "complaint": payload.complaint.strip(),
        "classification": classification,
        "solution": reply,
        "timestamp": datetime.utcnow()
    })

    return ComplaintOut(classification=classification, solution=reply)


@app.get("/complaints", response_model=List[ComplaintList])
async def list_complaints(limit: int = Query(10, ge=1, le=100)):
    pipeline = [
        {"$match": {"solution": {"$exists": True, "$ne": None, "$ne": ""}}},
        {"$sort": {"timestamp": -1}},
        {"$limit": limit}
    ]
    result = []
    for doc in complaints.aggregate(pipeline):
        result.append({
            "id": str(doc["_id"]),
            "complaint": doc.get("complaint", ""),
            "classification": doc.get("classification", "general"),
            "solution": doc.get("solution", ""),
            "timestamp": doc.get("timestamp", datetime.utcnow())
        })
    return result


@app.get("/stats")
async def get_stats():
    pipeline = [
        {"$match": {"solution": {"$exists": True, "$ne": None, "$ne": ""}}},
        {"$group": {"_id": "$classification", "count": {"$sum": 1}}}
    ]
    stats = {item["_id"] or "unknown": item["count"] for item in complaints.aggregate(pipeline)}
    return stats


@app.get("/metrics")
async def complaint_metrics():
    match_stage = {"solution": {"$exists": True, "$ne": None, "$ne": ""}}

    pipeline = [
        {"$match": match_stage},
        {"$group": {
            "_id": "$classification",
            "count": {"$sum": 1},
            "latest": {"$max": "$timestamp"},
            "oldest": {"$min": "$timestamp"}
        }},
        {"$sort": {"count": -1}}
    ]

    results = list(complaints.aggregate(pipeline))
    total_complaints = sum(r["count"] for r in results)
    categories = {r["_id"] or "unknown": r for r in results}

    # Today’s stats
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_pipeline = [
        {"$match": {**match_stage, "timestamp": {"$gte": today_start}}},
        {"$group": {"_id": "$classification", "count": {"$sum": 1}}}
    ]
    today_stats = {item["_id"] or "unknown": item["count"] for item in complaints.aggregate(today_pipeline)}

    top_category = max(results, key=lambda x: x["count"])["_id"] if results else "none"
    top_count = max((r["count"] for r in results), default=0)

    metrics = {
        "summary": {
            "total_classified_complaints": total_complaints,
            "unique_categories": len(results),
            "top_complaint_type": top_category.capitalize(),
            "top_complaint_count": top_count,
            "percentage_of_top": round((top_count / total_complaints * 100), 1) if total_complaints > 0 else 0
        },
        "today": {
            "complaints_today": sum(today_stats.values()),
            "breakdown": {k.capitalize(): v for k, v in today_stats.items()}
        },
        "all_time_breakdown": {
            cat.capitalize(): {
                "count": categories[cat]["count"],
                "percentage": round((categories[cat]["count"] / total_complaints * 100), 2) if total_complaints > 0 else 0,
                "first_seen": categories[cat]["oldest"].strftime("%Y-%m-%d %H:%M UTC"),
                "latest": categories[cat]["latest"].strftime("%Y-%m-%d %H:%M UTC")
            }
            for cat in categories
        },
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }

    return metrics


# ====================== PRODUCTION ENTRYPOINT ======================
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")