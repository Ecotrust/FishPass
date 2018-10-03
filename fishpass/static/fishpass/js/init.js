$( document ).ready(function() {
  app.panel.form.init();
  // get barrier layer ajax
  app.request.get_barrier_layer()
    .then(function(response) {
      var features = response.geojson.features;
      app.map.layer.barriers.addFeatures(features);
      app.map.addLayer(app.map.layer.barriers.layer);
    })
});
