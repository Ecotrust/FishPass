barrierHoverSelectAction = function(feat) {
  if (feat) {
    var pixel = app.map.getPixelFromCoordinate(feat.getGeometry().getCoordinates());
    console.log(pixel);
    app.map.barrierInfo.tooltip('hide')
    .css({
      left: pixel[0] + 'px',
      top: (pixel[1]-15) + 'px'
    })
    .attr('data-original-title', feat.get('site_name') + " (" + feat.get('stream_name') +")")
    .tooltip('show');
  } else {
    app.map.barrierInfo.tooltip('hide');
  }
};

app.report_init = function(geojson) {
  app.map.addLayer(app.map.layer.barriers.layer);
  mapSettings.configureLayer(app.map.layer.barriers.layer);
  // app.map.layer.barriers.layer.addGeoJSONFeatures(geojson);
  app.map.layer.barriers.addFeatures(geojson);
  app.map.layer.barriers.layer.setVisible(true);
  app.map.zoomToExtent(app.map.layer.barriers.layer.getSource().getExtent());

  app.map.barrierHoverInteraction = new ol.interaction.Select({
    condition: ol.events.condition.pointerMove,
    layers: [
      app.map.layer.barriers.layer
    ],
    style: app.map.styles.PointSelected
  });

  app.map.barrierSelected = false;

  $('#map').prepend('<div id="barrier-info"></div>');
  app.map.barrierInfo = $('#barrier-info');
  setTimeout(function() {
    app.map.barrierInfo.tooltip({
      animation: false,
      trigger: 'manual'
    });
  }, 50);

  app.map.addInteraction(app.map.barrierHoverInteraction);

  app.map.barrierHoverInteraction.on('select', function(event) {
    barrierHoverSelectAction(event.selected[0]);
  });


};
