# Current Recommendation Architecture

## Flow

API request
→ RecommendationService
→ ProductRepository
→ TF-IDF recommender
→ Optional LLM reranker
→ Store recommendation
→ Return products

## Current limitations

- Product retrieval uses only name and category.
- No product descriptions, reviews, or attributes are used.
- User personalization is limited.
- LLM reranker gets weak context.
- No vector search yet.
- No retrieval layer for user history.

## Target RAG architecture

Product descriptions, reviews, attributes
→ Product document builder
→ Embeddings
→ Vector store
→ Semantic product retrieval
→ LLM reranking

User history, purchases, preferences
→ User history documents
→ Embeddings
→ Vector store
→ Relevant user context retrieval
→ Personalized LLM recommendations