# Databricks notebook source
from pyspark.sql.types import *
import pyspark.sql.functions as F
from pyspark.sql.functions import *

# COMMAND ----------

# ruta de los folder
temporal_path  = "dbfs:/mnt/conjuntodedatos/temporal"
bronze_path  = "dbfs:/mnt/conjuntodedatos/bronze"
silver_path  = "dbfs:/mnt/conjuntodedatos/silver"
gold_path  = "dbfs:/mnt/conjuntodedatos/gold"

# COMMAND ----------

# MAGIC %md
# MAGIC ### transformar poblacion
# MAGIC

# COMMAND ----------

# cargo poblacion de bronze
poblacion = spark.read.format("delta").load(f"{bronze_path}/poblacion")
display(poblacion)

# COMMAND ----------

# Agregar una columna id autoincremental
poblacion = poblacion.withColumn("Id_Estado", monotonically_increasing_id())
# Ajustar los valores para iniciar en 1 en lugar de 0
poblacion = poblacion.withColumn("Id_Estado", expr("Id_Estado + 1"))
poblacion.show()


# COMMAND ----------

# Obtener los valores únicos de los estado
poblacion.select("Nombre_Estado").distinct().rdd.map(lambda x: x[0]).collect()

# COMMAND ----------

# Eliminar registros donde "Nombre_Estado" sea igual a "Puerto Rico"
poblacion = poblacion.filter(poblacion["Nombre_Estado"] != "Puerto Rico")

# COMMAND ----------

# Reorganizar las columnas
poblacion = poblacion.select("Id_Estado", "Nombre_Estado", "Total_Poblacion", "Categoria_Densidad")
# Mostrar el DataFrame resultante
poblacion.show(5)

# COMMAND ----------

# guardo en silver
poblacion.write.mode("overwrite").format("delta").save(f"{silver_path}/estados")

# COMMAND ----------

# cargo estados de silver
estados = spark.read.format("delta").load(f"{silver_path}/estados")
display(estados)

# COMMAND ----------

# MAGIC %md
# MAGIC ### transformar franquicias

# COMMAND ----------

# cargo franquicias de bronze
franquicias = spark.read.format("delta").load(f"{bronze_path}/franquicias")
display(franquicias)

# COMMAND ----------

# Contar registros duplicados
duplicados = franquicias.groupBy(*franquicias.columns).count().filter("count > 1")
# Mostrar la cantidad de registros duplicados
duplicados.count()

# COMMAND ----------

# Eliminar duplicados
franquicias = franquicias.dropDuplicates()

# COMMAND ----------

# Agregar una columna id autoincremental
franquicias = franquicias.withColumn("Id_Franquicia", monotonically_increasing_id())
# Ajustar los valores para iniciar en 1 en lugar de 0
franquicias = franquicias.withColumn("Id_Franquicia", expr("Id_Franquicia + 1"))
franquicias.show(3)

# COMMAND ----------

# Reorganizar las columnas
franquicias = franquicias.select('Id_Franquicia', 'Nombre_Franquicia', 'Min_Inversion', 'Max_Inversion', 'Año_Fundado','Unidades')
# Mostrar el DataFrame resultante
franquicias.show(5)

# COMMAND ----------

# guardo en silver
franquicias.write.mode("overwrite").format("delta").save(f"{silver_path}/franquicias")

# COMMAND ----------

# cargo franquicias de silver
franquicias = spark.read.format("delta").load(f"{silver_path}/franquicias")
display(franquicias)

# COMMAND ----------

# MAGIC %md
# MAGIC ### transformar google

# COMMAND ----------

# cargo google de bronze
google = spark.read.format("delta").load(f"{bronze_path}/google")
display(google)

# COMMAND ----------

# Eliminar una columna
google = google.drop("Unnamed")
google.show(3)

# COMMAND ----------

# Obtener los valores únicos de los estado
google.select("Nombre_Estado").distinct().rdd.map(lambda x: x[0]).collect()

# COMMAND ----------

# Reemplazar guiones bajos por espacios en la columna "Nombre_Estado"
google = google.withColumn("Nombre_Estado", regexp_replace("Nombre_Estado", "_", " "))

# COMMAND ----------

# Unir los DataFrames en función de la columna "Nombre_Estado"
google = google.join(estados, on="Nombre_Estado", how="left")
display(google)

# COMMAND ----------

# Agregar una columna id autoincremental
google = google.withColumn("Id_Local", monotonically_increasing_id())
# Ajustar los valores para iniciar en 1 en lugar de 0
google = google.withColumn("Id_Local", expr("Id_Local + 1"))
google.show(3)

# COMMAND ----------

# Reorganizar las columnas
google = google.select('Id_Local', 'Nombre_Franquicia', 'Latitud', 'Longitud', 'Categoria','Promedio_Rating','Cantidad_Reviews','Id_Estado', 'Nombre_Estado')
# Mostrar el DataFrame resultante
display(google)

# COMMAND ----------

# guardo en silver
google.write.mode("overwrite").format("delta").save(f"{silver_path}/google")

# COMMAND ----------

# cargo google de silver
google = spark.read.format("delta").load(f"{silver_path}/google")
display(google)

# COMMAND ----------

# MAGIC %md
# MAGIC ### transformar yelp

# COMMAND ----------

# cargo yelp de bronze
yelp = spark.read.format("delta").load(f"{bronze_path}/yelp")
yelp.show(3)

# COMMAND ----------

# Eliminar una columna
yelp = yelp.drop("Unnamed")
yelp.show(3)

# COMMAND ----------

# Eliminar filas con valores faltantes
yelp = yelp.dropna(how="any")

# COMMAND ----------

# Reorganizar las columnas
yelp = yelp.select('Latitud', 'Longitud', 'Comentario')
# Mostrar el DataFrame resultante
display(yelp)

# COMMAND ----------

# Eliminar duplicados
yelp = yelp.dropDuplicates()

# COMMAND ----------

# guardo en silver
yelp.write.mode("overwrite").format("delta").save(f"{silver_path}/yelp")

# COMMAND ----------

# cargo yelp de silver
yelp = spark.read.format("delta").load(f"{silver_path}/yelp")
display(yelp)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Reviews (dataset final)

# COMMAND ----------

# Unir los DataFrames en función de las columnas "Latitud" y "Longitud"
Reviews = google.join(yelp, on=["Latitud", "Longitud"], how="left")
display(Reviews)

# COMMAND ----------

# Cambiar el nombre de la columna "Id_Local" a "Id_Reviews"
Reviews = Reviews.withColumnRenamed("Id_Local", "Id_Reviews")
Reviews.show(3)

# COMMAND ----------

# Reemplazar valores nulos en la columna "Comentario" por "sin comentario"
Reviews = Reviews.withColumn("Comentario", when(col("Comentario").isNull(), "sin comentario").otherwise(col("Comentario")))
# Mostrar el DataFrame resultante
display(Reviews)

# COMMAND ----------

# Reorganizar las columnas
Reviews = Reviews.select('Id_Reviews', 'Nombre_Franquicia', 'Latitud', 'Longitud', 'Categoria','Promedio_Rating','Cantidad_Reviews', 'Comentario', 'Id_Estado', 'Nombre_Estado')
# Mostrar el DataFrame resultante
display(Reviews)

# COMMAND ----------

# Crear una nueva columna "Id_Estado" relacionada con el DataFrame "franquicias"
Reviews = Reviews.join(franquicias.select("Nombre_Franquicia", "Id_Franquicia"), on="Nombre_Franquicia", how="left")
# Mostrar el DataFrame resultante
display(Reviews)

# COMMAND ----------

# Reorganizar las columnas
Reviews = Reviews.select('Id_Reviews', 'Nombre_Franquicia', 'Latitud', 'Longitud', 'Categoria','Promedio_Rating','Cantidad_Reviews', 'Comentario', 'Id_Estado', 'Nombre_Estado','Id_Franquicia')
# Mostrar el DataFrame resultante
display(Reviews)

# COMMAND ----------

# guardo en silver
Reviews.write.mode("overwrite").format("delta").save(f"{silver_path}/Reviews")

# COMMAND ----------

# cargo Reviews de silver
Reviews = spark.read.format("delta").load(f"{silver_path}/Reviews")
display(Reviews)

# COMMAND ----------

# MAGIC %md
# MAGIC ### dividir dataframe (guardar en gold)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Reviews

# COMMAND ----------

# Reviews
# Obtén el número total de filas
total_filas = Reviews.count()

# Calcula la mitad del número total de filas
mitad_filas = total_filas // 2

# Divide el DataFrame en dos partes iguales
Reviews_1, Reviews_2 = Reviews.randomSplit([0.5, 0.5], seed=42)

# COMMAND ----------

# guardo en gold
#Reviews_1.write.mode("overwrite").csv(f"{gold_path}/Reviews_1")
Reviews_1.write.mode("overwrite").format("delta").save(f"{gold_path}/Reviews_1")
Reviews_2.write.mode("overwrite").format("delta").save(f"{gold_path}/Reviews_2")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Estados

# COMMAND ----------

# estados
# Obtén el número total de filas
total_filas = estados.count()

# Calcula la mitad del número total de filas
mitad_filas = total_filas // 2

# Divide el DataFrame en dos partes iguales
estados_1, estados_2 = estados.randomSplit([0.5, 0.5], seed=42)

# COMMAND ----------

# guardo en gold
#estados_1.write.mode("overwrite").csv(f"{gold_path}/estados_1")
estados_1.write.mode("overwrite").format("delta").save(f"{gold_path}/estados_1")
estados_2.write.mode("overwrite").format("delta").save(f"{gold_path}/estados_2")

# COMMAND ----------

# MAGIC %md
# MAGIC #### franquicias

# COMMAND ----------

# franquicias
# Obtén el número total de filas
total_filas = franquicias.count()

# Calcula la mitad del número total de filas
mitad_filas = total_filas // 2

# Divide el DataFrame en dos partes iguales
franquicias_1, franquicias_2 = franquicias.randomSplit([0.5, 0.5], seed=42)

# COMMAND ----------

# guardo en gold
#franquicias_1.write.mode("overwrite").csv(f"{gold_path}/franquicias_1")
franquicias_1.write.mode("overwrite").format("delta").save(f"{gold_path}/franquicias_1")
franquicias_2.write.mode("overwrite").format("delta").save(f"{gold_path}/franquicias_2")
