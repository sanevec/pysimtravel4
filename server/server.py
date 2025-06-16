import os
from flask import Flask, send_from_directory, send_file, abort, Response
import numpy as np
from map.map import getMap

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
            filtered = getMap()
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