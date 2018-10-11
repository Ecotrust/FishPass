app.map.selection = {
  select: null,
  setSelect: function(selectInteraction) {
    app.map.removeInteraction(app.map.selection.select);
    app.map.selection.select = selectInteraction;
    app.map.addInteraction(app.map.selection.select);
    app.map.selection.select.on('select', function(event) {
      console.log('selection event at ' + ol.coordinate.toStringHDMS(ol.proj.transform(
      event.mapBrowserEvent.coordinate, 'EPSG:3857', 'EPSG:4326'
    )));
    app.map.selection.select.getFeatures().forEach(function(feat) {
        var layer = app.map.selection.select.getLayer(feat).get('id');
        app.map.layer[layer].selectAction(feat);
    });
  }
};

app.map.interaction = {
  selectNone: new ol.interaction.Select({
    layers: []
  }),
  selectFilter: new ol.interaction.Select({
    layers: [
      app.map.layer.huc10.layer,
      app.map.layer.huc12.layer
      app.map.layer.county.layer,
    ],
    style: app.map.styles.PolygonSelected
  }),
}
