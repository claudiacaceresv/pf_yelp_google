import pandas as pd
from sklearn.neighbors import KernelDensity
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy.optimize import minimize
import re
from gensim.models import Word2Vec
import nltk
from geopy.distance import geodesic
from fastapi import FastAPI, HTTPException
import folium
from starlette.responses import FileResponse

app = FastAPI()

# Descargar el recurso 'punkt' para tokenizar o separar palabras
nltk.download('punkt')

# Carga los archivos necesarios y el modelo entrenado
meta_2 = pd.read_csv("Metadata ML.csv")
meta = pd.read_csv("Metadata.csv")
model = Word2Vec.load('modelo_word2vec.bin')
model.wv.vectors = model.wv.vectors.astype('float32')  
model.wv.init_sims(replace=True) 
categorias_existentes = meta['category'].unique()

# Kernel Density Estimation (KDE)
coordenadas = meta[['latitude', 'longitude']].values
kde = KernelDensity(bandwidth=0.01, metric='haversine')
kde.fit(np.radians(coordenadas))
densidades = kde.score_samples(np.radians(coordenadas))
meta['densidad'] = densidades

# Función para obtener restaurantes cercanos
def obtener_restaurantes_cercanos(nombre_lugar):
    restaurantes_cercanos = meta_2.copy()
    latitud_usuario = restaurantes_cercanos[restaurantes_cercanos['local_name'] == nombre_lugar]['latitude'].iloc[0]
    longitud_usuario = restaurantes_cercanos[restaurantes_cercanos['local_name'] == nombre_lugar]['longitude'].iloc[0]
    restaurantes_cercanos['Distancia (m)'] = restaurantes_cercanos.apply(
        lambda row: geodesic((latitud_usuario, longitud_usuario), (row['latitude'], row['longitude'])).meters, axis=1
    )
    distancia_limite_metros = 500
    restaurantes_cercanos = restaurantes_cercanos[(restaurantes_cercanos['Distancia (m)'] <= distancia_limite_metros)]
    restaurantes_cercanos = restaurantes_cercanos.sort_values(by='Distancia (m)')
    return restaurantes_cercanos

@app.post("/categorias/")
def obtener_categorias(palabra: str):
    palabra = re.sub(r'[^\w\s]', '', palabra)
    try:
        # Se buscan las palabras similares 
        palabra_similar, similaridad = model.wv.most_similar(palabra, topn=1)[0]
        categorias_con_palabra_similar = [categoria for categoria in categorias_existentes if palabra_similar in categoria]
        
        # Filtrar nombres de lugares que contienen la palabra literalmente
        lugares_con_palabra = meta[meta['local_name'].str.contains(palabra, case=False)]['local_name'].tolist()
        
        # Combinar ambas listas de nombres de lugares sin duplicados
        nombres_lugares_combinados = list(set(categorias_con_palabra_similar + lugares_con_palabra))
        
        return {"nombres_lugares": nombres_lugares_combinados}
    except KeyError:
        return {"nombres_lugares": []}

@app.post("/restaurantes_cercanos/")
def obtener_restaurantes_cercanos_api(nombre_lugar: str):
    restaurantes_cercanos = obtener_restaurantes_cercanos(nombre_lugar)
    columnas = ["local_name", "category", "Distancia (m)", "latitude", "longitude"]
    
    # Crear un mapa interactivo con Folium
    mapa_restaurantes = folium.Map(location=[restaurantes_cercanos['latitude'].mean(), restaurantes_cercanos['longitude'].mean()], zoom_start=15)
    
    for _, restaurante in restaurantes_cercanos.iterrows():
        folium.Marker(
            location=[restaurante['latitude'], restaurante['longitude']],
            popup=restaurante['local_name']
        ).add_to(mapa_restaurantes)
    
    mapa_restaurantes.save('restaurantes_cercanos_map.html')
    
    return {"restaurantes_cercanos": restaurantes_cercanos[columnas].to_dict(orient="records")}

@app.get("/ver_mapa/")
def ver_mapa():
    return FileResponse("restaurantes_cercanos_map.html")

# uvicorn main:app --reload
