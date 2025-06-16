import os
import json
from flask import Flask, send_from_directory, send_file, abort, Response
import requests, overpy, geojson
import hashlib, pickle
from functools import wraps
import numpy as np

def fusionarCalles(viario):
    # Anota en los extremos en los que dos calles coinciden.
    extremos= {}
    for feature in viario:
        if feature.get('geometry', {}).get('type') == 'LineString':
            coords = feature['geometry']['coordinates']
            if len(coords) < 2:
                continue
            c0 = tuple(coords[0])
            c1 = tuple(coords[-1])
            # if c0 == c1:
            #     continue
            if extremos.get(c0) is None:
                extremos[c0] = [feature]
            else:
                # inser if not in
                if feature not in extremos[c0]:
                    extremos[c0].append(feature)
            if extremos.get(c1) is None:
                extremos[c1] = [feature]
            else:
                # inser if not in
                if feature not in extremos[c1]:
                    extremos[c1].append(feature)
    # cuenta el número de calles con igual nombre
    for c, features in extremos.items():
        if len(features) > 1:
            nameCount= {}
            for feature in features:
                name = feature['properties'].get('name','default')                
                if nameCount.get(name) is None:
                    nameCount[name] = 1
                else:
                    nameCount[name] += 1
            for name, count in nameCount.items():
                if count ==2:
                    # si no hay ambigüedad, las fusiona.
                    # Al fusionarlas reemplazar en otros extremos
                    primero=None
                    segundo=None
                    for feature in features:
                        name2 = feature['properties'].get('name','default')
                        if name2==name:
                            coords = feature['geometry']['coordinates']
                            c0 = tuple(coords[0])
                            c1 = tuple(coords[-1])
                            if c0==c:
                                segundo=feature
                            if c1==c:
                                primero=feature

                    if primero==segundo:
                        print("Absurdo se ha introducido dos veces la misma calle")
                        continue

                    if primero is None or segundo is None:
                        print("Debgueo: No se han encontrado dos calles con el mismo nombre en los extremos", c, name)
                        continue

                    # Fusiona las propiedades y concatena las coordenadas
                    new_feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": primero['geometry']['coordinates'] + segundo['geometry']['coordinates'][1:]
                        },
                        "properties": {**primero['properties'], **segundo['properties']}
                    }
                    # Reemplaza las características originales en el viario
                    # elimina las originales
                    viario.remove(primero)
                    if not segundo in viario:
                        print("Debug: No se ha encontrado la segunda calle en el viario", segundo)
                    viario.remove(segundo)
                    # añade la nueva
                    viario.append(new_feature)
                    # cambia en los extremos
                    extremos[c].remove(primero)
                    extremos[c].remove(segundo)
                    extremos[c].append(new_feature)
                    # En los otros extremos, reemplaza la referencia
                    c_1=tuple(new_feature['geometry']['coordinates'][-1])
                    c_0=tuple(new_feature['geometry']['coordinates'][0])
                    if c_1 !=c:
                        extremos[c_1].remove(segundo)
                        extremos[c_1].append(new_feature)
                    if c_0!=c:
                        if not primero in extremos[c_0]:
                            print("Debug: No se ha encontrado la primera calle en el extremo", primero, c_0)
                        extremos[c_0].remove(primero)
                        extremos[c_0].append(new_feature)

def cache(func):
    """
    Decorador que, dado que la función recibe (entre otros) parámetros de tipo dict,
    genera un hash a partir de ellos y almacena el resultado en ../cache/<hash>.
    En llamadas posteriores con los mismos dicts, carga el resultado desde disco.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
    
        # 2) Serializar esos dicts de forma canónica (JSON con sort_keys=True)
        #    para que el hash sea estable independientemente del orden interno de los dicts.
        try:
            serializado = json.dumps(kwargs, sort_keys=True, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            # Si alguno de los dicts contiene valores no JSON-serializables, podemos
            # recurrir a pickle para serializar, aunque el hash podría variar más.
            serializado = pickle.dumps(kwargs)
        
        # 3) Calcular un SHA256 sobre esa cadena/binario
        if isinstance(serializado, str):
            serializado = serializado.encode('utf-8')
        digest = hashlib.sha256(serializado).hexdigest()

        # 4) Construir ruta a ../cache/<digest>
        #    Asumimos que el directorio base es aquel donde se ejecuta este script.
        cache_dir = os.path.abspath(os.path.join(os.getcwd(), '..', 'cache'))
        os.makedirs(cache_dir, exist_ok=True)
        cache_path = os.path.join(cache_dir, digest)

        # 5) Si ya existe el archivo de cache, devolverlo en lugar de llamar a func
        if os.path.isfile(cache_path):
            with open(cache_path, 'rb') as f:
                resultado_guardado = pickle.load(f)
            return resultado_guardado

        # 6) Si no existía cache, ejecutar la función, guardar el resultado y devolverlo
        resultado = func(**kwargs)
        with open(cache_path, 'wb') as f:
            pickle.dump(resultado, f)
        return resultado

    return wrapper

@cache
def download_viario(city="Sevilla",highwayFilter='motorway trunk primary secondary',cache=0,highwayExclude=""):
    """


    Descarga el viario principal de Sevilla (rotondas y avenidas principales)
    usando la librería Overpy (Overpass API) y retorna un FeatureCollection GeoJSON.

    Args:
        output_geojson_path (str, opcional): Ruta para guardar el GeoJSON resultante.

    Returns:
        dict: GeoJSON FeatureCollection con líneas de rotondas y avenidas principales.
    """
    # Inicializar API de Overpass
    api = overpy.Overpass()

    # Consulta: todas las rotondas y vías principales (motorway, trunk, primary, secondary, tertiary)
    # en el área administrativa de Sevilla
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = '''
    [out:json][timeout:180];
    area[name="Sevilla"][boundary="administrative"][admin_level="8"]->.searchArea;
    (
      way["highway"](area.searchArea);
    );
    out geom;
    '''
    query=query.replace("Sevilla", city)

    response = requests.get(overpass_url, params={'data': query})
    response.raise_for_status()
    data = response.json()

    features = []
    tipos={}

    # motorway	rosa / salmón (#E8755A)
    # trunk	naranja (#FF8000)
    # primary	amarillo (#FFD700)
    # secondary

    
    highwayFilter=highwayFilter.split()
    highwayExclude=highwayExclude.split()

    noIncluded=set()
    for elem in data.get('elements', []):
        if elem.get('type') == 'way' and 'geometry' in elem:
            coords = [(pt['lon'], pt['lat']) for pt in elem['geometry']]
            feature = geojson.Feature(
                geometry=geojson.LineString(coords),
                properties=elem.get('tags', {})
            )
            if 'highway' in feature['properties']:
                highway = feature['properties']['highway']
                if highway in highwayExclude:
                    continue
                if highway in highwayFilter or highwayFilter == ['all']:
                    features.append(feature)
                else:
                    noIncluded.add(highway)

    #print("Tipos de carreteras no incluidas:", " ".join(str(x) for x in noIncluded))


    if False:
        for num,c in enumerate(cruce.cruces):
            features2=None
            # infinite at beginning
            cercano= 9999999999
            for elem in data.get('elements', []):
                p= (c['Longitud'], c['Latitud'])
                if elem.get('type') == 'way' and 'geometry' in elem:
                    coords = [(pt['lon'], pt['lat']) for pt in elem['geometry']]

                    for i in range(len(coords)-1):
                        dentro, proy = proyecta_en_segmento(p, coords[i], coords[i+1])
                        if dentro:
                            # feature = geojson.Feature(
                            #     geometry=geojson.LineString(coords),
                            #     properties=elem.get('tags', {})
                            # )
                            # filtra rotonda
                            # highway=feature['properties'].get('lanes')
                            # if tipos.get(highway) is None:
                            #     tipos[highway]=1
                            # else:
                            #     tipos[highway]+=1
                            #if not highway is None and  highway>"1":
                            distancia= ((p[0]-proy[0])**2 + (p[1]-proy[1])**2)
                            if distancia<cercano:
                                cercano=distancia
                                feature = geojson.Feature(
                                    geometry=geojson.LineString(coords),
                                    properties=elem.get('tags', {})
                                )
                                #print(f"Elemento: {elem['tags']}")
                                #print(f"Elemento: {elem['geometry']}")
                                #print(f"Elemento: {feature}")

                                features2=feature

            
                # mantienes una estructura circular ordenada. 
                # El problema son las medio lunas. 
                # Alternativa b. Por los detectores.
            features.append(features2)
            print("Progreso: ", num, " / ", len(cruce.cruces))

    for highway, count in tipos.items():
        print(f"{highway}: {count}")

    return features 

    feature_collection = geojson.FeatureCollection(features)

    feature_collection["crs"]= {
        "type": "name",
        "properties": {
        "name": "EPSG:4326"
        }
    }

    # Guardar GeoJSON si se solicita
    # if output_geojson_path:
    #     with open(output_geojson_path, 'w', encoding='utf-8') as f:
    #         json.dump(feature_collection, f, ensure_ascii=False, indent=2)

    return feature_collection

def duplicarViario(viario):
    """
    Duplicates the given viario GeoJSON features by creating a new feature for each existing one.
    This is useful for visualizing both sides of a road or path in a map.
    
    Args:
        viario (list): List of GeoJSON features representing the viario.

    Returns:
        list: New list of GeoJSON features with duplicated geometries.
    """
    duplicated_features = []
    reubicacion={}
    reubicable=[]
    for feature in viario:
        if feature.get('geometry', {}).get('type') == 'LineString':
            properties = feature.get('properties', {})
            oneway= properties.get('oneway')
            lanes = properties.get('lanes')

            if oneway==None and lanes is not None:
                junction= properties.get('junction')
                if junction is None:
                    nlanes=int(lanes)
                    if nlanes > 1:
                        oneway='no'


            if oneway == 'yes' or oneway == None:
                duplicated_features.append(feature) 
                reubicable.append(feature)
            else:
                # Halla el vecotr de la dirección.
                coords = feature['geometry']['coordinates']
                if len(coords) < 0:
                    continue
                a= coords[0]
                b= coords[-1]
                direction= (
                    (b[0] - a[0]),
                    (b[1] - a[1])
                )
                ortogonal= (
                    -direction[1],  # Invertir y cambiar de lugar para ortogonal
                    direction[0]
                )
                length = (ortogonal[0]**2 + ortogonal[1]**2)**0.5
                if length == 0:
                    continue
                ortogonal = (
                    ortogonal[0] / length,  # Normalizar
                    ortogonal[1] / length
                )

                if lanes is not None:
                    properties["lanes"] = str(int(lanes) // 2)

                coords1 = []
                coords_1= []
                for i,c in enumerate(coords):
                    #weight =  0.000005*nlanes
                    weight =  0.00001
                    extremo=0
                    if 0==i:
                        extremo=-1
                    if i==len(coords)-1:
                        extremo=1
                    #     weight = 0 
                    # Desplazar ortogonalmente
                    coords1.append((c[0] + ortogonal[0] * weight, c[1] + ortogonal[1] * weight))
                    coords_1.append((c[0] - ortogonal[0] * weight, c[1] - ortogonal[1] * weight))
                    c=tuple(c)

                    if reubicacion.get(c) is None:
                        reubicacion[c] = [
                            (coords1[-1],-extremo),
                            (coords_1[-1],extremo)
                        ]
                    else:
                        reubicacion[c].append((coords1[-1],-extremo))
                        reubicacion[c].append((coords_1[-1],extremo))

                properties["oneway"] = "yes"

                
                # Reverse coord1
                coords1.reverse()
                duplicated_features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coords1
                    },
                    "properties": properties
                })
                duplicated_features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coords_1
                    },
                    "properties": properties
                })

    # Reubicar coordenadas
    for feature in reubicable:
        coords = feature['geometry']['coordinates']
        # Solo reubicamos extremos
        c0=tuple(coords[0])
        if reubicacion.get(c0) is not None:
            cand= reubicacion[c0]
            minDistancia = float('inf')
            mejorCoord = None
            for c_ in cand:
                c, extremo = c_
                dentro, proyecta = proyecta_en_segmento2(c, c0, coords[1])
                distancia = ((c[0] - proyecta[0]) ** 2 + (c[1] - proyecta[1]) ** 2)
                if extremo==-1:
                    dentro=False
                if dentro:
                    if distancia < minDistancia:
                        minDistancia = distancia
                        mejorCoord = c 
            coords[0] = mejorCoord

        c1=tuple(coords[-1])
        if reubicacion.get(c1) is not None:
            cand= reubicacion[c1]
            minDistancia = float('inf')
            mejorCoord = None
            for c_ in cand:
                c, extremo = c_
                dentro, proyecta = proyecta_en_segmento2(c, coords[-2], c1)
                distancia = ((c[0] - proyecta[0]) ** 2 + (c[1] - proyecta[1]) ** 2)
                if extremo==1:
                    dentro=False
                if dentro:                    
                    if distancia < minDistancia:
                        minDistancia = distancia
                        mejorCoord = c
            coords[-1] = mejorCoord
    return duplicated_features

# Función para filtrar GeoJSON por Regulador
def filter_geojson_by_cruce(regulador_value):
    geo_file = os.path.join(app.root_path, 'private', 'LamparasOficial', 'Lamparas_vehiculo.geojson')
    if os.path.isfile(geo_file):
        with open(geo_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Filtrar features
        filtered_lights = [
            feat for feat in data.get('features', [])
            if feat.get('properties', {}).get('Regulador') == regulador_value
        ]

        filtered_lights = []
        nposte_set = set()

        for feat in data.get('features', []):
            props = feat.get('properties', {})
            if props.get('Regulador') == regulador_value:
                filtered_lights.append(feat)
                nposte = props.get('Nposte')
                if nposte is not None:
                    nposte_set.add(nposte)

        # select postes than appear in the filtered features
        poste_file = os.path.join(app.root_path, 'private', 'PostesOficial', 'Postes.geojson')
        with open(poste_file, 'r', encoding='utf-8') as f:
            poste = json.load(f)
        
        filtered_postes = []
        Nposte2poste= {}
        for feat in poste.get('features', []):
            props = feat.get('properties', {})
            nposte = props.get('NPoste')
            regulador = props.get('Regulador')
            # nposte in nposte_set and 
            if regulador == regulador_value:
                filtered_postes.append(feat)
                Nposte2poste[nposte] = feat

       

        # Map
        viario=download_viario(cache=3,highwayFilter='all',highwayExclude="footway cycleway service construction steps pedestrian path")

        viriado=fusionarCalles(viario)

        viario=duplicarViario(viario)

        proyectarPostes(filtered_postes, viario)

        #  include lines between postes and lights
        lines=[]
        for light in filtered_lights:
            props = light.get('properties', {})
            nposte = props.get('Nposte')
            if nposte in Nposte2poste:
                poste_feat = Nposte2poste[nposte]
                # Crear una línea entre el poste y la luz
                mediumPoint= (
                    (poste_feat['geometry']['coordinates'][0] + light['geometry']['coordinates'][0]) / 2,
                    (poste_feat['geometry']['coordinates'][1] + light['geometry']['coordinates'][1]) / 2
                )
                line = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            poste_feat['geometry']['coordinates'],
                            mediumPoint
                        ]
                    },
                    "properties": {
                        "Nposte": nposte,
                        "Regulador": regulador_value
                    }
                }
                lines.append(line)

        # Construir nuevo objeto GeoJSON
        data["features"] = lines+filtered_lights+filtered_postes+viario
        return json.dumps(data, ensure_ascii=False)
    return ""

def proyecta_en_segmento2(punto, inicio, fin):
    medio= (
        (inicio[0] + fin[0]) / 2,
        (inicio[1] + fin[1]) / 2
    )
    return True, medio

def proyecta_en_segmento(punto, inicio, fin):
    """
    Proyecta un punto sobre un segmento definido por dos puntos (inicio y fin).
    Devuelve si el punto está dentro del segmento y las coordenadas del punto proyectado.
    """
    # Convertir a numpy para cálculos más fáciles
    p = np.array(punto)
    a = np.array(inicio)
    b = np.array(fin)

    # Vector del segmento
    ab = b - a
    # Longitud del segmento
    ab_length = np.linalg.norm(ab)

    if ab_length == 0:
        return False, None  # El segmento es un punto

    # Proyección del punto sobre el segmento
    ap = p - a
    t = np.dot(ap, ab) / (ab_length ** 2)

    dentro= 0<t  and t < 1

    proy = a + t * ab
    return dentro, tuple(proy)


def proyectarPostes(postes, viario):
    for poste in postes:
        coords = poste['geometry']['coordinates']
        p = (coords[0], coords[1])
        # infinite at beginning
        cercano = 9999999999
        proy = None
        for elem in viario:
            if elem.get('geometry', {}).get('type') == 'LineString':
                coords2 = elem['geometry']['coordinates']
                for i in range(len(coords2) - 1):
                    dentro, proy2 = proyecta_en_segmento(p, coords2[i], coords2[i + 1])
                    if dentro:
                        distancia = ((p[0] - proy2[0]) ** 2 + (p[1] - proy2[1]) ** 2)
                        if distancia < cercano:
                            cercano = distancia
                            proy = proy2
        if proy is not None:
            poste['geometry']['coordinates'] = proy


# Configuración de la aplicación
def create_app():
    app = Flask(__name__)
    PORT = int(os.environ.get('PORT', 3000))

    # 1) Ruta raíz y /main.html → entregamos html/main.html
    @app.route('/')
    @app.route('/main.html')
    def root():
        return send_file(os.path.join(app.root_path, 'html', 'main.html'))

    # 2) Catch-all para manejar recursos estáticos, módulos y geojson
    @app.route('/<path:req_path>')
    def catch_all(req_path):
        # 2.1) Archivos estáticos desde ./http
        http_file = os.path.join(app.root_path, 'http', req_path)
        if os.path.isfile(http_file):
            return send_from_directory(os.path.join(app.root_path, 'http'), req_path)

        # 2.2) Módulos desde ./node_modules
        modules_file = os.path.join(app.root_path, 'node_modules', req_path)
        if os.path.isfile(modules_file):
            return send_from_directory(os.path.join(app.root_path, 'node_modules'), req_path)

        # 2.3) GeoJSON especial
        if req_path.startswith('Nueva_1.geojson'):
            filtered = filter_geojson_by_cruce(152)
            return Response(filtered, mimetype='application/vnd.geo+json')

        # 2.4) Otros archivos en html/
        html_file = os.path.join(app.root_path, 'html', req_path)
        if os.path.isfile(html_file):
            return send_file(html_file)

        # 2.5) No encontrado → 404
        abort(404)

    return app


import os
import threading
import webbrowser



# 3) Arrancamos el servidor
if __name__ == '__main__':
    app = create_app()
    port=3000

    url = f'http://localhost:{port}/'

    def _open_browser():
        webbrowser.open(url, new=2)

    threading.Timer(0.30, _open_browser).start()

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', port)))