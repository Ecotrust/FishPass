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
  project_uid = href_array.pop();
  while (project_uid.length < 1) {
    project_uid = href_array.pop();
  }
  queryBarrierReport(project_uid, init_barrier_id, budget);

  app.map.initial_barriers_loaded = false;
  app.map.addLayer(app.map.layer.barriers.layer);
  mapSettings.configureLayer(app.map.layer.barriers.layer);
  // app.map.layer.barriers.layer.addGeoJSONFeatures(geojson);
  if (Object.keys(geojson).length > 0) {
    loadBarrierLayer(geojson);
  } else {
    queryBudgetGeoJSON(project_uid, budget);
    queryAllBarrierReports(project_uid, app.report.barrier_list, budget);
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

queryBudgetGeoJSON = function(project_uid, budget) {
  // TODO: Remove points from map
  app.map.layer.barriers.layer.setVisible(false);
  $.ajax({
      url: '/get_report_geojson_by_budget/' + project_uid + '/' + budget + '/',
      type: 'GET',
      dataType: 'json',
      success: function(response) {
        // Load points on map
        loadBarrierLayer(response);

        // Hide spinner
        $('#map-spinner').hide();
      },
      error: function(response) {
        alert('Unable to load results on map.');
        // Hide spinner
        $('#map-spinner').hide();
      }
  });
};

getBudgetGeoJSON = function(e) {
  // Show Spinner
  $('#map-spinner').show()
  href_array = window.location.href.split('/');
  project_uid = href_array.pop();
  while (project_uid.length < 1) {
    project_uid = href_array.pop();
  }
  budget = e.id.split('-')[1];
  queryBudgetGeoJSON(project_uid, budget);
  queryAllBarrierReports(project_uid, app.report.barrier_list, budget)
};

queryAllBarrierReports = function(project_uid, barrier_list, budget) {
  for (var i = 0; i < barrier_list.length; i++) {
    barrier_id = barrier_list[i];
    queryBarrierReport(project_uid, barrier_id, budget);
  }
};

queryBarrierReport = function(project_uid, barrier_id, budget) {
  $.ajax({
      url: '/get_barrier_report/' + project_uid + '/' + barrier_id + '/' + budget + '/',
      type: 'GET',
      success: function(response) {
        $('#barrier-' + barrier_id + '-' + budget).html(response);
      },
      error: function(response) {
        alert('Unable to get barrier results');
      }
  });
};

getBarrierReport = function(e) {
  href_array = window.location.href.split('/');
  project_uid = href_array.pop();
  while (project_uid.length < 1) {
    project_uid = href_array.pop();
  }
  barrier_id = e.id.split('-')[1];
  budget = e.id.split('-')[2];
  queryBarrierReport(project_uid, barrier_id, budget);
}
