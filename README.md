# Dark Web Deanonymization Backend

A FastAPI-based backend system for analyzing relationships between actors, handles, wallets, and posts.

---

## Features

- Actor profiling
- Handle tracking
- Wallet mapping
- Post storage
- Connection analysis
- Search functionality

---

## Tech Stack

- FastAPI
- PostgreSQL
- psycopg2
- Uvicorn

---
##  Project Architecture

> **DarkTrace** transforms scattered threat-intelligence data into structured,
> searchable intelligence for cyber investigations.

```text
                          DARKTRACE
                              │
                              ▼
                    ┌──────────────────┐
                    │      main.py     │
                    │  FastAPI Engine  │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         DATABASE          CRUD          CONNECTION
       database.py       crud.py        connection.py
              │              │              │
              └──────────────┼──────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │     ROUTES    │
                    └───────┬────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
       ACTORS            HANDLES           WALLETS
     actors.py         handles.py         wallets.py
          │                 │                 │
          └──────────┐      │      ┌──────────┘
                     ▼      ▼      ▼
                   POSTS    PROFILE
                 posts.py  profile.py
                       \      /
                        \    /
                         ▼  ▼
                        SEARCH
                     search.py
                         │
                         ▼
                   Intelligence
                     Results
```

###  Repository Blueprint

 backend
│
├──  app
│   │
│   ├──  main.py
│   │      └── Application Entry Point
│   │
│   ├──  database.py
│   │      └── Database Configuration
│   │
│   ├──  crud.py
│   │      └── CRUD Operations
│   │
│   ├──  connection.py
│   │      └── Database Connectivity
│   │
│   └──  routes
│       │
│       ├──  actors.py
│       │      └── Threat Actor Intelligence
│       │
│       ├──  handles.py
│       │      └── Handle / Alias Analysis
│       │
│       ├──  wallets.py
│       │      └── Cryptocurrency Wallet Intelligence
│       │
│       ├── posts.py
│       │      └── Post & Content Analysis
│       │
│       ├──  profile.py
│       │      └── Actor Profile Generation
│       │
│       └──  search.py
│              └── Investigation & Search Engine
│
├──  requirements.txt
│      └── Python Dependencies
│
└──  README.md
       └── Project Documentation

## Setup

1. Clone repo

git clone <your-repo-link>
cd backend

2. Install dependencies

pip install -r requirements.txt

3. Setup database

Create database in PostgreSQL:

CREATE DATABASE darkweb;

Update database config in app/database.py:

dbname="darkweb"
user="postgres"
password="your_password"
host="localhost"
port="5432"

4. Run server

uvicorn app.main:app --reload

---

## API Docs

http://127.0.0.1:8000/docs

---

## Endpoints

Actors  
GET /actors/  
GET /actors/{actor_id}  
GET /actors/{actor_id}/details  

Handles  
GET /handles/  
GET /handles/{handle_id}  
GET /handles/actor/{actor_id}  

Wallets  
GET /wallets/  
POST /wallets/  

Posts  
GET /posts/  
POST /posts/  

Connections  
GET /connections/  
GET /connections/{actor_id}  

Search  
GET /search/?q=keyword  

---

## Sample Requests

Create Wallet

{
  "actor_id": 1,
  "wallet_address": "0xABC123"
}

Create Post

{
  "handle_id": 1,
  "content": "sample post"
}

---

## Notes

- actor_id must exist before creating wallet
- handle_id must exist before creating post
- returns 400 if invalid IDs

---

## Status

Backend APIs completed and working.  
Ready for frontend integration.
