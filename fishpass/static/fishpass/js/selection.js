app.map.selection = {
  select: null,
  focusArea: [],
  setSelect: function(selectInteraction) {
    app.map.removeInteraction(app.map.selection.select);
    app.map.selection.select = selectInteraction;
    app.map.addInteraction(app.map.selection.select);
    app.map.selection.select.on('select', function(event) {
      console.log('selection event at ' + ol.coordinate.toStringHDMS(ol.proj.transform(event.mapBrowserEvent.coordinate, 'EPSG:3857', 'EPSG:4326')));
      // get number of select features
      var selectLength = app.map.selection.select.getFeatures().getLength();
      if (selectLength > 0) {
        var lastSelected = app.map.selection.select.getFeatures().getArray()[selectLength - 1];
        var layer = app.map.selection.select.getLayer(lastSelected).get('id');
        app.map.layer[layer].selectAction(lastSelected);
      } else {
        app.map.layer.focusArea.clearFeatures();
        app.map.selection.focusArea = [];
      }
      console.log(selectLength);
      console.log(app.map.selection.select);
    });
  }
};

app.map.interaction = {
  selectNone: new ol.interaction.Select({
    layers: []
  }),
  selectFilter: new ol.interaction.Select({
    toggleCondition: ol.events.condition.click,
    layers: [
      app.map.layer.huc10.layer,
      app.map.layer.huc12.layer,
      app.map.layer.county.layer,
    ],
    style: app.map.styles.transparent
  }),
}
