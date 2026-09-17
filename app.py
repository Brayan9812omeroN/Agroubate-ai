"""
app.py
Aplicación principal de AgroUbaté AI.

Ejecutar con:  python app.py
Sirve tanto la interfaz web (templates/static) como la API REST.
Usa sqlite3 (estándar de Python) para no requerir dependencias externas
además de Flask.
"""

from flask import Flask, jsonify, request, render_template, abort

from database import init_db, seed_if_empty, get_connection

app = Flask(__name__, static_folder="static", template_folder="templates")

with app.app_context():
    init_db()
    seed_if_empty()


# ---------- Interfaz web ----------
@app.route("/")
def index():
    return render_template("index.html")


# ---------- API: insumos ----------
@app.route("/api/insumos")
def listar_insumos():
    """Lista todos los insumos, opcionalmente filtrados por tipo."""
    tipo = request.args.get("tipo")
    conn = get_connection()
    if tipo:
        filas = conn.execute(
            "SELECT * FROM insumos WHERE tipo = ? ORDER BY nombre", (tipo,)
        ).fetchall()
    else:
        filas = conn.execute("SELECT * FROM insumos ORDER BY nombre").fetchall()
    conn.close()
    return jsonify([dict(f) for f in filas])


@app.route("/api/insumos/<int:insumo_id>/precios")
def comparar_precios_insumo(insumo_id):
    """Compara los precios de un insumo específico entre almacenes,
    ordenados del más barato al más caro."""
    conn = get_connection()
    insumo = conn.execute(
        "SELECT * FROM insumos WHERE id = ?", (insumo_id,)
    ).fetchone()
    if insumo is None:
        conn.close()
        abort(404, description="Insumo no encontrado")

    filas = conn.execute(
        """
        SELECT p.id, p.precio, p.fecha_actualizacion,
               a.id AS almacen_id, a.nombre AS almacen_nombre,
               a.municipio AS almacen_municipio, a.telefono AS almacen_telefono
        FROM precios_insumo p
        JOIN almacenes a ON a.id = p.almacen_id
        WHERE p.insumo_id = ?
        ORDER BY p.precio ASC
        """,
        (insumo_id,),
    ).fetchall()
    conn.close()

    comparacion = [
        {
            "id": f["id"],
            "precio": f["precio"],
            "fecha_actualizacion": f["fecha_actualizacion"],
            "almacen": {
                "id": f["almacen_id"],
                "nombre": f["almacen_nombre"],
                "municipio": f["almacen_municipio"],
                "telefono": f["almacen_telefono"],
            },
        }
        for f in filas
    ]

    return jsonify(
        {
            "insumo": dict(insumo),
            "comparacion": comparacion,
            "mejor_precio": comparacion[0] if comparacion else None,
        }
    )


@app.route("/api/almacenes")
def listar_almacenes():
    conn = get_connection()
    filas = conn.execute("SELECT * FROM almacenes ORDER BY nombre").fetchall()
    conn.close()
    return jsonify([dict(f) for f in filas])


# ---------- API: leche ----------
def _obtener_precios_leche():
    conn = get_connection()
    filas = conn.execute(
        """
        SELECT p.id, p.precio_litro, p.bonificacion, p.fecha_actualizacion,
               c.id AS comprador_id, c.nombre AS comprador_nombre,
               c.tipo AS comprador_tipo, c.municipio AS comprador_municipio
        FROM precios_leche p
        JOIN compradores c ON c.id = p.comprador_id
        """
    ).fetchall()
    conn.close()

    resultado = []
    for f in filas:
        precio_total = round(f["precio_litro"] + f["bonificacion"], 2)
        resultado.append(
            {
                "id": f["id"],
                "precio_litro": f["precio_litro"],
                "bonificacion": f["bonificacion"],
                "precio_total": precio_total,
                "fecha_actualizacion": f["fecha_actualizacion"],
                "comprador": {
                    "id": f["comprador_id"],
                    "nombre": f["comprador_nombre"],
                    "tipo": f["comprador_tipo"],
                    "municipio": f["comprador_municipio"],
                },
            }
        )
    resultado.sort(key=lambda p: p["precio_total"], reverse=True)
    return resultado


@app.route("/api/leche/compradores")
def listar_precios_leche():
    """Lista todos los compradores de leche con su precio total
    (precio base + bonificación), ordenados de mayor a menor."""
    return jsonify(_obtener_precios_leche())


@app.route("/api/leche/mejor-precio")
def mejor_precio_leche():
    """Devuelve el comprador que ofrece el mejor precio total por litro."""
    precios = _obtener_precios_leche()
    if not precios:
        return jsonify({"mensaje": "Aún no hay precios de leche registrados."}), 404
    return jsonify(precios[0])


# ---------- Salud del servicio ----------
@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "servicio": "AgroUbaté AI"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
