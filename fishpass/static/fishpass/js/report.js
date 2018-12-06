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

app.report_init = function(geojson, budget, init_barrier_id) {
  href_array = window.location.href.split('/');
  report_uid = href_array.pop();
  while (report_uid.length < 1) {
    report_uid = href_array.pop();
  }
  queryBarrierReport(report_uid, init_barrier_id, budget);

  app.map.initial_barriers_loaded = false;
  app.map.addLayer(app.map.layer.barriers.layer);
  mapSettings.configureLayer(app.map.layer.barriers.layer);
  // app.map.layer.barriers.layer.addGeoJSONFeatures(geojson);
  if (Object.keys(geojson).length > 0) {
    loadBarrierLayer(geojson);
  } else {
    queryBudgetGeoJSON(report_uid, budget);
  }

};

loadBarrierLayer = function(geojson) {
  app.map.layer.barriers.addFeatures(geojson);
  app.map.layer.barriers.layer.setVisible(true);
  app.map.zoomToExtent(app.map.layer.barriers.layer.getSource().getExtent());

  // TODO: Do we need to reset map interaction?
  if (!app.map.initial_barriers_loaded) {
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
    app.map.initial_barriers_loaded = true;
  }
}

queryBudgetGeoJSON = function(report_uid, budget) {
  // TODO: Remove points from map
  app.map.layer.barriers.layer.setVisible(false);
  $.ajax({
      url: '/get_report_geojson_by_budget/' + report_uid + '/' + budget + '/',
      type: 'GET',
      dataType: 'json',
      success: function(response) {
        // Load points on map
        loadBarrierLayer(response);

        // Hide spinner
        $('#map-spinner').hide();
        alert('good foo!');
      },
      error: function(response) {
        alert('Unable to load results on map.');
        // Hide spinner
        $('#map-spinner').hide();
      }
  });
};

getBudgetGeoJSON = function(e) {
  alert('foo!');
  // Show Spinner
  $('#map-spinner').show()
  href_array = window.location.href.split('/');
  report_uid = href_array.pop();
  while (report_uid.length < 1) {
    report_uid = href_array.pop();
  }
  budget = e.id.split('-')[1];
  queryBudgetGeoJSON(report_uid, budget);
};

queryBarrierReport = function(report_uid, barrier_id, budget) {
  $.ajax({
      url: '/get_barrier_report/' + report_uid + '/' + barrier_id + '/' + budget + '/',
      type: 'GET',
      success: function(response) {
        // TODO: Replace contents of $('#barrier-' + barrier_id + '-' + budget)
        alert('good foo!');
      },
      error: function(response) {
        alert('Unable to get barrier results');
      }
  });
};

getBarrierReport = function(e) {
  href_array = window.location.href.split('/');
  report_uid = href_array.pop();
  while (report_uid.length < 1) {
    report_uid = href_array.pop();
  }
  barrier_id = e.id.split('-')[1];
  budget = e.id.split('-')[2];
  queryBarrierReport(report_uid, barrier_id, budget);
}
