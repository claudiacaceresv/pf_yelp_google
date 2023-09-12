# ETL data de Google Places API 

## Indice

<details>
  <summary>Tabla de contenido</summary>
  <ol>
    <li><a href="#Pipeline">Pipeline</a></li>
    <li><a href="#Tecnologías">Tecnologías Utilizadas</a></li>
    <li><a href="#Extracción de datos con Cloud Functions">Extracción de datos con Cloud Functions</a></li>
    <li><a href="#Data Lake">Data Lake</a></li>
    <li><a href="#ETL automatizado con Cloud Functions">ETL automatizado con Cloud Functions</a></li>
    <li><a href="#Data Warehouse">Data Warehouse</a></li>
    <li><a href="#Video">Video</a></li>
  </ol>
</details>

## Pipeline 
Como una segunda fuente de datos, se extrajeron los datos de los restaurantes de Miami, para esto se siguió el flujo a continuación:

![pipeline](https://github.com/claudiacaceresv/pf_yelp_google/blob/9e3091720adf4532c8996f0cbbd8c48bab716e92/src/Pipeline%20API.png)

## Tecnologías
![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=for-the-badge&logo=google-cloud&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)
- Cloud Functions
- Cloud Storage
- Big Query
- Cloud Scheduler

## Automatización de la Extracción de Datos
A través de Cloud Scheduler, programamos una tarea que ejecuta una función diariamente para extraer información de la API y almacenarla en BigQuery. Esto simplifica los procesos de recopilación de datos con estas soluciones eficientes y confiables.

![schedulerapidata](https://github.com/claudiacaceresv/pf_yelp_google/blob/ecae7e03590019bb0db5c0c61810e27e209499cb/src/Cloud%20Scheduler.png)

## Extracción de datos con Cloud Functions
Para extraer los datos, se creó una función en Cloud Functions (API-Place-Google) que por medio de una API Key, extrae los datos directamente desde la API de Google Places y almacena la información en BigQuery cada vez que se ejecuta la función.

![getapidata](https://github.com/claudiacaceresv/pf_yelp_google/blob/ecae7e03590019bb0db5c0c61810e27e209499cb/src/Cloud%20Functions%20API.png)

## Data Warehouse
El proceso de ETL devuelve una tabla llamada "Metadata", que se almacena en el Data Warehouse en Big Query dentro de un schema llamado "API_Google_Place", del cual se puede extraer la información con consultas SQL y conectándose al cliente de Big Query.

![bigqueryapi](https://github.com/claudiacaceresv/pf_yelp_google/blob/ecae7e03590019bb0db5c0c61810e27e209499cb/src/BigQuery%20API.png)

## Video

En el siguiente video, podrás presenciar la tarea programada en Cloud Scheduler, la cual se ejecuta de manera diaria para extraer datos de la API de Google. Como resultado de este proceso, los datos son almacenados en nuestro Data Warehouse.

<div align="center">

![wink](https://github.com/claudiacaceresv/pf_yelp_google/blob/ecae7e03590019bb0db5c0c61810e27e209499cb/src/Video%20ETL%20API.gif)

</div>

