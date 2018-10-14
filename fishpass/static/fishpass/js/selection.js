app.map.selection = {
  select: null,
  focusArea: [],
  setSelect: function(selectInteraction) {
    app.map.removeInteraction(app.map.selection.select);
    app.map.selection.select = selectInteraction;
    app.map.addInteraction(app.map.selection.select);
    app.map.selection.select.on('select', function(event) {
      console.log('selection event at ' + ol.coordinate.toStringHDMS(ol.proj.transform(event.mapBrowserEvent.coordinate, 'EPSG:3857', 'EPSG:4326')));
      // clear previous focus area selection
      app.map.selection.focusArea = [];
      app.map.selection.select.getFeatures().forEach(function(feat) {
          var layer = app.map.selection.select.getLayer(feat).get('id');
          app.map.layer[layer].selectAction(feat);
      });
      for (var i = 0; i < app.map.selection.focusArea.length; i++) {
        console.log('yo');
      };
      console.log('yo2');
      // app.map.layer.focusArea.addFeatures(app.map.selection.focusArea);
    });
  }
};

app.map.interaction = {
  selectNone: new ol.interaction.Select({
    layers: []
  }),
  selectFilter: new ol.interaction.Select({
    addCondition: ol.events.condition.singleClick,
    layers: [
      app.map.layer.huc10.layer,
      app.map.layer.huc12.layer,
      app.map.layer.county.layer,
    ],
    style: app.map.styles.transparent
  }),
}
