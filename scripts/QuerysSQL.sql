SELECT guid, clase_ifc, nombre, propiedades->'PSet_Revit_Identity Data'->>'Mark' as marca_revit
FROM elementos_bim;

SELECT clase_ifc, COUNT(*) as total_elementos
FROM elementos_bim
GROUP BY clase_ifc
ORDER BY total_elementos DESC;

SELECT 
    nombre,
    propiedades->'PSet_Revit_Mechanical'->>'System Classification' AS clasificacion_sistema,
    propiedades->'PSet_Revit_Type_Identity Data'->>'Manufacturer' AS fabricante,
    propiedades->'PSet_Revit_Type_Identity Data'->>'Model' AS modelo_equipo
FROM elementos_bim
WHERE clase_ifc = 'IfcEnergyConversionDevice'
LIMIT 15;


SELECT *
FROM elementos_bim;


SELECT DISTINCT jsonb_object_keys(propiedades) AS psets_disponibles
FROM elementos_bim
WHERE clase_ifc = 'IfcEnergyConversionDevice';


SELECT 
    nombre,
    propiedades->'PSet_Revit_Type_Identity Data' AS identidad_tipo,
    propiedades->'PSet_Revit_Mechanical - Airflow' AS datos_ventilacion,
    propiedades->'PSet_Revit_Type_Electrical - Loads' AS cargas_electricas
FROM elementos_bim
WHERE clase_ifc = 'IfcEnergyConversionDevice'
LIMIT 1;


SELECT 
    nombre AS identificador_equipo,
    propiedades->'PSet_Revit_Type_Identity Data'->>'OmniClass Title' AS clasificacion_omniclass,
    propiedades->'PSet_Revit_Mechanical - Airflow'->>'Air Flow' AS caudal_aire,
    propiedades->'PSet_Revit_Type_Electrical - Loads' AS cargas_electricas,
    propiedades->'PSet_Revit_Type_Dimensions' AS dimensiones_fisicas
FROM elementos_bim
WHERE clase_ifc = 'IfcEnergyConversionDevice'
LIMIT 200;


SELECT 
    clase_ifc, 
    COUNT(*) as total_elementos
FROM elementos_bim
GROUP BY clase_ifc
ORDER BY total_elementos DESC;


SELECT 
    propiedades->'PSet_Revit_Type_Identity Data'->>'OmniClass Title' AS clasificacion_omniclass,
    COUNT(*) as cantidad
FROM elementos_bim
WHERE clase_ifc IN ('IfcFlowTerminal', 'IfcFlowController')
GROUP BY clasificacion_omniclass
ORDER BY cantidad DESC;


