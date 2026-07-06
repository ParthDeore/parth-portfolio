"""
Portfolio backend API
----------------------
Handles: contact form storage, blog posts, testimonials, visitor counter.
Database: Supabase (Postgres).

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Deploy: Render.com (same as your RAG project) - see README.md
"""

import os
from datetime import datetime
from typing import Optional, Literal

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
ADMIN_KEY = os.environ["ADMIN_KEY"]

# Comma-separated list of origins allowed to call this API,
# e.g. "https://parthdeore.github.io,http://127.0.0.1:5500"
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

app = FastAPI(title="Parth Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------
# Admin auth: every admin-only route requires this header:
#   X-Admin-Key: <your secret>
# This is intentionally simple (one shared secret, no user accounts)
# since it's just you managing your own site. If you ever add more
# admins or sensitive data, swap this for real login + hashed
# passwords (e.g. Supabase Auth).
# ---------------------------------------------------------------
def require_admin(x_admin_key: Optional[str] = Header(default=None)):
    if not x_admin_key or x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing admin key")


# ---------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------
class ContactMessageIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    subject: Optional[str] = Field(default=None, max_length=300)
    message: str = Field(min_length=1, max_length=5000)


class BlogPostIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=20000)
    cover_image_url: Optional[str] = None


class TestimonialIn(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    role: Optional[str] = Field(default=None, max_length=200)
    message: str = Field(min_length=1, max_length=2000)


class TestimonialStatusUpdate(BaseModel):
    status: Literal["pending", "approved", "rejected"]


@app.get("/")
def root():
    return {"status": "ok", "service": "Parth Portfolio API"}


# ---------------------------------------------------------------
# Contact messages
# ---------------------------------------------------------------
@app.post("/api/contact")
def submit_contact(payload: ContactMessageIn):
    result = supabase.table("contact_messages").insert(payload.model_dump()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Could not save your message")
    return {"success": True, "message": "Your message has been sent. Thank you!"}


@app.get("/api/admin/messages", dependencies=[Depends(require_admin)])
def list_messages():
    result = (
        supabase.table("contact_messages")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@app.patch("/api/admin/messages/{message_id}/read", dependencies=[Depends(require_admin)])
def mark_message_read(message_id: int):
    result = (
        supabase.table("contact_messages")
        .update({"is_read": True})
        .eq("id", message_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Message not found")
    return result.data[0]


@app.delete("/api/admin/messages/{message_id}", dependencies=[Depends(require_admin)])
def delete_message(message_id: int):
    supabase.table("contact_messages").delete().eq("id", message_id).execute()
    return {"success": True}


# ---------------------------------------------------------------
# Blog posts
# ---------------------------------------------------------------
@app.get("/api/blog")
def list_blog_posts():
    result = (
        supabase.table("blog_posts")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@app.post("/api/admin/blog", dependencies=[Depends(require_admin)])
def create_blog_post(payload: BlogPostIn):
    result = supabase.table("blog_posts").insert(payload.model_dump()).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Could not create post")
    return result.data[0]


@app.delete("/api/admin/blog/{post_id}", dependencies=[Depends(require_admin)])
def delete_blog_post(post_id: int):
    supabase.table("blog_posts").delete().eq("id", post_id).execute()
    return {"success": True}


# ---------------------------------------------------------------
# Testimonials
# ---------------------------------------------------------------
@app.get("/api/testimonials")
def list_approved_testimonials():
    result = (
        supabase.table("testimonials")
        .select("*")
        .eq("status", "approved")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@app.post("/api/testimonials")
def submit_testimonial(payload: TestimonialIn):
    data = payload.model_dump()
    data["status"] = "pending"
    result = supabase.table("testimonials").insert(data).execute()
    if not result.data:
        raise HTTPException(status_code=500, detail="Could not submit testimonial")
    return {"success": True, "message": "Thanks! Your testimonial will appear after review."}


@app.get("/api/admin/testimonials", dependencies=[Depends(require_admin)])
def list_all_testimonials():
    result = (
        supabase.table("testimonials")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


@app.patch("/api/admin/testimonials/{testimonial_id}", dependencies=[Depends(require_admin)])
def update_testimonial_status(testimonial_id: int, payload: TestimonialStatusUpdate):
    result = (
        supabase.table("testimonials")
        .update({"status": payload.status})
        .eq("id", testimonial_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Testimonial not found")
    return result.data[0]


@app.delete("/api/admin/testimonials/{testimonial_id}", dependencies=[Depends(require_admin)])
def delete_testimonial(testimonial_id: int):
    supabase.table("testimonials").delete().eq("id", testimonial_id).execute()
    return {"success": True}


# ---------------------------------------------------------------
# Visitor counter
# ---------------------------------------------------------------
@app.post("/api/visit")
def register_visit():
    current = supabase.table("page_visits").select("count").eq("id", 1).execute()
    if not current.data:
        supabase.table("page_visits").insert({"id": 1, "count": 1}).execute()
        return {"count": 1}
    new_count = current.data[0]["count"] + 1
    supabase.table("page_visits").update({"count": new_count}).eq("id", 1).execute()
    return {"count": new_count}


@app.get("/api/visit-count")
def get_visit_count():
    result = supabase.table("page_visits").select("count").eq("id", 1).execute()
    if not result.data:
        return {"count": 0}
    return {"count": result.data[0]["count"]}
