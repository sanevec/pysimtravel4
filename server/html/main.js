import Map from 'ol/Map.js';
import View from 'ol/View.js';
import Draw from 'ol/interaction/Draw.js';
import TileLayer from 'ol/layer/Tile.js';
import VectorLayer from 'ol/layer/Vector.js';
import OSM from 'ol/source/OSM.js';
import VectorSource from 'ol/source/Vector.js';
import { fromLonLat } from 'ol/proj.js';

import Style        from 'ol/style/Style.js';
import Stroke       from 'ol/style/Stroke.js';
import Fill         from 'ol/style/Fill.js';
import RegularShape from 'ol/style/RegularShape.js';
import Text         from 'ol/style/Text.js';
import PointGeom    from 'ol/geom/Point.js';
import LineString   from 'ol/geom/LineString.js';

import GeoJSON from 'ol/format/GeoJSON.js';

const geojsonFormat = new GeoJSON();

// URL del GeoJSON
const lamparasUrl = '/Nueva_1.geojson';

// Fuente vectorial inicial
const source = new VectorSource({
  url: lamparasUrl,
  format: new GeoJSON({
    dataProjection:    'EPSG:25830',
    featureProjection: 'EPSG:3857'
  }),
  wrapX: false
});

// Cargamos el GeoJSON original y luego puntos y líneas persistidos
fetch(lamparasUrl)
  .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
  .then(json => {
    // 1) Features originales
    const features = geojsonFormat.readFeatures(json, {
      dataProjection:    'EPSG:25830',
      featureProjection: 'EPSG:3857'
    });
    // asignar tipo 'Poste' a todos los puntos originales
    features.forEach(f => {
      if (f.getGeometry().getType() === 'Point') {
        f.set('tipo', 'Poste');
      }
    });
    source.addFeatures(features);

    // 2) Puntos persistidos
    const persistedPoints = JSON.parse(localStorage.getItem('savedPoints') || '[]');
    if (persistedPoints.length) {
      const extraPoints = geojsonFormat.readFeatures({
        type: 'FeatureCollection',
        features: persistedPoints
      }, {
        dataProjection:    'EPSG:25830',
        featureProjection: 'EPSG:3857'
      });
      source.addFeatures(extraPoints);
    }

    // 3) Líneas persistidas
    const persistedLines = JSON.parse(localStorage.getItem('savedLines') || '[]');
    if (persistedLines.length) {
      const extraLines = geojsonFormat.readFeatures({
        type: 'FeatureCollection',
        features: persistedLines
      }, {
        dataProjection:    'EPSG:25830',
        featureProjection: 'EPSG:3857'
      });
      source.addFeatures(extraLines);
    }
  })
  .catch(err => console.error('Error al cargar GeoJSON:', err));


// Colores por tipo
const colorPorTipo = {
  Poste:       'green',
  Coche:       'gray',
  Peatón:      'orange',
  Bicicleta:   'blue',
  Tranvibus:   'black',
  Semáforo:    'crimson',
  Bifurcación: 'dodgerblue'
};

// Crear forma según dirección
function crearFormaPorDireccion(direccion, color) {
  switch (direccion) {
    case 'Origen':
      return new RegularShape({ points: Infinity, radius: 6, fill: new Fill({ color }), stroke: new Stroke({ color:'black', width:1 }) });
    case 'Destino':
      return new RegularShape({ points: 4, radius: 6, angle: Math.PI/4, fill: new Fill({ color }), stroke: new Stroke({ color:'black', width:1 }) });
    case 'Bidireccional':
      return new RegularShape({ points: 3, radius: 8, fill: new Fill({ color }), stroke: new Stroke({ color:'black', width:1 }) });
    default:
      return new RegularShape({ points: Infinity, radius: 4, fill: new Fill({ color:'#888' }), stroke: new Stroke({ color:'black', width:1 }) });
  }
}

// Capa base
const raster = new TileLayer({ source: new OSM() });

// Capa vectorial con estilo dinámico
const vectorLayer = new VectorLayer({
  source,
  style: feature => {
    const geom = feature.getGeometry();
    const styles = [];

    // Líneas
    if (geom instanceof LineString) {
      // color según tipo de línea
      const tipoLinea = feature.get('tipo') || 'Coche';
      const lineColor = colorPorTipo[tipoLinea] || 'blue';
      styles.push(new Style({ stroke: new Stroke({ color: lineColor, width: 5 }) }));

      // flecha al final
      const coords = geom.getCoordinates();
      if (tipoLinea !== 'Peatón' && coords.length >= 2) {
        coords.slice(1).forEach((pt, i) => {
            const [x1, y1] = coords[i];
            const [x2, y2] = pt;
            const dx = x2 - x1, dy = y2 - y1;
            // ángulo de la flecha (mismo cálculo que antes)
            const rot = Math.atan2(dy, dx) - Math.PI/2;

            styles.push(new Style({
              geometry: new PointGeom([x2, y2]),
              image: new RegularShape({
                points: 3,
                radius: 8,
                rotation: -rot,
                rotateWithView: true,
                fill: new Fill({ color: lineColor })
              })
            }));
          });
        
          // Código antiguo que solo dibuja una flecha al final de la línea
        // const [x1,y1] = coords[coords.length-2];
        // const [x2,y2] = coords[coords.length-1];
        // const dx = x2-x1, dy = y2-y1;
        // const rot = Math.atan2(dy,dx) - Math.PI/2;
        // styles.push(new Style({
        //   geometry: new PointGeom([x2,y2]),
        //   image: new RegularShape({
        //     points: 3,
        //     radius: 8,
        //     rotation: -rot,
        //     rotateWithView: true,
        //     fill: new Fill({ color: lineColor })
        //   })
        // }));
      }

      // texto de carriles si >=2
      const lanes = parseInt(feature.get('carriles'),10) || 1;
      if (lanes >= 2) {
        const mid = geom.getCoordinateAt(0.5);
        styles.push(new Style({
          geometry: new PointGeom(mid),
          text: new Text({
            text: lanes.toString(),
            font: 'bold 16px sans-serif',
            fill: new Fill({ color: lineColor }),
            stroke: new Stroke({ color: 'white', width: 3 }),
            offsetY: -12
          })
        }));
      }

      return styles;
    }

    // Puntos
    if (geom.getType() === 'Point') {
      const tipo      = feature.get('tipo')      || 'Poste';
      const direccion = feature.get('direccion') || 'Origen';
      const color     = colorPorTipo[tipo]       || 'black';
      return new Style({ image: crearFormaPorDireccion(direccion, color) });
    }

    return null;
  }
});

// Restaurar view
const savedZoom   = parseFloat(localStorage.getItem('zoomLevel'));
const savedCenter = localStorage.getItem('mapCenter');
const initialZoom = isNaN(savedZoom) ? 13 : savedZoom;
const initialCenter = savedCenter
  ? JSON.parse(savedCenter)
  : fromLonLat([-5.984459,37.389092]);

// Crear mapa
const map = new Map({
  layers: [ raster, vectorLayer ],
  target: 'map',
  view: new View({ center: initialCenter, zoom: initialZoom })
});

// Referencias DOM
const infoPopup   = document.getElementById('infoPopup');
const infoTextarea = document.getElementById('infoTextarea');
const closeInfoBtn = document.getElementById('closeInfo');

const accionSelect    = document.getElementById('accion');
const direccionSelect = document.getElementById('direccion');
const tipoSelect      = document.getElementById('tipo');
const carrilesSelect  = document.getElementById('carriles');

const direccionContainer = direccionSelect.closest('.col-auto');
const tipoContainer      = tipoSelect.closest('.col-auto');
const carrilesContainer  = carrilesSelect.closest('.col-auto');

closeInfoBtn.addEventListener('click', () => {
  infoPopup.style.display = 'none';
});

let draw; // interacción activa

// Control visibilidad combos
function updateCombosVisibility(accion) {
  direccionContainer.style.display = accion==='Punto'             ? 'block':'none';
  tipoContainer.style.display      = (accion==='Punto'||accion==='Línea') ? 'block':'none';
  carrilesContainer.style.display  = accion==='Línea'             ? 'block':'none';
  if (accion === 'Consultar') {
    direccionContainer.style.display = 'none';
    tipoContainer.style.display      = 'none';
    carrilesContainer.style.display  = 'none';
  }
}

// Manejo de acción
accionSelect.addEventListener('change', () => {
  const accion = accionSelect.value;

  if (draw) {
    map.removeInteraction(draw);
    draw = null;
  }

  if (accion === 'Línea') {
    draw = new Draw({ source, type:'LineString' });

    draw.on('drawend', event => {
      const feature = event.feature;
      const geom    = feature.getGeometry();
      const coords  = geom.getCoordinates();
      const snapR   = 20;

      // snap de extremos
      const pts = source.getFeatures().filter(f=>f.getGeometry().getType()==='Point');
      const snap = c => {
        let minD=Infinity, nearest=null;
        pts.forEach(f=>{
          const fc=f.getGeometry().getCoordinates();
          const d=Math.hypot(fc[0]-c[0],fc[1]-c[1]);
          if(d<minD){minD=d;nearest=fc;}
        });
        return (nearest&&minD<=snapR)?nearest:c;
      };
      coords[0] = snap(coords[0]);
      coords[coords.length-1] = snap(coords[coords.length-1]);
      geom.setCoordinates(coords);

      // añadir carriles y tipo
      feature.set('carriles', carrilesSelect.value);
      feature.set('tipo',    tipoSelect.value);

      // persistir línea
      const arr = JSON.parse(localStorage.getItem('savedLines')||'[]');
      arr.push( geojsonFormat.writeFeatureObject(feature,{
        dataProjection:'EPSG:25830',
        featureProjection:'EPSG:3857'
      }) );
      localStorage.setItem('savedLines', JSON.stringify(arr));
    });

    map.addInteraction(draw);

  } else if (accion === 'Punto') {
    draw = new Draw({ source, type:'Point' });

    draw.on('drawend', event => {
      const f = event.feature;
      f.setProperties({
        direccion: direccionSelect.value,
        tipo:      tipoSelect.value
      });
      if (f.get('tipo')!=='Poste') {
        const arr = JSON.parse(localStorage.getItem('savedPoints')||'[]');
        arr.push( geojsonFormat.writeFeatureObject(f,{
          dataProjection:'EPSG:25830',
          featureProjection:'EPSG:3857'
        }) );
        localStorage.setItem('savedPoints', JSON.stringify(arr));
      }
    });

    map.addInteraction(draw);
  }

  updateCombosVisibility(accion);
});

// inicializar visibilidad
document.addEventListener('DOMContentLoaded', () => {
  updateCombosVisibility(accionSelect.value);
});

// guardar zoom/center
let lastZ = map.getView().getZoom();
let lastC = map.getView().getCenter();
map.on('moveend', ()=>{
  const v=map.getView(), nz=v.getZoom(), nc=v.getCenter();
  if(nz!==lastZ||nc[0]!==lastC[0]||nc[1]!==lastC[1]){
    localStorage.setItem('zoomLevel', nz);
    localStorage.setItem('mapCenter', JSON.stringify(nc));
    lastZ=nz; lastC=nc;
  }
});

// Borrar puntos y líneas persistentes
map.on('singleclick', evt => {
  const accion = accionSelect.value;
  const coord  = evt.coordinate;

  if (accion === 'Consultar') {
    console.log('Consultar');
    // 1) Buscar la feature más cercana
    const nearest = source.getClosestFeatureToCoordinate(coord);
    if (!nearest) return;

    // 2) Obtener propiedades menos la geometría
    const props = { ...nearest.getProperties() };
    delete props.geometry;

    // 3) Rellenar y mostrar el textarea
    infoTextarea.value = JSON.stringify(props, null, 2);

    // 4) Colocar el popup en la posición del clic (en píxeles)
    const pixel = map.getPixelFromCoordinate(coord);
    infoPopup.style.left = (pixel[0] + 10) + 'px';
    infoPopup.style.top  = (pixel[1] + 10) + 'px';
    infoPopup.style.display = 'block';
    return;
  }

  if (accion !== 'Borrar') return;

  // 1) Intentar borrar un punto
  const pt = source.getClosestFeatureToCoordinate(coord);
  if (pt && pt.getGeometry().getType() === 'Point') {
    // eliminar del source
    source.removeFeature(pt);

    // actualizar savedPoints
    let savedPts = JSON.parse(localStorage.getItem('savedPoints') || '[]');
    const pc = pt.getGeometry().getCoordinates();
    savedPts = savedPts.filter(o =>
      !(o.geometry.coordinates[0] === pc[0] && o.geometry.coordinates[1] === pc[1])
    );
    localStorage.setItem('savedPoints', JSON.stringify(savedPts));
    return;
  }

  // 2) Si no era un punto, buscamos la línea más cercana
  let minD = Infinity;
  let closestLine = null;
  source.getFeatures().forEach(f => {
    if (f.getGeometry().getType() === 'LineString') {
      // punto más cercano en la línea
      const cp = f.getGeometry().getClosestPoint(coord);
      const d = Math.hypot(cp[0] - coord[0], cp[1] - coord[1]);
      if (d < minD) {
        minD = d;
        closestLine = f;
      }
    }
  });

  const threshold = 10; // unidades de mapa (aprox metros en EPSG:3857)
  if (closestLine && minD <= threshold) {
    // eliminar la línea
    source.removeFeature(closestLine);

    // actualizar savedLines
    let savedLines = JSON.parse(localStorage.getItem('savedLines') || '[]');
    const coords = closestLine.getGeometry().getCoordinates();
    savedLines = savedLines.filter(obj =>
      JSON.stringify(obj.geometry.coordinates) !== JSON.stringify(coords)
    );
    localStorage.setItem('savedLines', JSON.stringify(savedLines));
  }
});


/*
document.getElementById('copyButton').addEventListener('click', () => {
  const points = JSON.parse(localStorage.getItem('savedPoints') || '[]');
  const lines  = JSON.parse(localStorage.getItem('savedLines') || '[]');

  const result = {
    puntos: points,
    lineas: lines
  };

  const text = JSON.stringify(result, null, 2); // Formateado

  navigator.clipboard.writeText(text)
    .then(() => alert('Datos copiados al portapapeles'))
    .catch(err => alert('Error al copiar: ' + err));
});
*/


document.getElementById('copyButton').addEventListener('click', () => {
  // 1) Calcula el extent (límites) de la vista actual
  const extent = map.getView().calculateExtent(map.getSize());

  // 2) Obtén solo las features visibles en ese extent
  const visibleFeatures = source.getFeaturesInExtent(extent);

  // 3) Separa puntos y líneas y transfórmalos a GeoJSON
  const puntos = [];
  const lineas = [];

  visibleFeatures.forEach(feature => {
    const geomType = feature.getGeometry().getType();
    const obj = geojsonFormat.writeFeatureObject(feature, {
      dataProjection:    'EPSG:25830',
      featureProjection: 'EPSG:3857'
    });

    if (geomType === 'Point') {
      puntos.push(obj);
    } else if (geomType === 'LineString') {
      lineas.push(obj);
    }
  });

  // 4) Construye el objeto final y cópialo
  const result = { puntos, lineas };
  const text   = JSON.stringify(result, null, 2);
  text = text.replace(/null/g, 'None');
  
  navigator.clipboard.writeText(text)
    .then(() => alert('Solo se han copiado las geometrías visibles'))
    .catch(err => alert('Error al copiar: ' + err));
});
