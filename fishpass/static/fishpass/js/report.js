barrierHoverSelectAction = function(feat) {
  if (feat) {
    var pixel = app.map.getPixelFromCoordinate(feat.getGeometry().getCoordinates());
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

barrierClickInteraction = function(feat) {
  if (feat) {
    barrier_id = feat.getId();
    if (!barrier_id) {
      barrier_id = feat.get('pad_id');
      feat.setId(barrier_id);
    }
    $('#barrier-' + barrier_id + '-' + app.report.current_budget + '-tab').trigger('click');
    app.map.barrierSelected = barrier_id;
  }
}

check_for_download = function(project_uid, type, time) {
  $.ajax({
    url: '/check_download_report/',
    type: 'GET',
    data: {
        project_uid: project_uid,
        report_type: type,
        timer: time
    },
    success: function(response) {
      if (response.hasOwnProperty('available') && response.available == true) {
        if (type == 'all') {
          $('#download-report-button').on('click', function() {alert('File is ready')});
          $('#download-report-button').html('Download Full Results');
          $('#download-report-button').prop('disabled', false);
        }
        if (type == 'filtered') {
          $('#download-filtered-report-button').on('click', function() {alert('File is ready')});
          $('#download-filtered-report-button').html('Download Filtered Results');
          $('#download-filtered-report-button').prop('disabled', false);
        }
      } else {
        setTimeout(function() {
          time = time + 5; // Wait time in seconds. After 60 server to try re-recreating the missing file.
          check_for_download(project_uid, type, time);
        }, 5000);
      }
    },
    error: function(response) {
      console.log('failed to check if report (' + type + ') was ready');
    }
  })
}

app.report_init = function(geojson, budget) {
  $('#download-report-button').on('click', function() {alert('Download Functionality Coming Soon!')});
  $('#download-filtered-report-button').on('click', function() {alert('Download Functionality Coming Soon!')});
  app.map.barrierSelected = false;
  app.report.current_budget = budget;
  app.report.budgets_loaded = [];
  href_array = window.location.href.split('/');
  project_uid = href_array.pop();
  while (project_uid.length < 1) {
    project_uid = href_array.pop();
  }

  check_for_download(project_uid, 'all', 0);
  check_for_download(project_uid, 'filtered', 0);


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

    app.map.barrierClickInteraction = new ol.interaction.Select({
      layers: [
        app.map.layer.barriers.layer
      ],
      style: app.map.styles.ReportBarrierSelected
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
    app.map.addInteraction(app.map.barrierClickInteraction);

    app.map.barrierHoverInteraction.on('select', function(event) {
      barrierHoverSelectAction(event.selected[0]);
    });
    app.map.barrierClickInteraction.on('select', function(event) {
      barrierClickInteraction(event.selected[0]);
    });
    app.map.on('click', function(event) {
      if (app.map.barrierSelected) {
        event.preventDefault();
        event.stopPropagation();
        app.map.barrierClickInteraction.getFeatures().clear();
        app.map.barrierSelected = false;
      }
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
  href_array = window.location.href.split('/');
  project_uid = href_array.pop();
  while (project_uid.length < 1) {
    project_uid = href_array.pop();
  }
  budget = e.id.split('-')[1];
  app.report.current_budget = budget;
  // Show Spinner
  $('#map-spinner').show()
  queryBudgetGeoJSON(project_uid, budget);
  queryAllBarrierReports(project_uid, app.report.barrier_list, budget)
};

queryAllBarrierReports = function(project_uid, barrier_list, budget) {
  if (!app.report.budgets_loaded.includes(budget)){
    app.report.budgets_loaded.push(budget);
    for (var i = 0; i < barrier_list.length; i++) {
      barrier_id = barrier_list[i];
      queryBarrierReport(project_uid, barrier_id, budget);
    }
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
