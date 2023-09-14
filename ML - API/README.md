<div align="center">

![wink](https://github.com/claudiacaceresv/pf_yelp_google/blob/24daf1d8afe3d5b2e4d5aa844a48d1b382acd2b5/src/Data%20science.gif)
</div>

## Desarrollo Sistema de Recomendación

<details>
  <summary>Tabla de contenido</summary>
  <ol>
    <li><a href="#Modelo-de-Machine-Learning">Modelo de Machine Learning</a></li>
    <li><a href="#Pipeline">Pipeline</a></li>
    <li><a href="#Tecnologías">Tecnologías Utilizadas</a></li>
    <li><a href="#Data-Warehouse">Data Warehouse</a></li>
    <li><a href="#VertexAI">VertexAI</a></li>
    <li><a href="#Cloud-Storage">Cloud Storage</a></li>
    <li><a href="#Deploy">Deploy</a></li>
  </ol>
</details>

## Modelo de Machine Learning

Se llevó a cabo un ensamble entre un modelo con estructura de red neuronal utilizado para el reconocimiento de palabras (word2vec con su variante CBOW - Continuous Bag of Words), y un modelo simple desarrollado por nosotros, basado en un sistema de puntuación que busca optimizar una suma ponderada para calificar restaurantes. Este sistema asigna ponderación a tres variables: la densidad de cada restaurante, el puntaje promedio otorgado por los usuarios a cada restaurante y el número de reseñas. Para calcular la densidad de cada restaurante, aplicamos el algoritmo Kernel Density Estimation (KDE). En este proceso, iteramos a través de cada restaurante y evaluamos su contribución a la densidad estimada en esa ubicación. Utilizamos una función núcleo (en este caso, kernel gaussiano) alrededor de cada restaurante para calcular esta contribución. A medida que nos alejamos de un restaurante en particular, su influencia disminuye gradualmente. Finalmente, normalizamos la estimación para obtener una función de densidad de probabilidad válida.

- **Funcionamiento:**

  **1. Primer paso: Ingreso de la categoría**
En el primer paso, el usuario introduce la categoría de interés. Por otro lado, el propietario del futuro establecimiento proporciona una categoría clave que desearía tener cerca de su parrilla. En este punto, el sistema de reconocimiento de similitud de palabras busca términos relacionados y, junto con la palabra ingresada por el usuario, genera un listado de restaurantes que cumplen con la característica solicitada.

  **2. Segundo paso: Creación del sistema de puntuación con datos filtrados**
En el segundo paso, procedemos a elaborar el sistema de puntuación utilizando los datos previamente filtrados. Seleccionamos información relevante, que incluye la densidad de cada restaurante, el puntaje promedio otorgado por los usuarios y el número de reseñas recibidas por cada establecimiento. Estas características se ponderan mediante una función de suma ponderada dentro de este subconjunto de datos. Aplicamos el método del descenso del gradiente para ajustar estos valores y, de esta manera, construimos el sistema de puntuación específico para este grupo particular de restaurantes. Finalmente, organizamos estos datos en un orden descendente según las puntuaciones obtenidas.

  **3. Tercer paso: Selección de los restaurantes puntuados por el usuario**
En el tercer paso, el usuario tiene la oportunidad de seleccionar entre los restaurantes que han sido calificados previamente. El propietario del futuro restaurante puede elegir uno de estos restaurantes clasificados en función de sus puntuaciones. Al hacerlo, se despliega una vista que muestra todos los restaurantes cercanos a la elección realizada. Estos restaurantes seleccionados nos brindan la base para elaborar uno de nuestros KPIs. Además, para el usuario, esta selección proporciona información valiosa sobre una zona potencialmente recomendable para ubicar su restaurante. Esto adquiere mayor relevancia en vista de la proximidad del evento mundial, cuando los establecimientos estarán abarrotados y la gente tenderá a preferir los locales mejor calificados y recomendados en principio.

En resumen, este enfoque del modelo combina tanto la información semántica (a través de la similitud de palabras) como la información cuantitativa (densidad, puntaje promedio y cantidad de reseñas) para proporcionar recomendaciones de ubicación fundamentadas en datos sólidos y fácilmente comprensibles.

## Pipeline
Para la creación del sistema de recomendación para el cliente, se siguió el flujo a continuación:

![pipeline](https://github.com/claudiacaceresv/pf_yelp_google/blob/644ab0c390677654af3093b31480ac98af4a15bf/src/Pipeline%20ML.png)

## Tecnologías
![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)
![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
- Big Query
- Cloud Storage
- Cloud Run

## Data Warehouse
Los datos utilizados en el sistema de recomendación fueron extraídos previamente del Data Warehouse, que se conformó durante el proceso de ETL. Para el desarrollo del modelo de machine learning, se tomaron en consideración exclusivamente los datos contenidos en la tabla 'Metadata_ML' del dataset 'GMaps_ML'.

![dwml](https://github.com/claudiacaceresv/pf_yelp_google/blob/644ab0c390677654af3093b31480ac98af4a15bf/src/BigQuery%20ML.png)

## VertexAI
Para el desarrollo del modelo, se empleó un entorno Jupyter Notebook integrado en VertexAI. Desde este entorno, se extrajeron los datos necesarios desde Big Query mediante consultas SQL y se asignaron a un dataframe para su posterior procesamiento con las bibliotecas pandas y scikit-learn. En este contexto, se diseñó un modelo de recomendación para el cliente que permite ingresar la categoría de su establecimiento local. A través de este modelo, el cliente puede identificar los restaurantes líderes que pertenecen a la misma categoría.

El modelo utiliza variables como densidad, puntuación y número de revisiones de los locales para calcular una puntuación ponderada. Esto permite posicionar estratégicamente el restaurante en cuestión. Los resultados de esta ponderación se presentan al cliente a través de un mapa interactivo, ofreciendo una visualización clara y práctica de las recomendaciones. 

[Link al código del Notebook de VertexAI](https://github.com/claudiacaceresv/pf_yelp_google/blob/a9200aa808b91532dd0ed4d2ed1dcbbf25bbe6f2/ML%20-%20API/Modelo-ML.ipynb) 

![vertexai](https://github.com/claudiacaceresv/pf_yelp_google/blob/e927c6eb8847be5f2054b405435f258328d36369/src/Modelo%20ML%20Vertex.png)

## Cloud Storage
El modelo entrenado se exportó de manera directa desde el entorno Workbench de VertexAI a un repositorio en Cloud Storage, listo para su posterior implementación.

![csml](https://github.com/claudiacaceresv/pf_yelp_google/blob/f1d183bcd9955a1ce5b94e2944c02b6e08096f1f/src/Storage%20ML.png)

## Deploy
Para poner a disposición del usuario el sistema de recomendación, se creó una imagen Docker a partir del archivo almacenado en el repositorio de Cloud Storage, junto con el código esencial necesario para alojar una API en FastAPI. Esta API ofrece endpoints que pueden ser consumidos para obtener las recomendaciones proporcionadas por el modelo cada vez que se soliciten.

La imagen Docker resultante se implementó en el servicio Cloud Run, lo que permitió la puesta en línea de la API desarrollada en FastAPI, haciéndola accesible en línea para su utilización.

[Link a la API deployada](https://modelo-machine-learning-p4ruvbt7oq-uc.a.run.app/docs) 

![depdocker](https://github.com/claudiacaceresv/pf_yelp_google/blob/525865d879c5b37a658ccf96925f05124cfa77be/src/Docker%20Hub.jpg)
![depcrun](https://github.com/claudiacaceresv/pf_yelp_google/blob/525865d879c5b37a658ccf96925f05124cfa77be/src/Cloud%20Run.png)
![apiml](https://github.com/claudiacaceresv/pf_yelp_google/blob/525865d879c5b37a658ccf96925f05124cfa77be/src/FastAPI.png)

