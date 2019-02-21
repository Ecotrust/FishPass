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
  'huc02': {
    id: 'fishpasssupport.4v1pyr4t',
    id_field: 'HUC2',
    name_field: 'Name',
    name: 'HUC 02',
    report_methods: ['filter'],
    map_layer_id: 'huc02'
  },
  'huc04': {
    id: 'fishpasssupport.3wdtxzre',
    id_field: 'HUC4',
    name_field: 'Name',
    name: 'HUC 04',
    report_methods: ['filter'],
    map_layer_id: 'huc04'
  },
  'huc06': {
    id: 'fishpasssupport.3wm8d6lr',
    id_field: 'HUC6',
    name_field: 'Name',
    name: 'HUC 06',
    report_methods: ['filter'],
    map_layer_id: 'huc06'
  },
  'huc08': {
    id: 'fishpasssupport.0j3vqpr8',
    id_field: 'HUC8',
    name_field: 'Name',
    name: 'HUC 08',
    report_methods: ['filter'],
    map_layer_id: 'huc08'
  },
  'huc10': {
    id: 'fishpasssupport.c2ulfosi',
    id_field: 'HUC10',
    name_field: 'Name',
    name: 'HUC 10',
    report_methods: ['filter'],
    map_layer_id: 'huc10'
  },
  'huc12': {
    id: 'fishpasssupport.d1sxwwnb',
    id_field: 'HUC12',
    name_field: 'Name',
    name: 'HUC 12',
    report_methods: ['filter'],
    map_layer_id: 'huc12'
  },
  'boundary': {
    id: 'fishpasssupport.5cy4ee66',
    id_field: 'ORIG_FID',
    name_field: 'ORIG_FID',
    name: 'Extent',
    report_methods: ['filter'],
    map_layer_id: 'boundary'
  },
  'region': {
    id: 'fishpasssupport.blmgjg0s',
    id_field: 'OBJECTID',
    name_field: 'Region_Lon',
    name: 'Regions',
    report_methods: ['filter'],
    map_layer_id: 'region'
  },
  'chinook': {
    id: 'fishpasssupport.903ocprd',
    id_field: 'OBJECTID',
    name_field: 'ESU_DPS',
    name: 'Chinook ESU',
    report_methods: ['filter'],
    map_layer_id: 'chinook'
  },
  'chinook_spring': {
    id: 'fishpasssupport.68ypsukt',
    id_field: 'OBJECTID',
    name_field: 'ESU_DPS',
    name: 'Spring Chinook ESU',
    report_methods: ['filter'],
    map_layer_id: 'chinook_spring'
  },
  'chinook_fall': {
    id: 'fishpasssupport.0gdogtcv',
    id_field: 'OBJECTID',
    name_field: 'ESU_DPS',
    name: 'Fall Chinook ESU',
    report_methods: ['filter'],
    map_layer_id: 'chinook_fall'
  },
  'coho': {
    id: 'fishpasssupport.5wz7x6s5',
    id_field: 'OBJECTID',
    name_field: 'ESU_DPS',
    name: 'Coho ESU',
    report_methods: ['filter'],
    map_layer_id: 'coho'
  },
  'steelhead': {
    id: 'fishpasssupport.18it32o6',
    id_field: 'OBJECTID',
    name_field: 'ESU_DPS',
    name: 'Steelhead DPS',
    report_methods: ['filter'],
    map_layer_id: 'steelhead'
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

focusAreaSelectAction = function(feat) {
  if (app.map.barrierClickInteraction.getFeatures().getArray().length == 0) {
    // unit type used for request params
    var unitType = app.map.selection.select.getLayer(feat).get('unitType');
    // id used for front end code
    var id = app.map.selection.select.getLayer(feat).get('id');
    var idField = app.mapbox.layers[id].id_field;
    var unitId = feat.getProperties()[idField];
    app.request.get_focus_area_geojson_by_type(unitType, unitId, function(response) {
      // response contain GeoJSON object
      var featId = response.features[0].properties.id;
      if (app.map.selection.focusArea.includes(featId)) {
        var indexOfId = app.map.selection.focusArea.indexOf(featId);
        app.map.selection.focusArea.splice(indexOfId,1);
        app.map.layer.focusArea.removeFeatureById(featId);
      } else {
        app.map.selection.focusArea.push(featId);
        app.map.layer.focusArea.addFeatures(response);
      };
      $('#id_target_area').val(app.map.selection.focusArea);
      app.viewModel.scenarios.scenarioFormModel.filters.target_area_input = app.map.selection.focusArea;
      $('#id_target_area').trigger('change');
    });
    // Allow user to re-click same feature
    app.map.selection.select.getFeatures().clear();
  } else {
    app.map.barrierClickInteraction.getFeatures().clear();
    app.map.barrierHoverInteraction.getFeatures().clear();
  }
};

app.map.layer = {
    huc02: {
      layer: new ol.layer.VectorTile({
        name: 'HUC 02',
        title: 'HUC 02',
        unitType: 'HUC02',
        id: 'huc02', // set id equal to x in app.map.layer.x
        source: new ol.source.VectorTile({
          attributions: 'USGS, USDA NRCS, US EPA',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.huc02.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },
    huc04: {
      layer: new ol.layer.VectorTile({
        name: 'HUC 04',
        title: 'HUC 04',
        unitType: 'HUC04',
        id: 'huc04', // set id equal to x in app.map.layer.x
        source: new ol.source.VectorTile({
          attributions: 'USGS, USDA NRCS, US EPA',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.huc04.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },
    huc06: {
      layer: new ol.layer.VectorTile({
        name: 'HUC 06',
        title: 'HUC 06',
        unitType: 'HUC06',
        id: 'huc06', // set id equal to x in app.map.layer.x
        source: new ol.source.VectorTile({
          attributions: 'USGS, USDA NRCS, US EPA',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.huc06.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },
    // TODO: add to mapbox
    huc08: {
      layer: new ol.layer.VectorTile({
        name: 'HUC 08',
        title: 'HUC 08',
        unitType: 'HUC08',
        id: 'huc08', // set id equal to x in app.map.layer.x
        source: new ol.source.VectorTile({
          attributions: 'USGS, USDA NRCS, US EPA',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.huc08.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },
    // TODO: add to mapbox
    huc10: {
      layer: new ol.layer.VectorTile({
        name: 'HUC 10',
        title: 'HUC 10',
        unitType: 'HUC10',
        id: 'huc10', // set id equal to x in app.map.layer.x
        source: new ol.source.VectorTile({
          attributions: 'USGS, USDA NRCS, US EPA',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.huc10.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
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
        unitType: 'HUC12',
        id: 'huc12', // set id equal to x in app.map.layer.x
        source: new ol.source.VectorTile({
          attributions: 'USGS, USDA NRCS, US EPA',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.huc12.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
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
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.county.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },

    boundary: {
      layer: new ol.layer.VectorTile({
        name: 'Extent',
        title: 'Extent',
        unitType: 'Boundary',
        id: 'boundary',
        source: new ol.source.VectorTile({
          attributions: '',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.boundary.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },
    region: {
      layer: new ol.layer.VectorTile({
        name: 'Region',
        title: 'Region',
        unitType: 'Region',
        id: 'region',
        source: new ol.source.VectorTile({
          attributions: '',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.region.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },
    coho: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.coho.name,
        title: app.mapbox.layers.coho.name,
        unitType: 'Coho',
        id: app.mapbox.layers.coho.map_layer_id,
        source: new ol.source.VectorTile({
          attributions: 'NOAA Fisheries, National Marine Fisheries Service, U.S. Department of Commerce, National Atmospheric and Oceanic Administration',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.coho.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },
    chinook: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.chinook.name,
        title: app.mapbox.layers.chinook.name,
        unitType: 'Chinook',
        id: app.mapbox.layers.chinook.map_layer_id,
        source: new ol.source.VectorTile({
          attributions: 'NOAA Fisheries, National Marine Fisheries Service, U.S. Department of Commerce, National Atmospheric and Oceanic Administration',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.chinook.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },
    chinook_spring: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.chinook_spring.name,
        title: app.mapbox.layers.chinook_spring.name,
        unitType: 'Chinook_Spring',
        id: app.mapbox.layers.chinook_spring.map_layer_id,
        source: new ol.source.VectorTile({
          attributions: 'NOAA Fisheries, National Marine Fisheries Service, U.S. Department of Commerce, National Atmospheric and Oceanic Administration',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.chinook_spring.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },
    chinook_fall: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.chinook_fall.name,
        title: app.mapbox.layers.chinook_fall.name,
        unitType: 'Chinook_Fall',
        id: app.mapbox.layers.chinook_fall.map_layer_id,
        source: new ol.source.VectorTile({
          attributions: 'NOAA Fisheries, National Marine Fisheries Service, U.S. Department of Commerce, National Atmospheric and Oceanic Administration',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.chinook_fall.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
        renderBuffer: 500
      }),
      selectAction: focusAreaSelectAction
    },
    steelhead: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.steelhead.name,
        title: app.mapbox.layers.steelhead.name,
        unitType: 'Steelhead',
        id: app.mapbox.layers.steelhead.map_layer_id,
        source: new ol.source.VectorTile({
          attributions: 'NOAA Fisheries, National Marine Fisheries Service, U.S. Department of Commerce, National Atmospheric and Oceanic Administration',
          format: new ol.format.MVT({
            featureClass: ol.Feature
          }),
          url: 'https://api.mapbox.com/v4/' + app.mapbox.layers.steelhead.id + '/{z}/{x}/{y}.mvt?access_token=' + app.mapbox.key
        }),
        style: app.map.styles.FocusArea,
        visible: false,
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
        style: app.map.styles.ReportPoint,
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
      clearFeatures: function() {
        app.map.layer.focusArea.layer.getSource().clear();
      },
      addFeatures: function(geojsonObject) {
        app.map.layer.focusArea.layer.getSource().addFeatures((new ol.format.GeoJSON()).readFeatures(geojsonObject));
      },
      removeFeatureById: function(id) {
        var features = app.map.layer.focusArea.layer.getSource().getFeatures();
        var featureToRemove;
        // loop through features for property id
        for (var feat of features) {
          var props = feat.getProperties();
          if (id == props.id) {
            featureToRemove = feat;
          }
        }
        app.map.layer.focusArea.layer.getSource().removeFeature(featureToRemove);
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
        title: 'Satellite Imagery',
        type: 'base',
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
