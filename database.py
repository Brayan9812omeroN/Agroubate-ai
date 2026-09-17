"""
database.py
Capa de acceso a datos de AgroUbaté AI, usando sqlite3 (incluido en Python
estándar, sin dependencias externas). Crea el esquema y siembra datos de
ejemplo de la subregión de Ubaté al arrancar la aplicación.
"""

import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "agroubate.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS almacenes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    municipio TEXT NOT NULL,
    telefono TEXT
);

CREATE TABLE IF NOT EXISTS insumos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL,          -- concentrado | sal_mineralizada | medicamento
    unidad TEXT NOT NULL DEFAULT 'bulto 40kg'
);

CREATE TABLE IF NOT EXISTS precios_insumo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insumo_id INTEGER NOT NULL REFERENCES insumos(id),
    almacen_id INTEGER NOT NULL REFERENCES almacenes(id),
    precio REAL NOT NULL,
    fecha_actualizacion TEXT NOT NULL DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS compradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL,          -- acopio | lecheria | industria
    municipio TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS precios_leche (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comprador_id INTEGER NOT NULL REFERENCES compradores(id),
    precio_litro REAL NOT NULL,
    bonificacion REAL NOT NULL DEFAULT 0,
    fecha_actualizacion TEXT NOT NULL DEFAULT (date('now'))
);
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def seed_if_empty():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS n FROM almacenes")
    if cur.fetchone()["n"] > 0:
        conn.close()
        return  # ya hay datos

    almacenes = [
        ("Agroinsumos Ubaté", "Ubaté", "3101234567"),
        ("Almacén Fedegán Villa de San Diego", "Ubaté", "3112345678"),
        ("Agropecuaria Carmen de Carupa", "Carmen de Carupa", "3123456789"),
        ("Insumos del Valle - Sutatausa", "Sutatausa", "3134567890"),
    ]
    cur.executemany(
        "INSERT INTO almacenes (nombre, municipio, telefono) VALUES (?, ?, ?)",
        almacenes,
    )

    insumos = [
        ("Concentrado Lechero 18% Proteína", "concentrado", "bulto 40kg"),
        ("Concentrado Levante Terneras", "concentrado", "bulto 40kg"),
        ("Sal Mineralizada Ganado de Leche", "sal_mineralizada", "bulto 40kg"),
        ("Antiparasitario Ivermectina 1%", "medicamento", "frasco 500ml"),
        ("Vitamina AD3E Inyectable", "medicamento", "frasco 100ml"),
    ]
    cur.executemany(
        "INSERT INTO insumos (nombre, tipo, unidad) VALUES (?, ?, ?)", insumos
    )

    # ids: almacenes 1-4, insumos 1-5 (autoincrement desde una BD vacía)
    precios_insumo = [
        (1, 1, 78000), (1, 2, 76500), (1, 3, 79200), (1, 4, 77800),
        (2, 1, 71000), (2, 2, 72500), (2, 4, 70800),
        (3, 1, 54000), (3, 2, 52500), (3, 3, 55000),
        (4, 2, 23000), (4, 3, 24500), (4, 4, 22800),
        (5, 1, 18500), (5, 3, 19200),
    ]
    cur.executemany(
        "INSERT INTO precios_insumo (insumo_id, almacen_id, precio) VALUES (?, ?, ?)",
        precios_insumo,
    )

    compradores = [
        ("Alpina - Centro de Acopio Ubaté", "industria", "Ubaté"),
        ("Alquería - Ruta Sabana Norte", "industria", "Ubaté"),
        ("Cooperativa Lechera de Carupa", "acopio", "Carmen de Carupa"),
        ("Lechería Local Sutatausa", "lecheria", "Sutatausa"),
    ]
    cur.executemany(
        "INSERT INTO compradores (nombre, tipo, municipio) VALUES (?, ?, ?)",
        compradores,
    )

    precios_leche = [
        (1, 1650, 80),
        (2, 1600, 120),
        (3, 1580, 40),
        (4, 1620, 0),
    ]
    cur.executemany(
        "INSERT INTO precios_leche (comprador_id, precio_litro, bonificacion) VALUES (?, ?, ?)",
        precios_leche,
    )

    conn.commit()
    conn.close()
