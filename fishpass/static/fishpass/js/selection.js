app.map.selection = {
  select: null,
  focusArea: [],
  setSelect: function(selectInteraction) {
    app.map.removeInteraction(app.map.selection.select);
    app.map.selection.select = selectInteraction;
    app.map.addInteraction(app.map.selection.select);
    app.map.selection.select.on('select', function(event) {
      var layer = app.map.selection.select.getLayer(event.selected[0]).get('id')
      if (event.selected.length > 0) {
        app.map.layer[layer].selectAction(event.selected[0]);
      }
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
      app.map.layer.huc12.layer,
      app.map.layer.county.layer,
    ],
    style: app.map.styles.transparent
  }),
}
