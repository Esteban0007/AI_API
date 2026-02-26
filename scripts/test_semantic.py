import requests

KEY = "rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg"
URL = "https://api.readyapi.net/api/v1/search/query"
H = {"x-api-key": KEY, "Content-Type": "application/json"}

tests = [
    ("love story with sad ending", "💔 Historia de amor triste"),
    ("superhero saves the world", "🦸 Superhéroe salva el mundo"),
    ("intelligent robot wants to be human", "🤖 Robot quiere ser humano"),
    ("war survival extreme conditions", "⚔️  Guerra y supervivencia"),
    ("bank heist robbery stolen money", "💰 Robo a banco"),
    ("animated movie with talking animals", "🐾 Animación animales"),
    ("space exploration alien planet", "🚀 Exploración espacial"),
    ("serial killer detective thriller", "🔪 Asesino en serie detective"),
]

for query, label in tests:
    r = requests.post(URL, headers=H, json={"query": query, "top_k": 3})
    data = r.json()
    ms = data.get("execution_time_ms", 0)
    results = data.get("results", [])
    print(f"{label}  ({ms:.0f}ms)")
    for x in results:
        print(f"   {x['score']:.3f} | {x['title']} ({x['metadata'].get('year', '')})")
    print()
