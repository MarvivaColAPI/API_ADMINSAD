import json
import requests
import geojson
import os
from git import Repo
from datetime import datetime

# URL para solicitar el token de autenticación
url_autenticacion = "https://api.adminsat.com/v2/api/applications/autenticacion/token/"
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

# Verificar si la solicitud fue exitosa
if respuesta_autenticacion.status_code == 200:
    # Extraer el token de autenticación
    access_token = respuesta_autenticacion.json()["access_token"]
    cabecera_ubicacion = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    # Hacer una solicitud GET para obtener la ubicación de los activos
    respuesta_ubicacion = requests.get(url_ubicacion, headers=cabecera_ubicacion)
    
    if respuesta_ubicacion.status_code == 200:
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
            # Convertir las fechas de UNIX a formato americano
            fecha_hora_equipo = datetime.fromtimestamp(ubicacion["fecha_hora_equipo"]).strftime('%m/%d/%Y %H:%M:%S')
            fecha_hora_servidor = datetime.fromtimestamp(ubicacion["fecha_hora_servidor"]).strftime('%m/%d/%Y %H:%M:%S')
            
            # Crear un diccionario de propiedades para la ubicación
            propiedades = {
                "Nombre": ubicacion["nombre"],
                "Placa": ubicacion["placa"],
                "Velocidad": ubicacion["velocidad"],
                "Calidad GPS": "Buena" if ubicacion["calidad_gps"] else "Mala",
                "Ignición": "Encendido" if ubicacion["ignicion"] else "Apagado" if ubicacion["ignicion"] is not None else "Desconocido",
                "Porcentaje de batería": ubicacion["bateria"],
                "Altitud": ubicacion["altitud"],
                "Fecha y hora del equipo": fecha_hora_equipo,
                "Fecha y hora del servidor": fecha_hora_servidor,
                "Evento": ubicacion["evento_nombre"],
                "Identificador": ubicacion["identificador"],
                "Odómetro": ubicacion["odometro"]
            }
            
            # Crear una geometría Point usando las coordenadas
            geometria = geojson.Point((ubicacion["longitud"], ubicacion["latitud"]))
            
            # Crear una característica GeoJSON
            feature = geojson.Feature(geometry=geometria, properties=propiedades)
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
        repo.git.add(archivo_geojson)
        repo.index.commit('Actualización automática del archivo ubicaciones.geojson')
        origin = repo.remote(name='origin')
        origin.push()
    else:
        print("Error al obtener la ubicación de los activos:", respuesta_ubicacion.status_code)
else:
    print("Error al obtener el token de autenticación:", respuesta_autenticacion.status_code)
