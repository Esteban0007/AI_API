import requests
import json

API_KEY = "cc433a69889d3e52798fb4c2cf6a69f4"
BASE_URL = "https://api.themoviedb.org/3"
LANG = "en-US"


def get_movie_data(pages=100):
    final_json = {"documents": []}

    for page in range(1, pages + 1):
        # 1. Get list of popular movies
        url = f"{BASE_URL}/movie/popular?api_key={API_KEY}&language={LANG}&page={page}"
        response = requests.get(url).json()

        for movie in response.get("results", []):
            m_id = movie["id"]

            # 2. Get extra details (Credits for Director and Cast)
            detail_url = f"{BASE_URL}/movie/{m_id}?api_key={API_KEY}&language={LANG}&append_to_response=credits,keywords"
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
                    "poster_path": f"https://image.tmdb.org/t/p/w500{details.get('poster_path')}",
                },
            }
            final_json["documents"].append(doc)

    return final_json


# Run for the first 5 pages to get a solid 100-movie dataset
data = get_movie_data(pages=5)

# Save the result
with open("dataset_movies_en.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Dataset successfully generated in 'dataset_movies_en.json'")
