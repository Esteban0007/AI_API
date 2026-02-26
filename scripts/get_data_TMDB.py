"""
Download 2000 movies from TMDB and load them directly into the ReadyAPI.

Steps:
  1. Clear all existing documents via DELETE /api/v1/documents/clear-all
  2. Fetch 2000 movies from TMDB (100 pages × 20 results) with full details
  3. Upload them in batches of 50 via POST /api/v1/documents/upload

Usage:
    python scripts/get_data_TMDB.py
    python scripts/get_data_TMDB.py --pages 100 --batch 50 --save-json movies.json
"""

import argparse
import json
import time
import sys

import requests

# ── TMDB ────────────────────────────────────────────────────────────────────
TMDB_API_KEY = "cc433a69889d3e52798fb4c2cf6a69f4"
TMDB_BASE    = "https://api.themoviedb.org/3"
TMDB_LANG    = "en-US"

# ── ReadyAPI ─────────────────────────────────────────────────────────────────
READY_API_URL = "https://api.readyapi.net"
READY_API_KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"
HEADERS = {
    "x-api-key": READY_API_KEY,
    "Content-Type": "application/json",
    "accept": "application/json",
}


# ── Fetch from TMDB ──────────────────────────────────────────────────────────

def fetch_movies(pages: int = 100, sleep_sec: float = 0.1) -> list:
    """Fetch up to pages×20 unique movies with full details from TMDB."""
    docs = []
    seen_ids = set()

    for page in range(1, pages + 1):
        url = f"{TMDB_BASE}/movie/popular?api_key={TMDB_API_KEY}&language={TMDB_LANG}&page={page}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            results = resp.json().get("results", [])
        except Exception as e:
            print(f"  ⚠️  Page {page} failed: {e}")
            continue

        for movie in results:
            m_id = movie["id"]
            if m_id in seen_ids:
                continue
            seen_ids.add(m_id)

            # Full details + credits
            detail_url = (
                f"{TMDB_BASE}/movie/{m_id}?api_key={TMDB_API_KEY}&language={TMDB_LANG}"
                f"&append_to_response=credits"
            )
            try:
                details = requests.get(detail_url, timeout=10).json()
            except Exception:
                continue

            overview = (details.get("overview") or "").strip()
            if not overview:
                continue  # skip movies with no description

            director = next(
                (m["name"] for m in details.get("credits", {}).get("crew", [])
                 if m["job"] == "Director"),
                "Unknown",
            )
            cast   = [m["name"] for m in details.get("credits", {}).get("cast", [])[:5]]
            genres = [g["name"] for g in details.get("genres", [])]

            poster = details.get("poster_path")
            poster_url = f"https://image.tmdb.org/t/p/w500{poster}" if poster else ""

            release_date = details.get("release_date", "")

            doc = {
                "id": f"tmdb-{m_id}",
                "title": details.get("title", movie.get("title", "")),
                "content": overview,
                "keywords": [],
                "metadata": {
                    "tmdb_id":        m_id,
                    "language":       "en",
                    "original_title": details.get("original_title", ""),
                    "poster_path":    poster_url,
                    "genres":         genres,
                    "director":       director,
                    "cast":           cast,
                    "release_date":   release_date,
                    "rating":         details.get("vote_average", 0.0),
                },
            }
            docs.append(doc)

        print(f"  Page {page}/{pages} — {len(docs)} movies so far", end="\r")
        if sleep_sec:
            time.sleep(sleep_sec)

    print()
    return docs


# ── ReadyAPI helpers ─────────────────────────────────────────────────────────

def clear_all_documents():
    """Delete all existing documents from the ReadyAPI collection."""
    print("🗑️  Clearing all existing documents...")
    resp = requests.delete(
        f"{READY_API_URL}/api/v1/documents/clear-all",
        headers=HEADERS,
        timeout=30,
    )
    if resp.status_code == 200:
        data = resp.json()
        print(f"   ✅ Deleted {data.get('deleted_count', '?')} documents")
    else:
        print(f"   ⚠️  Clear returned {resp.status_code}: {resp.text}")


def upload_all(docs: list) -> tuple[int, int]:
    """Upload all documents in one request — server handles internal chunking."""
    payload = {"documents": docs}
    print(f"   Sending {len(docs)} documents to the API (server will batch internally)...")
    resp = requests.post(
        f"{READY_API_URL}/api/v1/documents/upload",
        headers=HEADERS,
        json=payload,
        timeout=600,  # up to 10 min for large datasets
    )
    if resp.status_code == 200:
        data = resp.json()
        return data.get("uploaded_count", len(docs)), data.get("failed_count", 0)
    else:
        print(f"   ⚠️  Upload error {resp.status_code}: {resp.text[:300]}")
        return 0, len(docs)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Load 2000 TMDB movies into ReadyAPI")
    parser.add_argument("--pages",     type=int,   default=100,  help="TMDB pages to fetch (20 movies/page)")
    parser.add_argument("--batch",     type=int,   default=50,   help="Upload batch size")
    parser.add_argument("--sleep",     type=float, default=0.1,  help="Seconds between TMDB page requests")
    parser.add_argument("--save-json", type=str,   default="",   help="Also save movies to a JSON file")
    parser.add_argument("--no-clear",  action="store_true",      help="Skip clearing existing documents")
    args = parser.parse_args()

    print("=" * 60)
    print("🎬  TMDB → ReadyAPI Loader")
    print("=" * 60)

    # Step 1: clear existing docs
    if not args.no_clear:
        clear_all_documents()

    # Step 2: fetch movies from TMDB
    print(f"\n📥  Fetching movies from TMDB ({args.pages} pages ≈ {args.pages * 20} movies)...")
    movies = fetch_movies(pages=args.pages, sleep_sec=args.sleep)
    print(f"   ✅ Fetched {len(movies)} movies with descriptions\n")

    # Optionally save to JSON
    if args.save_json:
        with open(args.save_json, "w", encoding="utf-8") as f:
            json.dump({"documents": movies}, f, ensure_ascii=False, indent=2)
        print(f"   💾  Saved to {args.save_json}\n")

    if not movies:
        print("❌ No movies to upload. Exiting.")
        sys.exit(1)

    # Step 3: upload everything in one single call
    print(f"📤  Uploading {len(movies)} movies (server batches internally)...")
    ok, fail = upload_all(movies)

    print()
    print("=" * 60)
    print(f"✅  Done! {ok} movies indexed, {fail} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()


API_KEY = "cc433a69889d3e52798fb4c2cf6a69f4"
BASE_URL = "https://api.themoviedb.org/3"
LANG = "en-US"


import argparse
import time
def get_movie_data(pages=100):
    final_json = {"documents": []}

    for page in range(1, pages + 1):
        # 1. Get list of popular movies
def get_movie_data(pages=100, sleep_seconds=0.0):
        response = requests.get(url).json()
    seen_ids = set()

        for movie in response.get("results", []):
            m_id = movie["id"]

            # 2. Get extra details (Credits for Director and Cast)
            detail_url = f"{BASE_URL}/movie/{m_id}?api_key={API_KEY}&language={LANG}&append_to_response=credits,keywords"
            details = requests.get(detail_url).json()

            # Extract Director
            # Skip duplicates
            if m_id in seen_ids:
                continue
            seen_ids.add(m_id)
            director = next(
                (
                    member["name"]
                    for member in details.get("credits", {}).get("crew", [])
                    if member["job"] == "Director"
                ),
                "Unknown",
            )

            # Extract Top 3 Actors
            cast = [
                member["name"]
                for member in details.get("credits", {}).get("cast", [])[:3]
            ]

            # Extract Genres
            genres = [g["name"] for g in details.get("genres", [])]

            # 3. Format according to your structure
            doc = {
                "id": f"tmdb-{m_id}",
                "title": details.get("title"),
                "content": details.get("overview"),
                "keywords": [director]
                + genres
            poster_path = details.get("poster_path")
            full_poster_url = (
                f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
            )
                + cast
                + [details.get("release_date", "")[:4]],
                "metadata": {
                    "tmdb_id": m_id,
                    "language": "en",
                    "original_title": details.get("original_title"),
                    "poster_path": f"https://image.tmdb.org/t/p/w500{details.get('poster_path')}",
                    "genres": genres,
                    "director": director,
                    "cast": cast,
                    "release_date": details.get("release_date"),
                    "rating": details.get("vote_average"),
                },
                    "poster_path": full_poster_url,
            final_json["documents"].append(doc)

    return final_json


# Run for 40 pages to get ~2000-movie dataset (50 movies per page)
# Note: TMDB API may return fewer results due to filtering
print("Downloading movies from TMDB... (this takes a few minutes)")
data = get_movie_data(pages=40)
        if sleep_seconds:
            time.sleep(sleep_seconds)

# Save the result
with open("tmdb_2000_movies.json", "w", encoding="utf-8") as f:
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download TMDB movie dataset")
    parser.add_argument(
        "--pages",
        type=int,
        default=100,
        help="Number of pages to fetch (20 movies per page). 100 pages ≈ 2000 movies",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.0,
        help="Seconds to sleep between pages (avoid rate limits)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="tmdb_2000_movies.json",
        help="Output JSON filename",
    )

    args = parser.parse_args()

    print("Downloading movies from TMDB... (this takes a few minutes)")
    data = get_movie_data(pages=args.pages, sleep_seconds=args.sleep)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(
        f"✅ Dataset successfully generated with {len(data['documents'])} movies in '{args.output}'"
    )
