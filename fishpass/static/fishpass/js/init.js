$( document ).ready(function() {
  app.panel.form.init();
  // get barrier layer ajax
  app.request.get_barrier_layer()
    .then(function(response) {
      var geojsonObject = response.geojson;
      app.map.layer.barriers.addFeatures(geojsonObject);
      app.map.addLayer(app.map.layer.barriers.layer);
    })
});
