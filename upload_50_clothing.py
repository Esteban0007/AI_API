#!/usr/bin/env python3
"""Upload 50 clothing items to the user_1 tenant"""
import requests
import json

API_URL = "https://readyapi.net/api/v1/documents/upload"
API_KEY = "rapi_Nqvs8mqbsWASMqBThAtcprLnc7YUUFHHE2rpKpcDCnc"

documents = [
    {
        "id": "001",
        "title": "t-shirt",
        "content": "white cotton t-shirt",
        "keywords": ["basic", "casual"],
        "metadata": {
            "price": "15.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500",
        },
    },
    {
        "id": "002",
        "title": "jeans",
        "content": "blue denim jeans",
        "keywords": ["denim", "casual"],
        "metadata": {
            "price": "45.00",
            "sex": "male",
            "source": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=500",
        },
    },
    {
        "id": "003",
        "title": "dress",
        "content": "black formal dress",
        "keywords": ["formal", "elegant"],
        "metadata": {
            "price": "60.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=500",
        },
    },
    {
        "id": "004",
        "title": "jacket",
        "content": "black leather jacket",
        "keywords": ["outerwear", "rock"],
        "metadata": {
            "price": "120.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500",
        },
    },
    {
        "id": "005",
        "title": "sneakers",
        "content": "white leather sneakers",
        "keywords": ["shoes", "sport"],
        "metadata": {
            "price": "75.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1549298916-b41d501d3772?w=500",
        },
    },
    {
        "id": "006",
        "title": "hoodie",
        "content": "grey cotton hoodie",
        "keywords": ["streetwear", "cozy"],
        "metadata": {
            "price": "35.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=500",
        },
    },
    {
        "id": "007",
        "title": "shirt",
        "content": "blue slim shirt",
        "keywords": ["office", "formal"],
        "metadata": {
            "price": "30.00",
            "sex": "male",
            "source": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=500",
        },
    },
    {
        "id": "008",
        "title": "shorts",
        "content": "beige cargo shorts",
        "keywords": ["summer", "casual"],
        "metadata": {
            "price": "25.00",
            "sex": "male",
            "source": "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=500",
        },
    },
    {
        "id": "009",
        "title": "skirt",
        "content": "blue denim skirt",
        "keywords": ["casual", "summer"],
        "metadata": {
            "price": "22.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=500",
        },
    },
    {
        "id": "010",
        "title": "coat",
        "content": "brown wool coat",
        "keywords": ["winter", "elegant"],
        "metadata": {
            "price": "150.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=500",
        },
    },
    {
        "id": "011",
        "title": "beanie",
        "content": "yellow knit beanie",
        "keywords": ["winter", "accessory"],
        "metadata": {
            "price": "12.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1576871337622-98d48d1cf531?w=500",
        },
    },
    {
        "id": "012",
        "title": "blazer",
        "content": "navy blue blazer",
        "keywords": ["formal", "business"],
        "metadata": {
            "price": "85.00",
            "sex": "male",
            "source": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=500",
        },
    },
    {
        "id": "013",
        "title": "boots",
        "content": "brown leather boots",
        "keywords": ["shoes", "winter"],
        "metadata": {
            "price": "110.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1520639889410-d2a6d7ecce95?w=500",
        },
    },
    {
        "id": "014",
        "title": "scarf",
        "content": "red wool scarf",
        "keywords": ["winter", "accessory"],
        "metadata": {
            "price": "18.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=500",
        },
    },
    {
        "id": "015",
        "title": "heels",
        "content": "red high heels",
        "keywords": ["elegant", "party"],
        "metadata": {
            "price": "55.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=500",
        },
    },
    {
        "id": "016",
        "title": "socks",
        "content": "white cotton socks",
        "keywords": ["basic", "underwear"],
        "metadata": {
            "price": "8.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1582966232435-02758f81014e?w=500",
        },
    },
    {
        "id": "017",
        "title": "polo",
        "content": "green cotton polo",
        "keywords": ["sport", "casual"],
        "metadata": {
            "price": "32.00",
            "sex": "male",
            "source": "https://images.unsplash.com/photo-1586363104862-3a5e2ab60d99?w=500",
        },
    },
    {
        "id": "018",
        "title": "cardigan",
        "content": "beige knit cardigan",
        "keywords": ["knitwear", "warm"],
        "metadata": {
            "price": "45.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1608234808654-2a8875faa7fd?w=500",
        },
    },
    {
        "id": "019",
        "title": "belt",
        "content": "black leather belt",
        "keywords": ["leather", "accessory"],
        "metadata": {
            "price": "20.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1624222247344-550fb80583dc?w=500",
        },
    },
    {
        "id": "020",
        "title": "swimsuit",
        "content": "blue one-piece swimsuit",
        "keywords": ["summer", "beach"],
        "metadata": {
            "price": "28.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1557353425-6c61136de070?w=500",
        },
    },
    {
        "id": "021",
        "title": "sweater",
        "content": "blue wool sweater",
        "keywords": ["winter", "warm"],
        "metadata": {
            "price": "48.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1556905085-866159f4f5a2?w=500",
        },
    },
    {
        "id": "022",
        "title": "cap",
        "content": "black baseball cap",
        "keywords": ["sport", "accessory"],
        "metadata": {
            "price": "15.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=500",
        },
    },
    {
        "id": "023",
        "title": "trousers",
        "content": "grey chino trousers",
        "keywords": ["formal", "casual"],
        "metadata": {
            "price": "38.00",
            "sex": "male",
            "source": "https://images.unsplash.com/photo-1624371414361-e6e8ea48f4e2?w=500",
        },
    },
    {
        "id": "024",
        "title": "sandals",
        "content": "leather brown sandals",
        "keywords": ["summer", "shoes"],
        "metadata": {
            "price": "30.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1562273138-f46be4ebdf33?w=500",
        },
    },
    {
        "id": "025",
        "title": "sunglasses",
        "content": "black aviator sunglasses",
        "keywords": ["accessory", "summer"],
        "metadata": {
            "price": "40.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1511499767350-a1590fdb28bf?w=500",
        },
    },
    {
        "id": "026",
        "title": "pajamas",
        "content": "blue silk pajamas",
        "keywords": ["nightwear", "silk"],
        "metadata": {
            "price": "50.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1598554747436-c9293d6a588f?w=500",
        },
    },
    {
        "id": "027",
        "title": "tie",
        "content": "red silk tie",
        "keywords": ["formal", "accessory"],
        "metadata": {
            "price": "25.00",
            "sex": "male",
            "source": "https://images.unsplash.com/photo-1589756823851-411590f89829?w=500",
        },
    },
    {
        "id": "028",
        "title": "gloves",
        "content": "black leather gloves",
        "keywords": ["winter", "accessory"],
        "metadata": {
            "price": "35.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1549439602-43ebca2327af?w=500",
        },
    },
    {
        "id": "029",
        "title": "vest",
        "content": "quilted blue vest",
        "keywords": ["outerwear", "winter"],
        "metadata": {
            "price": "45.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1626497748470-0716492d5448?w=500",
        },
    },
    {
        "id": "030",
        "title": "suit",
        "content": "black formal suit",
        "keywords": ["formal", "wedding"],
        "metadata": {
            "price": "220.00",
            "sex": "male",
            "source": "https://images.unsplash.com/photo-1594932224828-b4b059b6f68d?w=500",
        },
    },
    {
        "id": "031",
        "title": "raincoat",
        "content": "yellow waterproof raincoat",
        "keywords": ["outerwear", "rain"],
        "metadata": {
            "price": "55.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1520975661595-6453be3f7070?w=500",
        },
    },
    {
        "id": "032",
        "title": "leggings",
        "content": "black sport leggings",
        "keywords": ["sport", "gym"],
        "metadata": {
            "price": "22.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1506629082925-63bd688022ba?w=500",
        },
    },
    {
        "id": "033",
        "title": "loafers",
        "content": "brown suede loafers",
        "keywords": ["shoes", "formal"],
        "metadata": {
            "price": "80.00",
            "sex": "male",
            "source": "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=500",
        },
    },
    {
        "id": "034",
        "title": "backpack",
        "content": "black canvas backpack",
        "keywords": ["accessory", "bag"],
        "metadata": {
            "price": "45.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500",
        },
    },
    {
        "id": "035",
        "title": "tights",
        "content": "black nylon tights",
        "keywords": ["underwear", "female"],
        "metadata": {
            "price": "10.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1551139724-4f0578887095?w=500",
        },
    },
    {
        "id": "036",
        "title": "blouse",
        "content": "white silk blouse",
        "keywords": ["formal", "female"],
        "metadata": {
            "price": "34.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1584030373081-f37b7bb4fa8e?w=500",
        },
    },
    {
        "id": "037",
        "title": "watch",
        "content": "silver metal watch",
        "keywords": ["accessory", "luxury"],
        "metadata": {
            "price": "150.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=500",
        },
    },
    {
        "id": "038",
        "title": "boxers",
        "content": "cotton blue boxers",
        "keywords": ["underwear", "male"],
        "metadata": {
            "price": "12.00",
            "sex": "male",
            "source": "https://images.unsplash.com/photo-1590673885247-aa7f1522a8a7?w=500",
        },
    },
    {
        "id": "039",
        "title": "wallet",
        "content": "brown leather wallet",
        "keywords": ["accessory", "leather"],
        "metadata": {
            "price": "28.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1627123430984-71d3d9d52ce9?w=500",
        },
    },
    {
        "id": "040",
        "title": "jewelry",
        "content": "gold necklace",
        "keywords": ["accessory", "gold"],
        "metadata": {
            "price": "90.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500",
        },
    },
    {
        "id": "041",
        "title": "slippers",
        "content": "grey wool slippers",
        "keywords": ["home", "shoes"],
        "metadata": {
            "price": "15.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1591534049594-b43063806295?w=500",
        },
    },
    {
        "id": "042",
        "title": "bra",
        "content": "black lace bra",
        "keywords": ["underwear", "female"],
        "metadata": {
            "price": "25.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1580214691763-8a07f7c4587a?w=500",
        },
    },
    {
        "id": "043",
        "title": "denim jacket",
        "content": "blue denim jacket",
        "keywords": ["outerwear", "casual"],
        "metadata": {
            "price": "55.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1523205771623-e0faa4d2813d?w=500",
        },
    },
    {
        "id": "044",
        "title": "tunic",
        "content": "white linen tunic",
        "keywords": ["summer", "casual"],
        "metadata": {
            "price": "32.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1581044777550-4cfa60707c03?w=500",
        },
    },
    {
        "id": "045",
        "title": "briefcase",
        "content": "leather brown briefcase",
        "keywords": ["bag", "office"],
        "metadata": {
            "price": "95.00",
            "sex": "male",
            "source": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500",
        },
    },
    {
        "id": "046",
        "title": "windbreaker",
        "content": "neon sports windbreaker",
        "keywords": ["outerwear", "sport"],
        "metadata": {
            "price": "45.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?w=500",
        },
    },
    {
        "id": "047",
        "title": "tank top",
        "content": "white tank top",
        "keywords": ["basic", "summer"],
        "metadata": {
            "price": "12.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=500",
        },
    },
    {
        "id": "048",
        "title": "bow tie",
        "content": "black silk bow tie",
        "keywords": ["formal", "accessory"],
        "metadata": {
            "price": "15.00",
            "sex": "male",
            "source": "https://images.unsplash.com/photo-1556011559-69f8c6792348?w=500",
        },
    },
    {
        "id": "049",
        "title": "parka",
        "content": "olive green parka",
        "keywords": ["winter", "outerwear"],
        "metadata": {
            "price": "130.00",
            "sex": "unisex",
            "source": "https://images.unsplash.com/photo-1544923246-77307dd654ca?w=500",
        },
    },
    {
        "id": "050",
        "title": "beret",
        "content": "black wool beret",
        "keywords": ["accessory", "french"],
        "metadata": {
            "price": "20.00",
            "sex": "female",
            "source": "https://images.unsplash.com/photo-1575425186775-b8de9a427e67?w=500",
        },
    },
]

payload = {"documents": documents}

response = requests.post(
    API_URL,
    headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
    json=payload,
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
