import pandas as pd
from pandas.io import gbq
from google.cloud import bigquery
import functions_framework
import json
import pickle

def hello_gcs(event, context):
    try:
        """Triggered by a change to a Cloud Storage bucket.
        Args:
             event (dict): Event payload.
             context (google.cloud.functions.Context): Metadata for the event.
        """

        food_service= ['restaurant','gastropubs', "grill"]

        def modify_category_column(data):
            categories_to_find = [
                "Mexican restaurant",
                "Pizza restaurant",
                "American restaurant",
                "Bar & grill",
                "Seafood restaurant",
                "Italian restaurant",
                "Barbecue restaurant",
                "Fast food restaurant",
                "Cuban restaurant",
                "Chinese restaurant",
                "Japanese restaurant"
            ]

            def replace_category(category):
                # Verificar si la categoría contiene "Restaurant" y no está en la lista prohibida
                if 'Restaurant' in category and category not in categories_to_find:
                    return 'Restaurant'
                else:
                    return category

            # Aplicar la función replace_category a la columna 'category'
            data['category'] = data['category'].apply(replace_category)
            
            # Crear una máscara booleana para cada fila que indica si alguna categoría coincide
            mask = data['category'].apply(lambda x: any(category in x for category in categories_to_find))

            # Actualizar la columna 'category' con la categoría encontrada
            data.loc[mask, 'category'] = data.loc[mask, 'category'].apply(lambda x: next(category for category in categories_to_find if category in x))
            
            # Filtrar el DataFrame solo por registros en categories_to_find o que contienen "Restaurant"
            data = data[data['category'].isin(categories_to_find) | data['category'].str.contains('Restaurant')]
            
            return data


        def json_normalize_misc(data):
            # Realizar la normalización JSON en la columna 'MISC'
            misc = pd.json_normalize(data['MISC'])

            if 'Payments' in misc.columns:
            
                # Modificar la columna 'solo_efectivo' para asignar 1 si 'Cash only' está presente en la lista, 0 en caso contrario
                misc['solo_efectivo'] = misc['Payments'].apply(lambda x: 1 if isinstance(x, list) and 'Cash-only' in x else 0)

                # Eliminar la columna 'Payments' del DataFrame resultante
                misc = misc.drop(columns=['Payments'])

            
            # Renombrar las columnas especificadas
            misc = misc.rename(columns={
                'Accessibility': 'apto_sillas_de_ruedas',
                'Atmosphere': 'atmosfera_agradable',
                'Crowd': 'apto_grupos_grandes'
            })
                
            columnas_a_reemplazar = ["apto_sillas_de_ruedas", "atmosfera_agradable", "apto_grupos_grandes"]
            
            for columna in columnas_a_reemplazar:
                misc[columna] = misc[columna].notna().astype(int)
            
            
            # Concatenar el DataFrame original "data" con el DataFrame "misc"
            data = pd.concat([data, misc], axis=1)

            # Eliminar las columnas que deseas después de la concatenación
            columnas_a_eliminar = ["MISC", "Service options", "Health & safety", "Planning", "Offerings", 
                           "Amenities", "Popular for", "Dining options", "From the business", "Highlights", 
                           "Recycling", "Getting here", "Activities"]

            # Verificar si las columnas existen antes de intentar eliminarlas
            if 'Lodging options' in data.columns:
                columnas_a_eliminar.append('Lodging options')

            if 'Health and safety' in data.columns:
                columnas_a_eliminar.append('Health and safety')
    
            data = data.drop(columns=columnas_a_eliminar)
            
            # Devolver el DataFrame "data" concatenado
            return data
        


        # Obteniendo ruta de archivo modificado y tipo de archivo
        file_name = event['name']
        file_type = file_name.split('.')[-1]

        if '/' in file_name:
            main_folder = file_name.split('/')[0]
            last_folder = file_name.split('/')[file_name.count('/')-1]

            if main_folder == 'GMaps':
                dataset = 'GMaps.'
                if file_name.split('/')[1] == 'reviews-estados':
                    table_name = 'Reviews'
                    state = last_folder.split('-')[-1]
                if file_name.split('/')[1] == 'metadata-sitios':
                    table_name = 'Metadata'

            if main_folder == 'Yelp':
                dataset = 'Yelp.'
                if last_folder == 'review':
                    table_name = 'Reviews'
                elif last_folder=='user':
                    table_name= 'Users'
                else:
                    table_name = file_name.split('.')[0].split('/')[1]
        
            if main_folder == 'GMaps-ML':
                dataset = 'GMaps_ML.'
                if file_name.split('/')[1] == 'metadata-sitios-ML':
                    table_name = 'Metadata_ML'



            # Revisando si archivo es csv
            if file_type == 'csv':
                # Leyendo archivo en dataframe
                data = pd.read_csv('gs://' + event['bucket'] + '/' + file_name)

            # Revisando si archivo es json    
            if file_type == 'json':
                try:
                    # Intentar leer el archivo json como si no tuviera saltos de linea
                    data = pd.read_json('gs://' + event['bucket'] + '/' + file_name)
                except ValueError as e:
                    if 'Trailing data' in str(e):
                        # Leer el archivo json conteniendo saltos de linea
                        data = pd.read_json('gs://' + event['bucket'] + '/' + file_name, lines = True)
                    else:
                        # Cualquier otro error
                        print('Ocurrió un error cargando el archivo JSON:', e)

            # Revisar si el archivo es tipo parquet
            if file_type == 'parquet':
                # Leyendo archivo en dataframe
                data = pd.read_parquet('gs://' + event['bucket'] + '/' + file_name)

            # Revisar si el archivo es tipo pkl (Pickle)
            if file_type == 'pkl':
                try:
                    # Leyendo archivo en DataFrame desde Google Cloud Storage
                    data = pd.read_pickle('gs://' + event['bucket'] + '/' + file_name)
                except Exception as e:
                    print(f'Ocurrió un error al leer el archivo Pickle: {e}')

            # Google Maps
            if main_folder == 'GMaps':
                if 'review' in last_folder:
                    data.drop(columns=["user_id","name","pics"],inplace=True)  
                    data.rename(columns={'text':'opinion', 'time':'date'}, inplace=True)
                    data['date'] = pd.to_datetime(data['date'], unit='ms').dt.strftime('%Y-%m-%d')
                    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
                    data = data[data['date'].dt.year >= 2019] #pendiente definir desde que año se va a tomar la data
                    data = data.applymap(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)
                    data.drop_duplicates(inplace=True)
                    data.reset_index(drop=True,inplace=True)

                    if state == 'Florida':
                        data['state'] = 'FL'
            

                if last_folder == 'metadata-sitios':

                    # Aplicar la función json_normalize_misc
                    data = json_normalize_misc(data)

                    data.drop(columns=['relative_results', 'url', 'description', 'price', 'hours', 'state'], inplace=True)
                    data.rename(columns={'name': 'local_name'}, inplace=True)
                    data.dropna(subset=['category'], inplace=True)
                    data.dropna()
                    data['category'] = data['category'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
                    data = data.applymap(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)
                    data.drop_duplicates(inplace=True)
                    data['state'] = data['address'].str.extract(r'(FL)')
                    data = data[data['state'] == 'FL']
                    data['City'] = data['address'].str.split(',').str[2:3].str.join(', ').str.strip()
                    data = data[data['City'] == 'Miami']
                    data[(data['latitude'] >= 25) & (data['latitude'] <= 25.99)]
                    data.reset_index(drop=True, inplace=True)

                    # Aplicar la función modify_category_column
                    data = modify_category_column(data)


            if main_folder == 'GMaps-ML':
                if last_folder == 'metadata-sitios-ML':

                    # Aplicar la función json_normalize_misc
                    data = json_normalize_misc(data)

                    data.drop(columns=['relative_results', 'url', 'description', 'price', 'hours', 'state'], inplace=True)
                    data.rename(columns={'name': 'local_name'}, inplace=True)
                    data.dropna(subset=['category'], inplace=True)
                    data.dropna()
                    data['category'] = data['category'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
                    data = data.applymap(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)
                    data.drop_duplicates(inplace=True)
                    
                    mask = data['category'].str.contains('|'.join(food_service), case=False)
                    data = data[mask]

                    data['state'] = data['address'].str.extract(r'(FL)')
                    data = data[data['state'] == 'FL']
                    data['City'] = data['address'].str.split(',').str[2:3].str.join(', ').str.strip()
                    data = data[data['City'] == 'Miami']
                    data[(data['latitude'] >= 25) & (data['latitude'] <= 25.99)]
                    data.reset_index(drop=True, inplace=True)



                    

            # Yelp
            if main_folder == 'Yelp':
                if  last_folder == 'review':
                    data.drop(columns=['cool','funny','useful','review_id','user_id'], inplace=True)
                    data.rename(columns={'text':'opinion', 'stars':'rating'}, inplace=True)
                    data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')
                    data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d')
                    data = data[data['date'].dt.year >= 2015]
                    data.reset_index(drop=True,inplace=True)
                    

                if table_name == 'business':
                    data = data.loc[:, ~data.columns.duplicated()]
                    data.drop(columns=['address','postal_code','is_open','attributes','hours'], inplace=True)
                    data.dropna(subset=['categories'], inplace=True)
                    data.dropna()
                    data.drop_duplicates(inplace=True)
                    mask = data['categories'].str.contains('|'.join(food_service), case=False)
                    data = data[mask]
                    data = data.applymap(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)
                    data.reset_index(drop=True,inplace=True)
                    data = data[data['state'] == 'FL']


                if table_name == 'checkin':
                    separated_dates = []

                    for index, row in data.iterrows():
                        if 'date' in row and isinstance(row['date'], str):
                            dates = row['date'].split(', ')
                            for date in dates:
                                separated_dates.append({'business_id': row['business_id'], 'date': date})

                    data = pd.DataFrame(separated_dates)
                    

            data = data.astype(str)

            data.to_gbq(destination_table=dataset + table_name, 
                                    project_id='pg-yelp-gmaps2', 
                                    table_schema=None,
                                    if_exists='append', progress_bar=False,  auth_local_webserver=False,  location='us')

    except Exception as e:
        print(f"An error occurred: {e}")
