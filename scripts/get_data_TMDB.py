import argparse
import json
import time

import requests

API_KEY = "cc433a69889d3e52798fb4c2cf6a69f4"
BASE_URL = "https://api.themoviedb.org/3"
LANG = "en-US"


def get_movie_data(pages: int = 100, sleep_seconds: float = 0.0):
    final_json = {"documents": []}
    seen_ids = set()

    for page in range(1, pages + 1):
        # 1. Get list of popular movies
        url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language={LANG}&page={page}"
        response = requests.get(url).json()

        for movie in response.get("results", []):
            m_id = movie["id"]

            # Skip duplicates
            if m_id in seen_ids:
                continue
            seen_ids.add(m_id)

            # 2. Get extra details (Credits for Director and Cast)
            detail_url = (
                f"{BASE_URL}/movie/{m_id}?api_key={API_KEY}&language={LANG}"
                f"&append_to_response=credits,keywords"
            )
            details = requests.get(detail_url).json()

            # Extract Director
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

            poster_path = details.get("poster_path")
            full_poster_url = (
                f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
            )

            # 3. Format according to your structure
            doc = {
                "id": f"tmdb-{m_id}",
                "title": details.get("title"),
                "content": details.get("overview"),
                "keywords": [director]
                + genres
                + cast
                + [details.get("release_date", "")[:4]],
                "metadata": {
                    "tmdb_id": m_id,
                    "language": "en",
                    "original_title": details.get("original_title"),
                    "poster_path": full_poster_url,
                    "genres": genres,
                    "director": director,
                    "cast": cast,
                    "release_date": details.get("release_date"),
                    "rating": details.get("vote_average"),
                },
            }
            final_json["documents"].append(doc)

        if sleep_seconds:
            time.sleep(sleep_seconds)

    return final_json


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
    )import requests
import json

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
