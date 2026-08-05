"""
Módulo de Carga (Load - L) del Pipeline ETL para Integración BIM
------------------------------------------------------------------
Descripción:
    Este script implementa la fase de carga masiva en el pipeline de datos.
    Lee el archivo JSON de la zona de Staging, establece una conexión segura
    con PostgreSQL e inyecta los registros en la tabla 'elementos_bim' utilizando
    una estrategia híbrida (campos relacionales estructurados + datos semiestructurados JSONB).

Objetivo Técnico:
    Garantizar la persistencia, la idempotencia de los datos (evitando duplicados)
    y mantener la integridad transaccional (propiedades ACID) durante el proceso
    de inyección de metadatos masivos.
"""

import json
import psycopg2
from psycopg2.extras import Json  # Wrapper crítico para mapear diccionarios a JSONB de PostgreSQL
import os

# ==========================================
# CONFIGURACIÓN DE CONEXIÓN (INFRAESTRUCTURA)
# ==========================================
# NOTA DE SEGURIDAD: Para despliegues productivos, se recomienda migrar estas 
# credenciales a variables de entorno (.env) para proteger el acceso.
DB_CONFIG = {
    "dbname": "bim_integration_db",
    "user": "etl_admin",
    "password": "aaCR1981#",  
    "host": "localhost",
    "port": 5432
}

# Definición de rutas del ecosistema de datos
# ruta_json = "data_output/extraccion_completa.json"
ruta_json = "data_output/extraccion_completa_Elec.json"

print("--- Iniciando Fase de Carga (L) en PostgreSQL ---")

# Validar la existencia del dataset transformado antes de levantar servicios de BD
if not os.path.exists(ruta_json):
    print(f"[ERROR] No se encontró el archivo de Staging: {ruta_json}. Corre primero el explorador.")
    exit()

try:
    # 1. Extracción desde la zona de Staging (Lectura del JSON local)
    with open(ruta_json, 'r', encoding='utf-8') as f:
        elementos = json.load(f)
    print(f"-> Archivo JSON cargado. Se preparan {len(elementos)} registros para inyección.")

    # 2. Conexión a la capa de persistencia (PostgreSQL)
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()  # Abre el cursor para ejecutar operaciones de base de datos
    print("[OK] Conexión establecida con bim_integration_db.")

    # 3. Definición de la estrategia de inserción (Query SQL con lógica UPSERT)
    # El uso de 'ON CONFLICT (guid) DO UPDATE' asegura la idempotencia del pipeline:
    # Si el elemento ya existe (mismo GUID), actualiza sus datos en lugar de fallar,
    # permitiendo reejecutar el script de forma segura (Data Pipeline Resiliency).
    query_insert = """
        INSERT INTO elementos_bim (guid, clase_ifc, nombre, propiedades)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (guid) 
        DO UPDATE SET 
            clase_ifc = EXCLUDED.clase_ifc,
            nombre = EXCLUDED.nombre,
            propiedades = EXCLUDED.propiedades;
    """

    registros_cargados = 0
    
    # Iteración y mapeo de tipos de datos nativos a SQL
    for el in elementos:
        # Se ejecuta la inserción parametrizada para prevenir ataques de inyección SQL.
        # El método Json() serializa de forma transparente el diccionario de Python
        # al formato binario optimizado JSONB de PostgreSQL.
        cursor.execute(query_insert, (
            el["GlobalId"],
            el["ClaseIFC"],
            el["NombreLimpio"],
            Json(el["Propiedades"])
        ))
        registros_cargados += 1

    # 4. Confirmación de Transacción (Capa de Consistencia ACID)
    # Todos los registros se envían en un solo bloque transaccional. Si un solo elemento
    # falla de forma catastrófica antes de esta línea, nada se escribe en la base de datos.
    conn.commit()
    
    print("\n--- Pipeline ETL Finalizado con Éxito ---")
    print(f"[OK] Se cargaron {registros_cargados} registros en la tabla 'elementos_bim'.")

except Exception as e:
    # Control de fallos y Rollback automático
    print(f"[ERROR] Hubo un problema crítico durante la carga: {e}")
    # Si la conexión alcanzó a inicializarse, se revierte la transacción para evitar estados corruptos
    if 'conn' in locals():
        print("[INFO] Ejecutando Rollback transaccional debido a falla...")
        conn.rollback()

finally:
    # 5. Gestión del ciclo de vida de los recursos (Liberación de memoria y sockets)
    # Garantiza el cierre de punteros y conexiones incluso si el script falla en el camino
    if 'cursor' in locals(): 
        cursor.close()
    if 'conn' in locals(): 
        conn.close()
    print("[INFO] Recursos de base de datos liberados correctamente.")