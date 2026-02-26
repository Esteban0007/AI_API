# 🔧 Herramientas de Debug para tu API

## ✅ Resumen de Pruebas

He verificado tu API y **está funcionando correctamente**:

- ✅ `top_k=5` → devuelve 5 resultados
- ✅ `top_k=3` → devuelve 3 resultados
- ✅ `top_k=7` → devuelve 7 resultados
- ✅ `top_k=10` → devuelve 10 resultados

---

## 🎯 Si Tienes un Problema Específico

Por favor usa estas herramientas para debuggear:

### 1. **Debug Tool Interactivo** (Recomendado)

```bash
python3 api_debug_tool.py "tu query aquí" 5
```

Ejemplo:

```bash
python3 api_debug_tool.py "Avatar" 5
python3 api_debug_tool.py "action movies" 10
```

### 2. **Test Exhaustivo de top_k**

```bash
python3 test_response_count.py
```

Prueba automáticamente top_k=1,3,5,10,15 y muestra cuántos resultados devuelve cada uno.

### 3. **Test de Respuesta Completa**

```bash
python3 full_response_test.py
```

Muestra la estructura completa de la respuesta JSON.

---

## 📋 Información que Necesito

**Para poder ayudarte mejor, dime:**

1. **¿Cuál es la query exacta que haces?**

   ```
   Ej: "science fiction", "Avatar", "movies about time travel"
   ```

2. **¿Qué valor de top_k usas?**

   ```
   Ej: 5
   ```

3. **¿Cuántos resultados esperas vs cuántos recibes?**

   ```
   Ej: Espero 5, pero recibo 3
   ```

4. **¿Cómo lo estás probando?**

   ```
   ¿Desde un cliente HTTP (curl/Postman)?
   ¿Desde código Python?
   ¿Desde una app frontend?
   ¿Desde Postman o similar?
   ```

5. **¿Cuál es exactamente la respuesta JSON que recibes?**

---

## 🚀 Ejemplo de Test Manual

```bash
# Con curl
curl -X POST https://api.readyapi.net/api/v1/search/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: rapi_xydaFtQ5nneYdyzA3cAfS1C4bMPLDU2tPqERDrOPxqleypR_j2yIMg" \
  -d '{"query": "science fiction", "top_k": 5}' | python3 -m json.tool
```

Esto te mostrará:

- Cuántos resultados devuelve (contar items en array "results")
- El valor de "total_results"
- Cada título y score

---

## 🐛 Posibles Causas del Problema

1. **No hay suficientes documentos en la BD**
   - Si la BD solo tiene 3 películas y pides 5, recibirás 3 (correcto)

2. **Filtros demasiado restrictivos**
   - Si usas filters que coinciden con 2 docs y pides 5, recibirás 2

3. **Error en el cliente (frontend/app)**
   - El API devuelve 5, pero tu app solo muestra 3

4. **Top_k no se está pasando correctamente**
   - El cliente no está enviando el parámetro top_k

5. **Caché o proxy intermedio**
   - Un proxy está truncando la respuesta

---

**Una vez que me digas cuál es tu problema específico, podré identificar y arreglar el bug exacto.** ✅
