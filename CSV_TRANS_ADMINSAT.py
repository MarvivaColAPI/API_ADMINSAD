import requests
import json

# Datos necesarios
username = 'gis.colombia_mv'
password = 'Marviva2022#1'
layer_url = 'https://services1.arcgis.com/GWTczcNsFHCvuTLo/arcgis/rest/services/Capa_Geojson/FeatureServer/0'  # Cambia esto a la URL correcta

# Función para obtener el token de ArcGIS Online
def get_token(username, password):
    token_url = 'https://www.arcgis.com/sharing/rest/generateToken'
    params = {
        'f': 'json',
        'username': username,
        'password': password,
        'referer': 'https://www.arcgis.com'
    }
    response = requests.post(token_url, data=params)
    response_json = response.json()
    if 'token' in response_json:
        return response_json['token']
    else:
        print("Error al obtener el token:", response_json)
        exit()

# Función para consultar datos de la capa en ArcGIS Online
def get_layer_data(token, layer_url):
    data_url = f'{layer_url}/query?where=1=1&outFields=*&f=json&token={token}'
    response = requests.get(data_url)
    
    # Verificar si se obtuvieron correctamente los datos
    if response.status_code == 200:
        response_json = response.json()
        print("Datos obtenidos exitosamente.")
        return response_json['features']  # Devuelve solo las características
    else:
        print(f"Error al obtener los datos: {response.status_code}")
        return None

# Función para actualizar la capa existente con nuevos datos de GeoJSON
def update_layer(token, layer_url, geojson_data):
    # Convertir el GeoJSON dict a string en formato JSON
    geojson_str = json.dumps(geojson_data)

    # Preparar la URL para actualizar la capa
    update_url = f'{layer_url}/updateFeatures'
    
    # Datos a enviar para actualizar la capa
    update_params = {
        'f': 'json',
        'token': token,
        'features': geojson_str  # Agregar los datos de GeoJSON aquí
    }

    response = requests.post(update_url, data=update_params)
    
    # Verificar si la capa se actualizó correctamente
    if response.status_code == 200:
        response_json = response.json()
        if 'updateResults' in response_json and response_json['updateResults'][0]['success']:
            print("Capa actualizada exitosamente.")
        else:
            print(f"Error al actualizar la capa: {response_json}")
    else:
        print(f"Error en la solicitud al actualizar la capa: {response.status_code}")

# Obtener el token de autenticación
token = get_token(username, password)
print(f"Token obtenido: {token}")

# Consultar los datos de la capa
geojson_data = get_layer_data(token, layer_url)

# Actualizar la capa con los nuevos datos si se obtuvieron correctamente
if geojson_data:
    update_layer(token, layer_url, geojson_data)
else:
    print("No se pudieron obtener los datos del GeoJSON.")
