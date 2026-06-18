"1. Extracción híbrida básica (Relacional + JSONB)
Explicación: Esta es una consulta de lectura directa que mezcla los dos mundos de tu arquitectura. Selecciona columnas relacionales clásicas (el identificador único guid, la clase IFC y el nombre) y usa la doble flecha ->> para navegar dentro de la columna JSONB propiedades, extraer el valor exacto de la "Marca" (Mark) de Revit y presentarlo como una columna de texto limpio llamada marca_revit.

SQL"
SELECT guid, clase_ifc, nombre, propiedades->'PSet_Revit_Identity Data'->>'Mark' as marca_revit
FROM elementos_bim;


"2. Inventario macro del modelo (Agrupación)
Explicación: Esta consulta actúa como una radiografía general del archivo BIM. Agrupa todos los elementos físicos según su categoría normativa (clase_ifc) y cuenta cuántos elementos existen por cada categoría, ordenándolos de mayor a menor. Es fundamental para saber rápidamente a qué disciplina te estás enfrentando (ej. si predominan ductos, luminarias o tuberías).

SQL"
SELECT clase_ifc, COUNT(*) as total_elementos
FROM elementos_bim
GROUP BY clase_ifc
ORDER BY total_elementos DESC;

"3. Escaneo de metadatos comerciales y de sistema
Explicación: Aquí filtramos la base de datos para ver exclusivamente los equipos mecánicos pesados (IfcEnergyConversionDevice). El objetivo es bucear en los diccionarios internos de Revit para extraer como texto plano (->>) el fabricante, el modelo y la clasificación del sistema. El LIMIT 15 se usa para no saturar la consola si el modelo llega a tener miles de equipos, trayendo solo una muestra rápida.

SQL"
SELECT 
    nombre,
    propiedades->'PSet_Revit_Mechanical'->>'System Classification' AS clasificacion_sistema,
    propiedades->'PSet_Revit_Type_Identity Data'->>'Manufacturer' AS fabricante,
    propiedades->'PSet_Revit_Type_Identity Data'->>'Model' AS modelo_equipo
FROM elementos_bim
WHERE clase_ifc = 'IfcEnergyConversionDevice'
LIMIT 15;


"4. Volcado completo (Raw Data)
Explicación: Es la consulta más básica en SQL. Trae absolutamente todas las columnas y todas las filas de la tabla. Aunque es útil para revisar que los datos se inyectaron, en entornos de producción con archivos grandes (como modelos mineros) se debe usar con precaución o acompañar de un LIMIT, ya que traerá a la pantalla miles de JSONs completos.

SQL"
SELECT *
FROM elementos_bim;


"5. Auditoría estructural (Descubrimiento de llaves)
Explicación: Esta es una consulta de diagnóstico avanzado. Usa la función nativa jsonb_object_keys para preguntarle a PostgreSQL: "¿Cuáles son los nombres exactos de los contenedores (PSets) que existen dentro de esta clase de equipos?". El DISTINCT garantiza que entregue una lista limpia sin repetir nombres, permitiéndote saber dónde buscar los parámetros si el modelador usó una taxonomía extraña.

SQL"
SELECT DISTINCT jsonb_object_keys(propiedades) AS psets_disponibles
FROM elementos_bim
WHERE clase_ifc = 'IfcEnergyConversionDevice';


"6. Extracción de contenedores completos (Flecha simple)
Explicación: A diferencia de las consultas anteriores que sacaban un texto específico, esta utiliza la flecha simple ->. Esto significa que en lugar de un texto, extrae el bloque JSON completo de dimensiones, ventilación o cargas eléctricas. Es ideal cuando sabes que el contenedor existe, pero quieres ver en bruto todas las llaves (keys) y valores (values) que el proyectista dejó allí dentro para un solo equipo (LIMIT 1).

SQL"
SELECT 
    nombre,
    propiedades->'PSet_Revit_Type_Identity Data' AS identidad_tipo,
    propiedades->'PSet_Revit_Mechanical - Airflow' AS datos_ventilacion,
    propiedades->'PSet_Revit_Type_Electrical - Loads' AS cargas_electricas
FROM elementos_bim
WHERE clase_ifc = 'IfcEnergyConversionDevice'
LIMIT 1;


"7. Extracción de ingeniería de detalles (Mixta)
Explicación: Esta consulta genera el "entregable" final de ingeniería. Extrae parámetros exactos como texto (->>) para la clasificación y el flujo de aire, pero mantiene en formato estructurado JSON (->) los bloques eléctricos y dimensionales completos. Toma una muestra más robusta (LIMIT 200) de los equipos pesados para comparar variabilidades paramétricas.

SQL"
SELECT 
    nombre AS identificador_equipo,
    propiedades->'PSet_Revit_Type_Identity Data'->>'OmniClass Title' AS clasificacion_omniclass,
    propiedades->'PSet_Revit_Mechanical - Airflow'->>'Air Flow' AS caudal_aire,
    propiedades->'PSet_Revit_Type_Electrical - Loads' AS cargas_electricas,
    propiedades->'PSet_Revit_Type_Dimensions' AS dimensiones_fisicas
FROM elementos_bim
WHERE clase_ifc = 'IfcEnergyConversionDevice'
LIMIT 200;


"8. Inventario macro del modelo (Repetición)
Explicación: Esta consulta es idéntica a la número 2. Sirve para auditar la volumetría total del modelo antes y después de inyectar un nuevo archivo IFC para verificar que la carga (UPSERT) no haya duplicado ni perdido componentes físicos.

SQL"
SELECT 
    clase_ifc, 
    COUNT(*) as total_elementos
FROM elementos_bim
GROUP BY clase_ifc
ORDER BY total_elementos DESC;


"9. Agrupación profunda (Indexación NoSQL)
Explicación: Esta es una de las demostraciones más potentes de tu base de datos híbrida. No está agrupando los elementos por una columna relacional tradicional, sino que está entrando a lo profundo del JSONB (->> 'OmniClass Title') y agrupando y contando los equipos eléctricos y terminales basándose en ese texto interno. Demuestra que PostgreSQL puede tratar la data semiestructurada con la misma eficiencia matemática que la data plana.

SQL"
SELECT 
    propiedades->'PSet_Revit_Type_Identity Data'->>'OmniClass Title' AS clasificacion_omniclass,
    COUNT(*) as cantidad
FROM elementos_bim
WHERE clase_ifc IN ('IfcFlowTerminal', 'IfcFlowController')
GROUP BY clasificacion_omniclass
ORDER BY cantidad DESC;