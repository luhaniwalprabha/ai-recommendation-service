# AI Recommendation System with RAG + Hybrid Ranking

## Problem

Modern recommendation systems need to combine:
- user behavior
- product similarity
- personalization
- explainability

This project builds a production-style recommendation engine that combines
RAG (Retrieval-Augmented Generation) with hybrid ranking and LLM-based reasoning.


## Architecture

The system follows a multi-stage pipeline:

1. Candidate Generation
   - Vector similarity (embeddings)
   - TF-IDF fallback

2. Filtering
   - Removes already seen products

3. Hybrid Ranking
   - Combines rating, user preferences, and semantic context

4. User RAG
   - Retrieves relevant user interactions using vector search

5. LLM Re-ranking (optional)
   - Uses GPT to re-rank candidates with reasoning

6. Fallback Explanation
   - Generates reasons even when LLM is unavailable


## Features

- FastAPI-based recommendation API
- Product + User RAG
- Hybrid ranking (rating + preference + context)
- LLM-based re-ranking (with fallback)
- Explainable recommendations
- Debug API for pipeline inspection
- Dev mode (no DB/Redis required)


## Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload

Test:
curl -X POST "http://127.0.0.1:8000/v1/recommendations/debug?user_id=101"