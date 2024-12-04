import json
import requests
import geojson
import os
from git import Repo

# URL para solicitar el token de autenticación
url_autenticacion = "https://api.adminsat.com/v2/api/applications/autenticacion/token/"
# URL para solicitar la ubicación de los activos
url_ubicacion = "https://api.adminsat.com/v2/api/applications/public/ubicacion/"

# Credenciales de usuario (proporcionadas por el cliente)
usuario = "manuel.velandia"
contrasena = "YhnTgb45"
client_id = "2FPHX5uTah9b5afo3a2Fk14aNaoGTKPIUT5GXTBk"
client_secret = "wIFBOahewJLYK9btPbiC4aDwr57oY6R9yIGXKPtf9ljeiZCXjWX4MrDjOhjbHRVYUVX9X8h3aLKVCeg4xngyWGaBcYTKgFUf9Aj0bH7Vz16dErE0lQYn2eLR1cKmTOMj"

# Cuerpo de la petición para obtener el token de autenticación
cuerpo_peticion_autenticacion = {
    "username": usuario,
    "password": contrasena,
    "client_id": client_id,
    "client_secret": client_secret,
    "grant_type": "password"
}

# Cabecera de la petición para obtener el token de autenticación
cabecera_autenticacion = {
    "Content-Type": "application/json"
}

# Hacer una solicitud POST para obtener el token de autenticación
respuesta_autenticacion = requests.post(url_autenticacion, json=cuerpo_peticion_autenticacion, headers=cabecera_autenticacion)

# Verificar si la solicitud fue exitosa (código de estado 200)
if respuesta_autenticacion.status_code == 200:
    # Extraer el token de autenticación de la respuesta JSON
    access_token = respuesta_autenticacion.json()["access_token"]
    # Cabecera de la petición para obtener la ubicación de los activos
    cabecera_ubicacion = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    # Hacer una solicitud GET para obtener la ubicación de los activos
    respuesta_ubicacion = requests.get(url_ubicacion, headers=cabecera_ubicacion)
    # Verificar si la solicitud fue exitosa (código de estado 200)
    if respuesta_ubicacion.status_code == 200:
        # Extraer la información de ubicación de la respuesta JSON
        ubicaciones = respuesta_ubicacion.json()
        
        # Crear una lista para almacenar las características GeoJSON
        features = []
        
        # Leer el archivo existente si existe
        archivo_geojson = "ubicaciones.geojson"
        if os.path.exists(archivo_geojson):
            with open(archivo_geojson, "r") as archivo:
                feature_collection_existente = geojson.load(archivo)
                features.extend(feature_collection_existente["features"])
        
        # Iterar sobre cada ubicación y crear una característica GeoJSON para cada una
        for ubicacion in ubicaciones:
            # Crear un diccionario de propiedades para la ubicación
            propiedades = {
                "Nombre": ubicacion["nombre"],
                "Placa": ubicacion["placa"],
                "Velocidad": ubicacion["velocidad"],
                "Calidad GPS": "Buena" if ubicacion["calidad_gps"] else "Mala",
                "Ignición": "Encendido" if ubicacion["ignicion"] else "Apagado" if ubicacion["ignicion"] is not None else "Desconocido",
                "Porcentaje de batería": ubicacion["bateria"],
                "Altitud": ubicacion["altitud"],
                "Fecha y hora del equipo": ubicacion["fecha_hora_equipo"],
                "Fecha y hora del servidor": ubicacion["fecha_hora_servidor"],
                "Evento": ubicacion["evento_nombre"],
                "Identificador": ubicacion["identificador"],
                "Odómetro": ubicacion["odometro"]
            }
            
            # Crear una geometría Point usando las coordenadas de latitud y longitud
            geometria = geojson.Point((ubicacion["longitud"], ubicacion["latitud"]))
            
            # Crear una característica GeoJSON con las propiedades y la geometría
            feature = geojson.Feature(geometry=geometria, properties=propiedades)
            
            # Agregar la característica a la lista de características
            features.append(feature)
        
        # Crear una colección FeatureCollection con todas las características
        feature_collection = geojson.FeatureCollection(features)
        
        # Escribir la colección FeatureCollection en el archivo .geojson
        with open(archivo_geojson, "w") as archivo:
            geojson.dump(feature_collection, archivo, indent=4)
            
        print("Archivo .geojson creado correctamente.")
        
        # Agregar y hacer commit de los cambios en el repositorio de GitHub
        repo_dir = os.path.abspath(os.path.dirname(__file__))  # Ruta al directorio del script
        repo = Repo(repo_dir)
        
        # Agregar los cambios
        repo.git.add(archivo_geojson)
        
        # Hacer commit de los cambios
        repo.index.commit('Actualización automática del archivo ubicaciones.geojson')
        
        # Empujar los cambios al repositorio remoto
        origin = repo.remote(name='origin')
        origin.push()
            
    else:
        print("Error al obtener la ubicación de los activos:", respuesta_ubicacion.status_code)
else:
    print("Error al obtener el token de autenticación:", respuesta_autenticacion.status_code)
