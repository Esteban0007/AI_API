from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.db.users import get_user_by_shopify_domain, register_shopify_shop

router = APIRouter()

class ShopifyRegisterRequest(BaseModel):
    shop: str

@router.get("/check")
async def check_shop(shop: str = Query(..., description="Dominio de la tienda de Shopify")):
    """
    Comprueba de forma silenciosa desde el backend si una tienda ya está registrada.
    Devuelve la información de la tienda junto con su API Key dinámica.
    """
    user = get_user_by_shopify_domain(shop)
    if user:
        return {
            "vinculado": True, 
            "shopify_domain": user["shopify_domain"],
            "created_at": user["created_at"],
            "api_key": user["api_key"]  # <-- Esto es lo que repara el dinamismo
        }
    return {"vinculado": False}

@router.post("/register")
async def register_shop(payload: ShopifyRegisterRequest):
    """
    Registra de forma automática la tienda de Shopify en la base de datos central.
    """
    shop_domain = payload.shop
    result = register_shopify_shop(shop_domain)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["message"])
        
    return {
        "success": True,
        "message": "Enlace completado con éxito",
        "api_key": result["api_key"]
    }
