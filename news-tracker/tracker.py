import os
import yaml
import feedparser
import requests
import trafilatura
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from sentence_transformers import SentenceTransformer
import hdbscan

# ---------- Utility Functions ----------

def load_sources(path="sources.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def fetch_articles(sources, limit=120):
    articles = []
    for src in sources.get("sources", []):
        feed = feedparser.parse(src["url"])
        for entry in feed.entries[:limit]:
            articles.append({
                "title": entry.get("title", "No title"),
                "link": entry.get("link", ""),
                "published": entry.get("published", "")
            })
    return articles[:limit]

def extract_text(url):
    try:
        downloaded = trafilatura.fetch_url(url)
        return trafilatura.extract(downloaded)
    except Exception:
        return None

def embed_articles(articles, model):
    texts = [a["title"] for a in articles]
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    return embeddings

def cluster_embeddings(embeddings, min_cluster_size=3):
    clusterer = hdbscan.HDBSCAN(min_cluster_size=min_cluster_size)
    labels = clusterer.fit_predict(embeddings)
    return labels

def summarize_cluster(texts):
    """Fallback simple summarization (first 2 sentences)."""
    combined = " ".join(texts)
    sentences = combined.split(". ")
    return ". ".join(sentences[:2]) + "..."

def generate_clusters(articles, labels):
    clusters = {}
    for article, label in zip(articles, labels):
        if label == -1:
            continue  # skip noise
        if label not in clusters:
            clusters[label] = {"items": [], "summary": ""}
        clusters[label]["items"].append(article)

    # Summarize
    for label, cluster in clusters.items():
        texts = [item["title"] for item in cluster["items"]]
        cluster["summary"] = summarize_cluster(texts)

    return clusters

def save_report(run_dir, clusters):
    os.makedirs(run_dir, exist_ok=True)
    report_path = os.path.join(run_dir, "report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        for i, (label, cluster) in enumerate(clusters.items()):
            f.write(f"## Cluster {i}\n")
            f.write(f"**Summary:** {cluster['summary']}\n\n")
            for item in cluster["items"]:
                f.write(f"- [{item['title']}]({item['link']})\n")
            f.write("\n")
    print(f"✅ Report saved at: {report_path}")

# ---------- Main ----------

if __name__ == "__main__":
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = os.path.join("data", "runs", run_id)
    os.makedirs(run_dir, exist_ok=True)
    print(f"Run directory: {run_dir}")

    # Step 1: Load sources
    sources = load_sources("sources.yaml")

    # Step 2: Fetch articles
    articles = fetch_articles(sources, limit=120)
    print(f"Fetched {len(articles)} items")

    # Step 3: Embed
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = embed_articles(articles, model)

    # Step 4: Cluster
    labels = cluster_embeddings(embeddings)
    clusters = generate_clusters(articles, labels)
    print(f"Clusters found: {len(clusters)}")

    # Step 5: Save report
    save_report(run_dir, clusters)
