import requests
import json
import os

# Parámetros de autenticación de ArcGIS
username = 'gis.colombia_mv'
password = 'Marviva2022#1'

# Obtener token de autenticación de ArcGIS
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

token = get_token(username, password)
print(f"Token obtenido: {token}")

# ID del ítem existente
item_id = '71a9955bd81c410186b6914c408dafb9'

# URL del servicio de ArcGIS Online donde actualizarás los datos
update_url = f'https://www.arcgis.com/sharing/rest/content/users/{username}/items/{item_id}/update'

# Ruta relativa al archivo GeoJSON en el repositorio
archivo_geojson = 'ubicaciones.geojson'

# Asegúrate de que el archivo existe
if not os.path.exists(archivo_geojson):
    print(f"El archivo {archivo_geojson} no existe.")
    exit()

# Actualizar archivo GeoJSON en ArcGIS Online
with open(archivo_geojson, 'rb') as file:
    files = {'file': file}
    params = {
        'f': 'json',
        'token': token
    }
    response = requests.post(update_url, files=files, data=params)
    response_data = response.json()

# Verifica si la actualización fue exitosa
if 'success' in response_data and response_data['success']:
    print(f"Archivo actualizado exitosamente. ID del ítem: {item_id}")
else:
    print("Error al actualizar el archivo:", response_data)
    exit()
