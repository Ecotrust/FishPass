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
    name: 'HUC2',
    report_methods: ['filter'],
    map_layer_id: 'huc02'
  },
  'huc04': {
    id: 'fishpasssupport.3wdtxzre',
    id_field: 'HUC4',
    name_field: 'Name',
    name: 'HUC4',
    report_methods: ['filter'],
    map_layer_id: 'huc04'
  },
  'huc06': {
    id: 'fishpasssupport.3wm8d6lr',
    id_field: 'HUC6',
    name_field: 'Name',
    name: 'HUC6',
    report_methods: ['filter'],
    map_layer_id: 'huc06'
  },
  'huc08': {
    id: 'fishpasssupport.0j3vqpr8',
    id_field: 'HUC8',
    name_field: 'Name',
    name: 'HUC8',
    report_methods: ['filter'],
    map_layer_id: 'huc08'
  },
  'huc10': {
    id: 'fishpasssupport.c2ulfosi',
    id_field: 'HUC10',
    name_field: 'Name',
    name: 'HUC10',
    report_methods: ['filter'],
    map_layer_id: 'huc10'
  },
  'huc12': {
    id: 'fishpasssupport.d1sxwwnb',
    id_field: 'HUC12',
    name_field: 'Name',
    name: 'HUC12',
    report_methods: ['filter'],
    map_layer_id: 'huc12'
  },
  'boundary': {
    id: 'fishpasssupport.5cy4ee66',
    id_field: 'ORIG_FID',
    name_field: 'ORIG_FID',
    name: 'FISHPass Boundary',
    report_methods: ['filter'],
    map_layer_id: 'boundary'
  },
  'region': {
    id: 'fishpasssupport.blmgjg0s',
    id_field: 'OBJECTID',
    name_field: 'Region_Lon',
    name: 'FISHPassRegions',
    report_methods: ['filter'],
    map_layer_id: 'region'
  },
  'chinook': {
    id: 'fishpasssupport.903ocprd',
    id_field: 'OBJECTID',
    name_field: 'ESU_DPS',
    name: 'Chinook ESUs: Other',
    report_methods: ['filter'],
    map_layer_id: 'chinook'
  },
  'chinook_spring': {
    id: 'fishpasssupport.68ypsukt',
    id_field: 'OBJECTID',
    name_field: 'ESU_DPS',
    name: 'Chinook ESUs: Spring',
    report_methods: ['filter'],
    map_layer_id: 'chinook_spring'
  },
  'chinook_fall': {
    id: 'fishpasssupport.0gdogtcv',
    id_field: 'OBJECTID',
    name_field: 'ESU_DPS',
    name: 'Chinook ESUs: Fall',
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
    name: 'Counties',
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
        name: app.mapbox.layers.huc02.name,
        title: app.mapbox.layers.huc02.name,
        unitType: 'HUC02',
        id: app.mapbox.layers.huc02.map_layer_id,
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
      selectAction: focusAreaSelectAction,
      hoverField: app.mapbox.layers.huc02.name_field
    },
    huc04: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.huc04.name,
        title: app.mapbox.layers.huc04.name,
        unitType: 'HUC04',
        id: app.mapbox.layers.huc04.map_layer_id,
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
      selectAction: focusAreaSelectAction,
      hoverField: app.mapbox.layers.huc04.name_field
    },
    huc06: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.huc06.name,
        title: app.mapbox.layers.huc06.name,
        unitType: 'HUC06',
        id: app.mapbox.layers.huc06.map_layer_id,
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
      selectAction: focusAreaSelectAction,
      hoverField: app.mapbox.layers.huc06.name_field
    },
    huc08: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.huc08.name,
        title: app.mapbox.layers.huc08.name,
        unitType: 'HUC08',
        id: app.mapbox.layers.huc08.map_layer_id,
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
      selectAction: focusAreaSelectAction,
      hoverField: app.mapbox.layers.huc08.name_field
    },
    huc10: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.huc10.name,
        title: app.mapbox.layers.huc10.name,
        unitType: 'HUC10',
        id: app.mapbox.layers.huc10.map_layer_id,
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
      selectAction: focusAreaSelectAction,
      hoverField: app.mapbox.layers.huc10.name_field
    },
    huc12: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.huc12.name,
        title: app.mapbox.layers.huc12.name,
        unitType: 'HUC12',
        id: app.mapbox.layers.huc12.map_layer_id,
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
      selectAction: focusAreaSelectAction,
      hoverField: app.mapbox.layers.huc12.name_field
    },
    county: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.county.name,
        title: app.mapbox.layers.county.name,
        unitType: 'County',
        id: app.mapbox.layers.county.map_layer_id,
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
      selectAction: focusAreaSelectAction,
      hoverField: app.mapbox.layers.county.name_field
    },
    boundary: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.boundary.name,
        title: app.mapbox.layers.boundary.name,
        unitType: 'Boundary',
        id: app.mapbox.layers.boundary.map_layer_id,
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
      selectAction: focusAreaSelectAction,
      // hoverField: app.mapbox.layers.boundary.name_field
      hoverField: '-'
    },
    region: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.region.name,
        title: app.mapbox.layers.region.name,
        unitType: 'Region',
        id: app.mapbox.layers.region.map_layer_id,
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
      selectAction: focusAreaSelectAction,
      hoverField: app.mapbox.layers.region.name_field
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
      selectAction: focusAreaSelectAction,
      hoverField: app.mapbox.layers.coho.name_field
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
      selectAction: focusAreaSelectAction,
      hoverField: app.mapbox.layers.chinook.name_field
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
      selectAction: focusAreaSelectAction,
      hoverField: app.mapbox.layers.chinook_spring.name_field
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
      selectAction: focusAreaSelectAction,
      hoverField: app.mapbox.layers.chinook_fall.name_field
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
      selectAction: focusAreaSelectAction,
      hoverField: app.mapbox.layers.steelhead.name_field
    },
    huc02_overlay: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.huc02.name,
        title: app.mapbox.layers.huc02.name,
        unitType: 'HUC02',
        id: app.mapbox.layers.huc02.map_layer_id,
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
    huc04_overlay: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.huc04.name,
        title: app.mapbox.layers.huc04.name,
        unitType: 'HUC04',
        id: app.mapbox.layers.huc04.map_layer_id,
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
    huc06_overlay: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.huc06.name,
        title: app.mapbox.layers.huc06.name,
        unitType: 'HUC06',
        id: app.mapbox.layers.huc06.map_layer_id,
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
    huc08_overlay: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.huc08.name,
        title: app.mapbox.layers.huc08.name,
        unitType: 'HUC08',
        id: app.mapbox.layers.huc08.map_layer_id,
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
    huc10_overlay: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.huc10.name,
        title: app.mapbox.layers.huc10.name,
        unitType: 'HUC10',
        id: app.mapbox.layers.huc10.map_layer_id,
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
    huc12_overlay: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.huc12.name,
        title: app.mapbox.layers.huc12.name,
        unitType: 'HUC12',
        id: app.mapbox.layers.huc12.map_layer_id,
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
    county_overlay: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.county.name,
        title: app.mapbox.layers.county.name,
        unitType: 'County',
        id: app.mapbox.layers.county.map_layer_id,
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
    boundary_overlay: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.boundary.name,
        title: app.mapbox.layers.boundary.name,
        unitType: 'Boundary',
        id: app.mapbox.layers.boundary.map_layer_id,
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
    region_overlay: {
      layer: new ol.layer.VectorTile({
        name: app.mapbox.layers.region.name,
        title: app.mapbox.layers.region.name,
        unitType: 'Region',
        id: app.mapbox.layers.region.map_layer_id,
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
    coho_overlay: {
      layer: new ol.layer.Tile({
        name: 'Coho Salmon ESU',
        title: 'Coho Salmon ESU',
        unitType: 'Coho',
        id: app.mapbox.layers.coho.map_layer_id,
        source: new ol.source.TileArcGISRest({
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_polygons08/MapServer',
          params: {'layers': 'show:3,4'},
          attributions: 'CDFW'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_polygons08/MapServer/',
          lyr_ids: [3,4],
          title: 'Coho Salmon ESU'
        }
      })
    },
    chinook_overlay: {
      layer: new ol.layer.Tile({
        name: 'Chinook Salmon Winter-run ESU, Sacramento River',
        title: 'Chinook Salmon Winter-run ESU, Sacramento River',
        unitType: 'Chinook',
        id: app.mapbox.layers.chinook.map_layer_id,
        source: new ol.source.TileArcGISRest({
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_polygons08/MapServer',
          params: {'layers': 'show:0'},
          attributions: 'CDFW'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_polygons08/MapServer/',
          lyr_ids: [0],
          title: 'Chinook Salmon Winter-run ESU, Sacramento River'
        }
      })
    },
    chinook_spring_overlay: {
      layer: new ol.layer.Tile({
        name: 'Chinook Salmon Spring-run ESU, Central Valley',
        title: 'Chinook Salmon Spring-run ESU, Central Valley',
        unitType: 'Chinook_Spring',
        id: app.mapbox.layers.chinook_spring.map_layer_id,
        source: new ol.source.TileArcGISRest({
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_polygons08/MapServer',
          params: {'layers': 'show:1'},
          attributions: 'CDFW'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_polygons08/MapServer/',
          lyr_ids: [1],
          title: 'Chinook Salmon Spring-run ESU, Central Valley'
        }
      })
    },
    chinook_fall_overlay: {
      layer: new ol.layer.Tile({
        name: 'Chinook Salmon Fall and late Fall-run ESU, Central Valley',
        title: 'Chinook Salmon Fall and late Fall-run ESU, Central Valley',
        unitType: 'Chinook_Fall',
        id: app.mapbox.layers.chinook_fall.map_layer_id,
        source: new ol.source.TileArcGISRest({
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_polygons08/MapServer',
          params: {'layers': 'show:2'},
          attributions: 'CDFW'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_polygons08/MapServer/',
          lyr_ids: [2],
          title: 'Chinook Salmon Fall and late Fall-run ESU, Central Valley'
        }
      })
    },
    steelhead_overlay: {
      layer: new ol.layer.Tile({
        name: 'Steelhead DPS',
        title: 'Steelhead DPS',
        unitType: 'Steelhead',
        id: app.mapbox.layers.steelhead.map_layer_id,
        source: new ol.source.TileArcGISRest({
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_polygons08/MapServer',
          params: {'layers': 'show:5,6,7,8,9,10'},
          attributions: 'CDFW'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_polygons08/MapServer/',
          // lyr_ids: [5,6,7,8,9,10], #RDH: All layers were redundant, but '10' had 1 more.
          lyr_ids: [10],
          title: 'Steelhead DPS'
        }
      })
    },

    upstream_potential: {
      layer: new ol.layer.Tile({
        name: 'Upstream',
        title: 'Upstream Potential Habitat',
        id: 'upstream',
        source: new ol.source.TileArcGISRest({
          url: 'https://maps.psmfc.org/server/rest/services/CFPF/CFPF_FISHPass/MapServer',
          params: {'layers': 'show:3'},
          attributions: 'PSMFC'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://maps.psmfc.org/server/rest/services/CFPF/CFPF_FISHPass/MapServer/',
          lyr_ids: [3],
          title: 'Upstream Potential Habitat'
        }
      })
    },
    baseline_habitat: {
      layer: new ol.layer.Tile({
        name: 'Basline Habitat',
        title: 'Baseline Fish Habitat',
        id: 'baseline',
        source: new ol.source.TileArcGISRest({
          url: 'https://maps.psmfc.org/server/rest/services/CFPF/CFPF_FISHPass/MapServer',
          params: {'layers': 'show:2'},
          attributions: 'PSMFC'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://maps.psmfc.org/server/rest/services/CFPF/CFPF_FISHPass/MapServer/',
          lyr_ids: [2],
          title: 'Baseline Fish Habitat'
        }
      })
    },
    assessment_database: {
      layer: new ol.layer.Tile({
        name: 'Assessment Database',
        title: 'Fish Passage Assessment Database',
        id: 'assessment_DB',
        source: new ol.source.TileArcGISRest({
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_PAD/PAD/MapServer',
          // params: {'layers': 'show:0'},
          attributions: 'CA DFG'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_PAD/PAD/MapServer/',
          lyr_ids: [0],
          title: 'Fish Passage Assessment Database'
        }
      })
    },
    protected_areas: {
      layer: new ol.layer.Tile({
        name: 'Protected Areas',
        title: 'Protected Areas',
        id: 'protected',
        source: new ol.source.TileArcGISRest({
          url: 'https://egis.fire.ca.gov/arcgis/rest/services/FRAP/ownership/MapServer',
          params: {'layers': 'show:0'},
          attributions: 'CAL FIRE'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://egis.fire.ca.gov/arcgis/rest/services/FRAP/ownership/MapServer/',
          lyr_ids: [0],
          title: 'Protected Areas'
        }
      })
    },
    nwst_2040_summer_stream_temps: {
      layer: new ol.layer.Tile({
        name: '2040 Summer Stream Temps',
        title: 'NorWeST 2040 Summer Stream Temps',
        id: 'summer_stream_temps_2040',
        source: new ol.source.TileArcGISRest({
          url: 'https://apps.fs.usda.gov/fsgisx02/rest/services/rmrs/RMRSAWAE_NorWeSTPredictedStreamTemperatures_2040_01/MapServer',
          params: {'layers': 'show:0'},
          attributions: 'Rocky Mountain Research Station – Air, Water, & Aquatic Environments'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://apps.fs.usda.gov/fsgisx02/rest/services/rmrs/RMRSAWAE_NorWeSTPredictedStreamTemperatures_2040_01/MapServer/',
          lyr_ids: [0],
          title: '2040 Summer Stream Temps'
        }
      })
    },
    nwst_2080_summer_stream_temps: {
      layer: new ol.layer.Tile({
        name: '2080 Summer Stream Temps',
        title: 'NorWeST 2080 Summer Stream Temps',
        id: 'summer_stream_temps_2080',
        source: new ol.source.TileArcGISRest({
          url: 'https://apps.fs.usda.gov/fsgisx02/rest/services/rmrs/RMRSAWAE_NorWeSTPredictedStreamTemperatures_2080_01/MapServer',
          params: {'layers': 'show:0'},
          attributions: 'Rocky Mountain Research Station – Air, Water, & Aquatic Environments'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://apps.fs.usda.gov/fsgisx02/rest/services/rmrs/RMRSAWAE_NorWeSTPredictedStreamTemperatures_2080_01/MapServer/',
          lyr_ids: [0],
          title: '2080 Summer Stream Temps'
        }
      })
    },
    historical_summer_stream_temps: {
      layer: new ol.layer.Tile({
        name: 'Historical Summer Stream Temps',
        title: 'NorWeST Historical Summer Stream Temps',
        id: 'summer_stream_temps_historical',
        source: new ol.source.TileArcGISRest({
          url: 'https://apps.fs.usda.gov/fsgisx02/rest/services/rmrs/RMRSAWAE_NorWeSTPredictedStreamTemperatures_MeanAugust_01/MapServer',
          params: {'layers': 'show:0'},
          attributions: 'Rocky Mountain Research Station – Air, Water, & Aquatic Environments'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://apps.fs.usda.gov/fsgisx02/rest/services/rmrs/RMRSAWAE_NorWeSTPredictedStreamTemperatures_MeanAugust_01/MapServer/',
          lyr_ids: [0],
          title: 'Historical Summer Stream Temps'
        }
      })
    },

    chinook_coastal_distribution: {
      layer: new ol.layer.Tile({
        name: 'Chinook Coastal Distribution: 2005',
        title: 'Chinook: California Coastal Distribution, 2005',
        id: 'chinook_coastal_distribution',
        source: new ol.source.TileArcGISRest({
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_pointslines09/MapServer',
          params: {'layers': 'show:6'},
          attributions: 'BDB'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_pointslines09/MapServer/',
          lyr_ids: [6],
          title: 'Chinook: California Coastal Distribution, 2005'
        }
      })
    },
    chinook_valley_distribution: {
      layer: new ol.layer.Tile({
        name: 'Chinook: Central Valley Spring-run Distribution, 2005',
        title: 'Chinook: Central Valley Spring-run Distribution, 2005',
        id: 'chinook_valley_distribution',
        source: new ol.source.TileArcGISRest({
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_pointslines09/MapServer',
          params: {'layers': 'show:7'},
          attributions: 'BDB'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_pointslines09/MapServer/',
          lyr_ids: [7],
          title: 'Chinook: Central Valley Spring-run Distribution, 2005'
        }
      })
    },
    coho_distribution: {
      layer: new ol.layer.Tile({
        name: 'Coho Distribution',
        title: 'Coho Distribution',
        id: 'coho_distribution',
        source: new ol.source.TileArcGISRest({
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_pointslines03/MapServer',
          params: {'layers': 'show:33'},
          attributions: 'BDB'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_pointslines03/MapServer/',
          lyr_ids: [33],
          title: 'Coho Distribution'
        }
      })
    },
    lamprey: {
      layer: new ol.layer.Tile({
        name: 'Pacific Lamprey Historical Range and Current Distribution',
        title: 'Pacific Lamprey Historical Range and Current Distribution',
        id: 'lamprey',
        source: new ol.source.TileArcGISRest({
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_pointslines26/MapServer',
          params: {'layers': 'show:5'},
          attributions: 'BDB'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_pointslines26/MapServer/',
          lyr_ids: [5],
          title: 'Pacific Lamprey Historical Range and Current Distribution'
        }
      })
    },
    summer_steelhead_distribution: {
      layer: new ol.layer.Tile({
        name: 'Summer Steelhead Distribution',
        title: 'Summer Steelhead Distribution',
        id: 'summer_steelhead_distribution',
        source: new ol.source.TileArcGISRest({
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_pointslines03/MapServer',
          params: {'layers': 'show:35'},
          attributions: 'BDB'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_pointslines03/MapServer/',
          lyr_ids: [35],
          title: 'Summer Steelhead Distribution'
        }
      })
    },
    winter_steelhead_distribution: {
      layer: new ol.layer.Tile({
        name: 'Winter Steelhead Distribution',
        title: 'Winter Steelhead Distribution',
        id: 'winter_steelhead_distribution',
        source: new ol.source.TileArcGISRest({
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_pointslines03/MapServer',
          params: {'layers': 'show:34'},
          attributions: 'BDB'
        }),
        visible: false,
        legend: {
          type: 'esrijson',
          url: 'https://map.dfg.ca.gov/arcgis/rest/services/Project_BIOS_Public/q_BIOS_Public_pointslines03/MapServer/',
          lyr_ids: [34],
          title: 'Winter Steelhead Distribution'
        }
      })
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
        // for (var feat of features) {
        for (var i = 0; i < features.length; i++) {
          var feat = features[i];
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
