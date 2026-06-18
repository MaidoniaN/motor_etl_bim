"""
Módulo de Extracción y Transformación (ETL) para Modelos BIM (IFC)
------------------------------------------------------------------
Descripción:
    Este script lee modelos BIM en formato IFC, identifica todos los elementos 
    físicos del modelo, limpia las inconsistencias de nomenclatura generadas por 
    el software de origen (ej. Revit), extrae sus metadatos técnicos (Property Sets) 
    y consolida la información en un archivo JSON estructurado (Staging Area).

Objetivo Técnico:
    Resolver la fragmentación y falta de estandarización en los metadatos de modelos 
    industriales y de especialidades, preparando la data para su inyección en un 
    modelo relacional.
"""

import ifcopenshell
import ifcopenshell.util.element
import urllib.parse
import json
import os

def limpiar_nombre_elemento(nombre_sucio):
    """
    Limpia la fragmentación de texto generada por software de modelado BIM.
    
    El software de diseño (como Revit) a menudo exporta los nombres de los elementos
    concatenando jerarquías, codificando espacios como caracteres web ('%20') y 
    repitiendo la cadena. Esta función normaliza el string.

    Args:
        nombre_sucio (str): El nombre original extraído del archivo IFC.

    Returns:
        str: El nombre comercial/técnico limpio del elemento.
    """
    if not nombre_sucio:
        return "Sin Nombre"
    
    # 1. Decodificar formato URL (transforma '%20' en espacios reales)
    nombre_decodificado = urllib.parse.unquote(nombre_sucio)
    
    # 2. Eliminar redundancias estructurales (ej. corta el string en el primer ':')
    nombre_limpio = nombre_decodificado.split(':')[0]
    
    # 3. Remover sufijos internos de instanciación del software (como '[1]', '[2]')
    nombre_final = nombre_limpio.split('[')[0].strip()
    
    return nombre_final

# ==========================================
# CONFIGURACIÓN DE RUTAS (PIPELINE)
# ==========================================
# Ruta del archivo origen. Se puede alternar entre modelos arquitectónicos, MEP, etc.
# ruta_archivo = "data_input/091210Med_Dent_Clinic_MEP_Plumb.ifc"
# ruta_archivo = "data_input/161210Med_Dent_Clinic_MEP_Mech.ifc"
ruta_archivo = "data_input/091210Med_Dent_Clinic_MEP_Elec.ifc"

# Ruta del archivo destino (Staging Area para la base de datos)
# ruta_salida = "data_output/extraccion_completa.json"
ruta_salida = "data_output/extraccion_completa_Elec.json"

# Crear el directorio de salida de forma segura si no existe en el sistema
os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)

print("--- Iniciando Extracción Masiva (ETL) ---")

try:
    # Cargar el modelo completo en memoria RAM
    modelo = ifcopenshell.open(ruta_archivo)
    
    # Búsqueda global: 'IfcElement' es la superclase normativa que engloba 
    # ABSOLUTAMENTE TODOS los elementos físicos (tuberías, válvulas, equipos, muros, etc.)
    elementos = modelo.by_type("IfcElement")
    
    # Lista principal que almacenará los diccionarios procesados
    datos_totales = []

    print(f"-> Procesando {len(elementos)} elementos físicos. Por favor, espera...")

    # Iteración sobre cada componente físico del modelo industrial
    for elemento in elementos:
        # 1. Armar el esqueleto base de identidad relacional del elemento
        diccionario_elemento = {
            "GlobalId": elemento.GlobalId,          # Identificador único universal (GUID)
            "ClaseIFC": elemento.is_a(),            # Clasificación normativa (ej. IfcEnergyConversionDevice)
            "NombreLimpio": limpiar_nombre_elemento(elemento.Name), # Transformación del string
            "Propiedades": {}                       # Contenedor dinámico para los Property Sets
        }

        # 2. Extracción profunda de metadatos (Property Sets)
        psets = ifcopenshell.util.element.get_psets(elemento)
        
        # Si el elemento posee metadatos técnicos, se procesan
        if psets:
            for pset_nombre, pset_datos in psets.items():
                # Se elimina el 'id' interno de memoria de la librería ifcopenshell,
                # ya que no aporta valor analítico ni de ingeniería al proceso ETL
                if 'id' in pset_datos:
                    del pset_datos['id']
                
                # Se anida el set de propiedades dentro del diccionario principal
                diccionario_elemento["Propiedades"][pset_nombre] = pset_datos
        
        # 3. Añadir el elemento completamente estructurado a la lista total
        datos_totales.append(diccionario_elemento)

    # 4. Fase de Carga a Staging Area (Exportación JSON)
    # Se usa ensure_ascii=False y utf-8 para preservar tildes y caracteres especiales
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        json.dump(datos_totales, f, indent=4, ensure_ascii=False)

    print("\n--- Extracción Completada ---")
    print(f"[OK] Se procesaron {len(elementos)} elementos exitosamente.")
    print(f"[OK] Los datos estructurados fueron exportados a: {ruta_salida}")

except Exception as e:
    # Captura general de errores (archivos corruptos, rutas inválidas, etc.)
    print(f"[ERROR] Hubo un problema crítico al ejecutar la extracción: {e}")