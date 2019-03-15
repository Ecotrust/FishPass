app.map.overlays = false;
for (var i=0; i < app.map.getLayers().getArray().length; i++) {
  if (app.map.getLayers().getArray()[i].get('title') == 'Overlays') {
    app.map.overlays = app.map.getLayers().getArray()[i];
  }
  if (app.map.getLayers().getArray()[i].get('title') != 'Overlays' && app.map.getLayers().getArray()[i].get('title') != "Base maps") {
    app.map.selections = app.map.getLayers().getArray()[i]
  }
}

if (app.map.overlays) {
  // app.map.overlays.getLayers().push(app.map.layer.assessment_database.layer);
  app.map.overlays.getLayers().push(app.map.layer.protected_areas.layer);
  app.map.overlays.getLayers().push(app.map.layer.historical_summer_stream_temps.layer);
  app.map.overlays.getLayers().push(app.map.layer.nwst_2040_summer_stream_temps.layer);
  app.map.overlays.getLayers().push(app.map.layer.nwst_2080_summer_stream_temps.layer);
  app.map.overlays.getLayers().push(app.map.layer.baseline_habitat.layer);
  app.map.overlays.getLayers().push(app.map.layer.upstream_potential.layer);
  app.map.overlays.getLayers().push(app.map.layer.steelhead_overlay.layer);
  app.map.overlays.getLayers().push(app.map.layer.chinook_fall_overlay.layer);
  app.map.overlays.getLayers().push(app.map.layer.chinook_spring_overlay.layer);
  app.map.overlays.getLayers().push(app.map.layer.chinook_overlay.layer);
  app.map.overlays.getLayers().push(app.map.layer.coho_overlay.layer);
  app.map.overlays.getLayers().push(app.map.layer.region_overlay.layer);
  app.map.overlays.getLayers().push(app.map.layer.county_overlay.layer);
  app.map.overlays.getLayers().push(app.map.layer.boundary_overlay.layer);
  app.map.overlays.getLayers().push(app.map.layer.huc12_overlay.layer);
  app.map.overlays.getLayers().push(app.map.layer.huc10_overlay.layer);
  app.map.overlays.getLayers().push(app.map.layer.huc08_overlay.layer);
  app.map.overlays.getLayers().push(app.map.layer.huc06_overlay.layer);
  app.map.overlays.getLayers().push(app.map.layer.huc04_overlay.layer);
  app.map.overlays.getLayers().push(app.map.layer.huc02_overlay.layer);
}

if (app.map.selections) {
  app.map.selections.getLayers().push(app.map.layer.huc02.layer);
  app.map.selections.getLayers().push(app.map.layer.huc04.layer);
  app.map.selections.getLayers().push(app.map.layer.huc06.layer);
  app.map.selections.getLayers().push(app.map.layer.huc08.layer);
  app.map.selections.getLayers().push(app.map.layer.huc12.layer);
  app.map.selections.getLayers().push(app.map.layer.huc10.layer);
  app.map.selections.getLayers().push(app.map.layer.county.layer);
  app.map.selections.getLayers().push(app.map.layer.boundary.layer);
  app.map.selections.getLayers().push(app.map.layer.region.layer);
  app.map.selections.getLayers().push(app.map.layer.coho.layer);
  app.map.selections.getLayers().push(app.map.layer.chinook.layer);
  app.map.selections.getLayers().push(app.map.layer.chinook_spring.layer);
  app.map.selections.getLayers().push(app.map.layer.chinook_fall.layer);
  app.map.selections.getLayers().push(app.map.layer.steelhead.layer);
  // app.map.selections.getLayers().push(app.map.layer.county.layer);
  // app.map.selections.getLayers().push(app.map.layer.roads.layer);
}

app.map.addLayer(app.map.layer.selectedFeature.layer);
app.map.addLayer(app.map.layer.focusArea.layer);

app.map.addControl(app.map.layerSwitcher);

selections = $(".layer-switcher .panel .group label:contains('Selection')").parent().children('ul').children('.layer');
selections.each(function() {
  label = this.children[1].innerText;
  id = this.children[0].id;
  lyr_obj = Object.values(app.map.layer).filter(function( obj ) { return obj.layer.get('title') == label;})[0];
  app.map.layerSwitcher.selections[lyr_obj.layer.get('id')] = {
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


app.map.addFocusAreaToMap = function(focus_area) {
  app.map.focus_area_feature = (new ol.format.GeoJSON()).readFeature(focus_area);
  app.map.scenarioLayer.getSource().addFeature(app.map.focus_area_feature);
  app.map.focus_area_feature.setStyle(app.map.styles.ReportArea);
  removeFilter();
  // setFilter(app.map.focus_area_feature, app.map.layer.resultPoints.layer);
}
