app.map = mapSettings.getInitMap();

app.map.getView().setCenter([-13277300, 4497600]);
app.map.getView().setZoom(6);
app.map.getView().setMinZoom(5);
app.map.getView().setMaxZoom(19);

app.map.zoomToExtent = function zoomToExtent(extent) {
  ol.Map.prototype.getView.call(this).fit(extent, {duration: 1600});
}

app.map.styles = {
    Point: function(feature, resolution) {
      var radius = 5;
      if (resolution < 5) {
          radius = 12;
      } else if (resolution < 40) {
          radius = 7;
      }
      return new ol.style.Style({
        image: new ol.style.Circle({
            radius: radius,
            fill:  new ol.style.Fill({
                color: '#ffffff'
            }),
            stroke: new ol.style.Stroke({
                color: '#aaffff',
                width: 3,
            }),
        }),
        zIndex: 9
      });
    },
    PointSelected: function(feature, resolution) {
      var radius = 8;
      if (resolution < 5) {
          radius = 16;
      } else if (resolution < 40) {
          radius = 10;
      }
      return new ol.style.Style({
        image: new ol.style.Circle({
            radius: radius,
            fill:  new ol.style.Fill({
                color: '#4D4D4D',
            }),
            stroke: new ol.style.Stroke({
                color: '#ffffff',
                width: 3,
            }),
        }),
        zIndex: 10
      });
    },
    LineString: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#67b8c6',
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 8,
        }),
        zIndex: 2
    }),
    LineStringSelected: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#3a5675',
            width: 6,
        }),
        image: new ol.style.Circle({
            radius: 10,
            fill:  new ol.style.Fill({
                color: '#FCC'
            }),
            stroke: new ol.style.Stroke({
                color: '#3a5675',
                width: 5,
            }),
        }),
        zIndex: 4
    }),
    Polygon: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: 'rgba(0, 0, 0, 0)',
            // lineDash: [12],
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 0,   //Don't show!!!
            // width: 20,
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 0, 0, 0)'   //Don't show!!!
        }),
        zIndex: 2
    }),
    PolygonSelected: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#58595b',
            lineDash: [12],
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 1,
        }),
        fill: new ol.style.Fill({
            color: 'rgba(93, 116, 82, 0.45)'
        }),
        zIndex: 4
    }),
    FocusArea: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#303030',
            lineCap: 'butt',
            lineJoin: 'miter',
            width: 1,
            miterLimit: 2
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 0, 0, 0)'
        }),
        zIndex: 4
    }),
    FocusAreaSelect: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#aa6600',
            lineCap: 'butt',
            lineJoin: 'miter',
            width: 2,
            miterLimit: 2
        }),
        fill: new ol.style.Fill({
            color: 'rgba(180, 80, 0, 0.8)'
        }),
        zIndex: 4
    }),
    ReportArea: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#3A5675',
            lineCap: 'butt',
            lineJoin: 'miter',
            width: 3,
            miterLimit: 2
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 0, 0, 0.4)'
        }),
        zIndex: 4
    }),
    transparent: new ol.style.Style({
      stroke: new ol.style.Stroke({
        color: 'transparent',
      }),
      fill: new ol.style.Fill({
        color: 'transparent'
      })
    })
};

/**
 * [Map - Layers, Sources, Features]
 * @type {Object}
 */
app.mapbox.layers = {
  /**
   * [layers from mapbox]
   * @type {String} [use layer name from mapbox. layer name used in confirmSelection() to find layer]
   */
  // 'strm_sgmnts_all6-11-0i3yy4': {
  //   id: 'ucsrbsupport.ba73w0bq',
  //   id_field: 'EtID',
  //   name_field: 'Name',
  //   ppt_ID: 'ppt_ID',
  //   NEAR_FID: 'NEAR_FID',
  //   name: 'Streams',
  //   report_methods: ['select'],
  //   map_layer_id: 'streams'
  // },
  'huc10_3857': {
    id: 'ucsrbsupport.HUC10_3857',
    id_field: 'HUC_10',
    name_field: 'HU_10_Name',
    name: 'HUC 10',
    report_methods: ['filter'],
    map_layer_id: 'huc10'
  },
  'huc12_3857': {
    id: 'ucsrbsupport.HUC12_3857',
    id_field: 'HUC_12',
    name_field: 'HU_12_NAME',
    name: 'HUC 12',
    report_methods: ['filter'],
    map_layer_id: 'huc12'
  },
  'county': {
    id: 'fishpasssupport.2dc9ezel',
    id_field: 'CNTYIDFP',
    name_field: 'NAME',
    name: 'County',
    report_methods: ['filter'],
    map_layer_id: 'county'
  }
};

/**
 * [Set basin boundary]
 * @method
 * @param  {[type]} layer [description]
 * @return {[type]}       [description]
 */
app.map.setBoundaryLayer = function(layer) {
  if (app.map.boundary) {
    layer.removeFilter(app.map.boundary);
  }
  app.map.boundary = new ol.filter.Mask({
    feature: layer.getSource().getFeatureById('bound'),
    inner: false,
    fill: new ol.style.Fill({color:[58,86,117,0.45]})
  });
  layer.addFilter(app.map.boundary);
  app.map.boundary.set('active', true);
}

/**
 * [Mask for focus area selection]
 * @method
 * @param  {[type]} feat  [description]
 * @param  {[type]} layer [description]
 * @return {[type]}       [description]
 */
setFilter = function(feat, layer) {
  if (app.map.mask) {
    layer.removeFilter(app.map.mask);
  }
  app.map.mask = new ol.filter.Mask({feature: feat, inner: false, fill: new ol.style.Fill({color:[58,86,117,0.3]})});
  layer.addFilter(app.map.mask);
  app.map.mask.set('active', true);
  app.map.zoomToExtent(feat.getGeometry().getExtent());
}

app.map.setFilter = setFilter;

removeFilter = function() {
  if (app.map.mask) {
    app.map.mask.set('active', false);
  }
}

confirmationReceived = function() {
  if (app.state.step < 1 || app.state.step == 'reset') {
    app.state.setStep = 1;
  } else if (app.state.step == 2) {
    // if already on step 2 then a new pourpoint has been selected
    // we need to the reset the filter form and then go back to step 2
    app.state.setStep = 'reset';
    app.state.setStep = 2;
  } else {
    app.state.setStep = 2;
  }
  closeConfirmSelection(true);
}

app.map.closePopup = function() {
  if (app.map.hasOwnProperty('popup') && app.map.popup != false) {
    var element = app.map.popup.getElement();
    $(element).popover('hide');
    $(element).popover('dispose');
  }
  app.map.popup=false;
}

confirmSelection = function(feat, vector) {
  var props = feat.getProperties();
  props.layer = props.layer.split('.shp')[0];
  var mbLayer = app.mapbox.layers[props.layer];
  var layer = app.map.layer[mbLayer.map_layer_id];
  var features = (new ol.format.GeoJSON()).readFeatures(vector, {
    dataProjection: 'EPSG:3857',
    featureProjection: 'EPSG:3857'
  });

  var feature = features[0];

  // add features for use later in results
  app.map.layer.selectedFeature.layer.getSource().clear();
  app.map.layer.selectedFeature.layer.getSource().addFeature(feature);
  app.map.layer.selectedFeature.layer.setVisible(true);

  if (app.state.method == 'select') {
    // hack for when we have no ppt basins and default to HUC 12.
    setFilter(feature, app.map.layer.streams.layer);
  } else {
    setFilter(feature, layer.layer);
  }
}

closeConfirmSelection = function(accepted) {
  app.map.closePopup();
  if (!accepted) {
    app.map.popupLock = false;
    removeFilter();
  }
  app.map.selection.select.getFeatures().clear();
}

generateFilterPopup = function(content) {
   // return '<button class="btn btn-danger" type="button" onclick="closeConfirmSelection();">&times;</button>' +
   return '' +
    content + '<div class="popover-bottom-confirm-buttons">' +
    '<button class="btn btn-success" type="button" onclick="confirmationReceived()">Yes</button>' +
    '<button class="btn btn-danger" type="button" onclick="closeConfirmSelection(false);">No</button>' +
    '</div>';
}

app.scenarioInProgressCheck = function() {
  if (app.scenarioInProgress()) {
    app.map.mask.set('active', false);
    app.viewModel.scenarios.reset({cancel: true});
    app.state.setStep = 0; // go back to step one
  }
}

// get barrier layer ajax
// app.request.get_barrier_layer()
//   .then(function(response) {
//     if (response) {
//       var geojsonObject = response.geojson;
//       app.map.layer.barriers.addFeatures(geojsonObject);
//       app.map.addLayer(app.map.layer.barriers.layer);
//     }
//   })

focusAreaSelectAction = function(feat) {
  // unit type used for request params
  var unitType = app.map.selection.select.getLayer(feat).get('unitType');
  // id used for front end code
  var id = app.map.selection.select.getLayer(feat).get('id');
  var idField = app.mapbox.layers[id].id_field;
  var unitId = feat.getProperties()[idField];
  // TODO: smarter selction so that we only query for newly selected features
  app.request.get_focus_area_geojson_by_type(unitType, unitId, function(response) {
    app.map.selection.focusArea.push(response);
    // app.scenarioInProgressCheck();
    // if (app.state.step < 1) {
      // app.state.setStep = 1; // step forward in state
    // }
    // if (feat) {
      // confirmSelection(feat, vector);
    // }
    // if (app.state.step < 2) {
      // app.state.setStep = 2; // step forward in state
  }).done(function() {
    app.map.selection.focusArea.forEach(function(fc) {
      app.map.layer.focusArea.addFeatures(fc);
    });
  })
};

var drawSource = new ol.source.Vector();
var drawInteraction = new ol.interaction.Draw({
  source: drawSource,
  type: "Polygon",
});
var snapInteraction = new ol.interaction.Snap({source: drawSource});
var modifyInteraction = new ol.interaction.Modify({source: drawSource});

app.map.draw = {
  maxAcres: 100000,
  source: drawSource,
  draw: drawInteraction,
  snap: snapInteraction,
  modify: modifyInteraction,
  enable: function() {
    app.map.addInteraction(drawInteraction);
    app.map.addInteraction(snapInteraction);
    createMeasureTooltip();
    // map.on('pointermove', pointerMoveHandler);
  },
  enableEdit: function() {
    // app.map.removeInteraction(drawInteraction);
    app.map.addInteraction(modifyInteraction);
    // app.map.addInteraction(snapInteraction);
  },
  // disableEdit: function() {
  //   app.map.removeInteraction(modifyInteraction);
  //   app.map.removeInteraction(snapInteraction);
  // },
  disable: function() {
    app.map.removeInteraction(modifyInteraction);
    app.map.removeInteraction(drawInteraction);
    app.map.removeInteraction(snapInteraction);
    app.map.removeInteraction(app.map.draw.draw);
    // map.on('pointermove', pointerMoveHandler);
  },
  getDrawingArea: function() {
    var drawFeatures = app.map.draw.source.getFeatures();
    totalArea = 0;
    for (var i = 0; i < drawFeatures.length; i++) {
        totalArea += ol.Sphere.getArea(drawFeatures[i].getGeometry());
    }
    return totalArea;
  },
};

app.map.draw.draw.on('drawstart', function(e) {
  if (app.state.step == 0) {
    app.state.setStep = 1;
  }

  /** @type {ol.Coordinate|undefined} */
  // var tooltipCoord = e.coordinate;

  // app.map.draw.toolTipListener = e.feature.getGeometry().on('change', function(evt) {
  //   var geom = evt.target;
  //   var output = formatAreaToAcres(geom);
  //   var tooltipCoord = geom.getInteriorPoint().getCoordinates();
  //   app.map.draw.measureTooltipElement.innerHTML = output;
  //   app.map.draw.measureTooltip.setPosition(tooltipCoord);
  // });
});

app.map.draw.draw.on('drawend', function(e) {
  app.map.draw.enableEdit();
  app.panel.draw.finishDrawing();
});

app.map.draw.measureTooltipElement;
app.map.draw.measureTooltip;
app.map.draw.toolTipListener;

app.map.draw.modify.on('modifyend', function(e) {
  console.log('change');
  app.panel.draw.finishDrawing();
});

/**
 * Handle pointer move for drawing
 * @param {ol.MapBrowserEvent} evt The event.
 */
var pointerMoveHandler = function(evt) {
  if (evt.dragging) {
    return;
  }
  var drawFeatures = app.map.draw.source.getFeatures();
  if (drawFeatures.length > 0) {
    var geom = (drawFeatures[0].getGeometry());
  }
};

/**
 * Format area output.
 * @param {ol.geom.Polygon} polygon The polygon.
 * @return {string} Formatted area.
 */
var formatAreaToAcres = function(polygon) {
  var area = ol.Sphere.getArea(polygon);
  var output = Math.round(area * 0.00024710538146717) + ' ' + 'acres';
  return output;
};

/**
 * Creates a new measure tooltip
 */
function createMeasureTooltip() {
  if (app.map.draw.measureTooltipElement) {
    app.map.draw.measureTooltipElement.parentNode.removeChild(app.map.draw.measureTooltipElement);
  }
  app.map.draw.measureTooltipElement = document.createElement('div');
  app.map.draw.measureTooltipElement.className = 'tooltip tooltip-measure';
  app.map.draw.measureTooltip = new ol.Overlay({
    element: app.map.draw.measureTooltipElement,
    offset: [0, -15],
    positioning: 'bottom-center'
  });
  app.map.addOverlay(app.map.draw.measureTooltip);
}

app.map.layer = {
    // TODO: add to mapbox
    huc10: {
      layer: new ol.layer.VectorTile({
        name: 'HUC 10',
        title: 'HUC 10',
        id: 'huc10', // set id equal to x in app.map.layer.x
        source: new ol.source.VectorTile({
          attributions: 'NRCS',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.huc10_3857.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },
    // TODO: add to mapbox
    huc12: {
      layer: new ol.layer.VectorTile({
        name: 'HUC 12',
        title: 'HUC 12',
        id: 'huc12', // set id equal to x in app.map.layer.x
        source: new ol.source.VectorTile({
          attributions: 'NRCS',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.huc12_3857.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },

    county: {
      layer: new ol.layer.VectorTile({
        name: 'County',
        title: 'County',
        unitType: 'County',
        id: 'county',
        source: new ol.source.VectorTile({
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: `https://api.mapbox.com/v4/${app.mapbox.layers.county.id}/{z}/{x}/{y}.mvt?access_token=${app.mapbox.key}`
        }),
        style: app.map.styles.FocusArea,
        visible: true,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },

    // openlayers layer for barriers
    barriers: {
      layer: new ol.layer.Vector({
        name: 'Barriers',
        title: 'Barriers',
        id: 'barriers', // set id equal to x in app.map.layer.x
        style: app.map.styles.Point,
        visible: true,
      }),
      addFeatures: function(geojsonObject) {
        var vectorSource = new ol.source.Vector({
          features: (new ol.format.GeoJSON()).readFeatures(geojsonObject)
        });
        app.map.layer.barriers.layer.setSource(vectorSource);
      },
      selectAction: focusAreaSelectAction
    },

    // change wkt to geojson, update addfeatures ()
    // get barriers showing on map
    project: {
        layer: mapSettings.getInitFilterResultsLayer('project', false),
        source: function() {
            return app.map.layer.project.layer.getSource();
        },
        addFeatures: function(features) {
            features.forEach(function(el,i,arr) {
                // replace addWKTFeatures with ol add geojson features
                // add to layer
                app.map.layer.planningUnits.layer.addWKTFeatures(el);
            });
        },
    },

    focusArea: {
      layer: new ol.layer.Vector({
        name: 'focus area',
        title: 'focus area',
        id: 'focusArea',
        style: app.map.styles.PolygonSelected,
        visible: true,
        source: new ol.source.Vector(),
      }),
      addFeatures: function(geojsonObject) {
        app.map.layer.focusArea.layer.getSource().addFeatures((new ol.format.GeoJSON()).readFeatures(geojsonObject));
      },
    },

    spatialOrganization: {
      layer: new ol.layer.Vector({
        style: app.map.styles.FocusArea,
      }),
      addFeatures: function(geojsonObject) {
        var vectorSource = new ol.source.Vector({
          features: (new ol.format.GeoJSON()).readFeatures(geojsonObject)
        });
        app.map.layer.spatialOrganization.layer.setSource(vectorSource);
      },
    },

    scenarios: {
        layer: mapSettings.getInitFilterResultsLayer('scenarios', false),
        source: function() {
            return app.map.layer.scenarios.layer.getSource();
        }
    },

    selectedFeature: {
      layer: new ol.layer.Vector({
        source: new ol.source.Vector(),
        style: app.map.styles.LineStringSelected
      })
    },
    satellite: {
      layer: new ol.layer.Tile({
        name: 'Satellite',
        title: 'Satellite',
        id: 'satellite',
        preload: Infinity,
        source: new ol.source.XYZ({
          // url:'https://{1-4}.aerial.maps.cit.api.here.com/maptile/2.1/maptile/newest/satellite.day/{z}/{x}/{y}/256/png?app_id=p5jWgIultJxoVtXb03Xl&app_code=Cpj_I6Yx3J3yhVFE7aD12Q',
          url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
          // attributions: 'Map Tiles &copy; ' + new Date().getFullYear() + ' ' + '<a href="https://developer.here.com">HERE</a>',
          attributions: 'Sources: Esri, DigitalGlobe, Earthstar Geographics, CNES/Airbus DS, GeoEye, USDA FSA, USGS, Getmapping, Aerogrid, IGN, IGP, and the GIS User Community'
        }),
        visible: false
      })
    }
};

app.map.layer.scenarios.layer.set('id','focusArea');
app.map.layer.project.layer.set('id','project');
app.map.layer.barriers.layer.set('id', 'planningUnits');

app.map.overlays = false;
for (var i=0; i < app.map.getLayers().getArray().length; i++) {
  if (app.map.getLayers().getArray()[i].get('title') == 'Overlays') {
    app.map.overlays = app.map.getLayers().getArray()[i];
  }
}

if (app.map.overlays) {
  app.map.overlays.getLayers().push(app.map.layer.huc12.layer);
  app.map.overlays.getLayers().push(app.map.layer.huc10.layer);
  app.map.overlays.getLayers().push(app.map.layer.county.layer);
  // app.map.overlays.getLayers().push(app.map.layer.huc8.layer);
  // app.map.overlays.getLayers().push(app.map.layer.county.layer);
  // app.map.overlays.getLayers().push(app.map.layer.roads.layer);
}

app.map.scaleLine = new ol.control.ScaleLine();
app.map.scaleLine.setUnits('us');
app.map.addControl(app.map.scaleLine);

app.map.layerSwitcher = new ol.control.LayerSwitcher({
  tipLabel: 'Layers'
});

app.map.addControl(app.map.layerSwitcher);
app.map.addLayer(app.map.layer.selectedFeature.layer);
app.map.addLayer(app.map.layer.focusArea.layer);

app.map.toggleMapControls = function(show) {
    if (show) {
        $('.ol-control').removeClass('hide');
    } else {
        $('.ol-control').addClass('hide');
    }
}

app.map.layerSwitcher.overlays = {};
overlays = $(".layer-switcher .panel .group label:contains('Overlays')").parent().children('ul').children('.layer');
overlays.each(function() {
  label = this.children[1].innerText;
  id = this.children[0].id;
  lyr_obj = Object.values(app.map.layer).filter(function( obj ) { return obj.layer.get('title') == label;})[0];
  app.map.layerSwitcher.overlays[lyr_obj.layer.get('id')] = {
    checkboxId: id,
    layer: lyr_obj.layer
  };
});

if (app.map.getLayerGroup) {
  app.map.getLayerGroup().getLayers().forEach(function(lyr) {
    if (lyr.getProperties().title === 'Base maps') {
      lyr.getLayers().push(app.map.layer.satellite.layer);
    }
  });
}

app.map.forestFilterOverlays = {}

app.map.enableLayer = function(layerName) {
  app.map.layer[layerName].layer.setVisible(true);
  $('#'+ app.map.layerSwitcher.overlays[layerName].checkboxId).prop('checked', true);
};

app.map.disableLayer = function(layerName) {
  app.map.layer[layerName].layer.setVisible(false);
  if (app.map.layerSwitcher.overlays[layerName]) {
    $('#'+ app.map.layerSwitcher.overlays[layerName].checkboxId).prop('checked', false);
  }
};

app.map.toggleLayer = function(layerName) {
  if ($('#'+ app.map.layerSwitcher.overlays[layerName].checkboxId).prop('checked')){
    app.map.disableLayer(layerName);
  } else {
    app.map.enableLayer(layerName);
  }
};

app.map.clearLayers = function() {
  var layerNames = Object.keys(app.map.layer);
  for (var i = 0; i < layerNames.length; i++) {
    app.map.disableLayer(layerNames[i]);
  }
}

app.map.addScenario = function(vectors) {
  // app.map.draw.source.clear(true);
  vectors.forEach(function(vector) {
    vector.setStyle(new ol.style.Style({
      fill: new ol.style.Fill({
        color: [92,115,82,0.4]
      }),
      stroke: new ol.style.Stroke({
        color: [92,115,82,0.8],
        width: 2
      }),
      zIndex: 6
    }))
  });
  if (!app.map.hasOwnProperty('scenarioLayer')) {
    app.map.scenarioLayer = app.map.draw;
    app.map.scenarioLayer.removeAllFeatures = function() {
      app.map.scenarioLayer.source.clear();
      // app.map.scenarioLayer.source.clear;
    }
    app.map.scenarioLayer.getSource = function() {
      return app.map.scenarioLayer.source;
    }
  }
  app.map.scenarioLayer.removeAllFeatures();
  app.map.scenarioLayer.getSource().addFeatures(vectors);
};

app.map.dropPin = function(coords) {
  if (app.map.dropPin.source) {
    app.map.dropPin.source.clear();
  } else {
    app.map.dropPin.source = new ol.source.Vector();
    app.map.dropPin.layer = new ol.layer.Vector({
      source: app.map.dropPin.source
    });
    app.map.addLayer(app.map.dropPin.layer);
  }
  app.map.dropPin.pin = new ol.Feature({
    geometry: new ol.geom.Point(coords)
  });
  app.map.dropPin.pin.setStyle(app.map.styles.Point);
  app.map.dropPin.source.addFeature(app.map.dropPin.pin);
}

app.map.addDownstreamPptsToMap = function(pptsArray) {
  app.map.layer.resultPoints.layer.setVisible(true);
  app.map.layer.resultPoints.layer.setZIndex(10);
  for (var i = 0; i < pptsArray.length; i++) {
    let feature = new ol.Feature({
      geometry: new ol.geom.Point(pptsArray[i].geometry.coordinates),
      id: pptsArray[i].id
    });
    feature.setStyle(app.map.styles.PourPoint);
    app.map.layer.resultPoints.layer.getSource().addFeature(feature);
  }
  app.map.selection.setSelect(app.map.selection.selectResultsPourPoint);
};

app.map.addFocusAreaToMap = function(focus_area) {
  app.map.focus_area_feature = (new ol.format.GeoJSON()).readFeature(focus_area);
  app.map.scenarioLayer.getSource().addFeature(app.map.focus_area_feature);
  app.map.focus_area_feature.setStyle(app.map.styles.ReportArea);
  removeFilter();
  // setFilter(app.map.focus_area_feature, app.map.layer.resultPoints.layer);
}

app.map.addDrainageBasinToMap = function(basin_geom) {
  if (app.map.hasOwnProperty('drainage_basin') && app.map.scenarioLayer.getSource().getFeatures().indexOf(app.map.drainage_basin) != -1) {
    app.map.scenarioLayer.getSource().removeFeature(app.map.drainage_basin);
  }
  app.map.drainage_basin = (new ol.format.GeoJSON()).readFeature(basin_geom);
  app.map.scenarioLayer.getSource().addFeature(app.map.drainage_basin);
  app.map.drainage_basin.setStyle(app.map.styles.FocusArea);
}
