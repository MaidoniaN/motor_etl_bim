import ifcopenshell
import psycopg2
import sys

def test_environment():
    print("--- Iniciando Prueba de Humo del Motor ETL ---")
    
    # 1. Prueba de extracción (IfcOpenShell)
    try:
        print(f"[OK] IfcOpenShell importado correctamente. Versión: {ifcopenshell.version}")
    except Exception as e:
        print(f"[ERROR] Fallo al cargar IfcOpenShell: {e}")
        sys.exit(1)

    # 2. Prueba de persistencia (PostgreSQL)
    try:
        conn = psycopg2.connect(
            dbname="bim_integration_db",
            user="etl_admin",
            password="aaCR1981#", # Actualiza esta línea
            host="localhost",
            port="5432"
        )
        print("[OK] Conexión a PostgreSQL (bim_integration_db) establecida con éxito.")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Fallo al conectar con PostgreSQL: {e}")
        sys.exit(1)

    print("--- ¡Infraestructura Fundacional 100% Operativa! ---")

if __name__ == "__main__":
    test_environment()
