#!/usr/bin/env python3
"""Upload clothing items to the user_1 tenant"""
import requests
import json

API_URL = "https://readyapi.net/api/v1/documents/upload"
API_KEY = "rapi_Nqvs8mqbsWASMqBThAtcprLnc7YUUFHHE2rpKpcDCnc"

documents = [
    {
        "id": "clothing_001",
        "title": "Classic Rock Band T-Shirt",
        "content": "Vintage-style cotton t-shirt featuring iconic rock band graphics. Perfect for music lovers and casual wear.",
        "keywords": ["tshirt", "rock", "music", "casual", "cotton", "vintage"],
        "metadata": {
            "gender": "unisex",
            "category": "tops",
            "style": "casual",
            "image": "https://images.unsplash.com/photo-1576566588028-4147f3842f27",
        },
    },
    {
        "id": "clothing_002",
        "title": "Slim Fit Blue Jeans",
        "content": "Classic blue denim jeans with a modern slim fit. Durable and stylish for everyday wear.",
        "keywords": ["jeans", "denim", "blue", "slim", "casual", "pants"],
        "metadata": {
            "gender": "unisex",
            "category": "bottoms",
            "style": "casual",
            "image": "https://images.unsplash.com/photo-1542272604-787c3835535d",
        },
    },
    {
        "id": "clothing_003",
        "title": "Black Leather Biker Jacket",
        "content": "Premium leather jacket with classic biker design. Features multiple pockets and silver zippers.",
        "keywords": ["jacket", "leather", "biker", "black", "premium", "outerwear"],
        "metadata": {
            "gender": "unisex",
            "category": "outerwear",
            "style": "edgy",
            "image": "https://images.unsplash.com/photo-1551028719-00167b16eac5",
        },
    },
    {
        "id": "clothing_004",
        "title": "Floral Summer Dress",
        "content": "Light and breezy floral print dress perfect for summer days. Features adjustable straps and flowing skirt.",
        "keywords": ["dress", "floral", "summer", "feminine", "lightweight", "pattern"],
        "metadata": {
            "gender": "women",
            "category": "dresses",
            "style": "feminine",
            "image": "https://images.unsplash.com/photo-1595777457583-95e059d581b8",
        },
    },
    {
        "id": "clothing_005",
        "title": "Performance Running Sneakers",
        "content": "High-performance athletic sneakers with cushioned sole and breathable mesh. Ideal for running and training.",
        "keywords": [
            "sneakers",
            "running",
            "athletic",
            "performance",
            "sports",
            "shoes",
        ],
        "metadata": {
            "gender": "unisex",
            "category": "shoes",
            "style": "athletic",
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff",
        },
    },
    {
        "id": "clothing_006",
        "title": "Cozy Wool Knit Sweater",
        "content": "Warm and comfortable wool blend sweater with classic cable knit pattern. Perfect for cold weather.",
        "keywords": ["sweater", "wool", "knit", "warm", "winter", "cozy"],
        "metadata": {
            "gender": "unisex",
            "category": "tops",
            "style": "casual",
            "image": "https://images.unsplash.com/photo-1576871337632-b9aef4c17ab9",
        },
    },
    {
        "id": "clothing_007",
        "title": "Khaki Cargo Shorts",
        "content": "Practical cargo shorts with multiple pockets. Made from durable cotton blend for outdoor activities.",
        "keywords": ["shorts", "cargo", "khaki", "practical", "outdoor", "pockets"],
        "metadata": {
            "gender": "men",
            "category": "bottoms",
            "style": "casual",
            "image": "https://images.unsplash.com/photo-1591195853828-11db59a44f6b",
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
