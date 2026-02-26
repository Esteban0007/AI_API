import argparse
import json
import time
import sys

import requests

TMDB_API_KEY = "cc433a69889d3e52798fb4c2cf6a69f4"
TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_LANG = "en-US"

READY_API_URL = "https://api.readyapi.net"
READY_API_KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"
HEADERS = {
    "x-api-key": READY_API_KEY,
    "Content-Type": "application/json",
    "accept": "application/json",
}


def fetch_movies(pages=100, sleep_sec=0.1):
    docs = []
    seen_ids = set()
    for page in range(1, pages + 1):
        url = f"{TMDB_BASE}/movie/popular?api_key={TMDB_API_KEY}&language={TMDB_LANG}&page={page}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            results = resp.json().get("results", [])
        except Exception as e:
            print(f"  Warning: Page {page} failed: {e}")
            continue

        for movie in results:
            m_id = movie["id"]
            if m_id in seen_ids:
                continue
            seen_ids.add(m_id)

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
                continue

            director = next(
                (
                    m["name"]
                    for m in details.get("credits", {}).get("crew", [])
                    if m["job"] == "Director"
                ),
                "Unknown",
            )
            cast = [m["name"] for m in details.get("credits", {}).get("cast", [])[:5]]
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
                    "tmdb_id": m_id,
                    "language": "en",
                    "original_title": details.get("original_title", ""),
                    "poster_path": poster_url,
                    "genres": genres,
                    "director": director,
                    "cast": cast,
                    "release_date": release_date,
                    "rating": details.get("vote_average", 0.0),
                },
            }
            docs.append(doc)

        print(f"  Page {page}/{pages} -- {len(docs)} movies so far", end="\r")
        if sleep_sec:
            time.sleep(sleep_sec)

    print()
    return docs


def clear_all_documents():
    print("Clearing all existing documents...")
    resp = requests.delete(
        f"{READY_API_URL}/api/v1/documents/clear-all",
        headers=HEADERS,
        timeout=30,
    )
    if resp.status_code == 200:
        data = resp.json()
        print(f"  Deleted {data.get('deleted_count', '?')} documents")
    else:
        print(f"  Warning: {resp.status_code}: {resp.text}")


def upload_all(docs):
    """
    Send all documents in one single request.
    The server automatically processes them in internal chunks of 50
    so the client never has to worry about splitting.
    """
    print(f"  Sending {len(docs)} documents (server batches internally)...")
    resp = requests.post(
        f"{READY_API_URL}/api/v1/documents/upload",
        headers=HEADERS,
        json={"documents": docs},
        timeout=600,
    )
    if resp.status_code == 200:
        data = resp.json()
        return data.get("uploaded_count", len(docs)), data.get("failed_count", 0)
    else:
        print(f"  Upload error {resp.status_code}: {resp.text[:300]}")
        return 0, len(docs)


def main():
    parser = argparse.ArgumentParser(description="Load TMDB movies into ReadyAPI")
    parser.add_argument(
        "--pages", type=int, default=100, help="TMDB pages to fetch (20 movies/page)"
    )
    parser.add_argument(
        "--sleep", type=float, default=0.1, help="Seconds between TMDB requests"
    )
    parser.add_argument(
        "--save-json", type=str, default="", help="Save fetched movies to a JSON file"
    )
    parser.add_argument(
        "--no-clear", action="store_true", help="Skip clearing existing documents"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("TMDB -> ReadyAPI Loader")
    print("=" * 60)

    if not args.no_clear:
        clear_all_documents()

    print(f"\nFetching from TMDB ({args.pages} pages ~ {args.pages * 20} movies)...")
    movies = fetch_movies(pages=args.pages, sleep_sec=args.sleep)
    print(f"  {len(movies)} movies fetched with descriptions\n")

    if args.save_json:
        with open(args.save_json, "w", encoding="utf-8") as f:
            json.dump({"documents": movies}, f, ensure_ascii=False, indent=2)
        print(f"  Saved to {args.save_json}\n")

    if not movies:
        print("No movies to upload. Exiting.")
        sys.exit(1)

    print(f"Uploading {len(movies)} movies (server handles chunking)...")
    ok, fail = upload_all(movies)

    print()
    print("=" * 60)
    print(f"Done! {ok} indexed, {fail} failed")
    print("=" * 60)


if __name__ == "__main__":
    main()
