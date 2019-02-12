$(document).ready( function () {
    $('#foo-table').DataTable(
      {
        "bPaginate": false,
        "info": false
      }
    );
    $('#net-gain-card').children().tooltip(
      {
        placement: 'right',
        title: 'This is the sum of the estimated habitat upstream of each barrier suggested for treatment that have been “weighted/changed” using cumulative passability.'
      }
    );
} );

queryAllBarrierReports = function(project_uid, barrier_list, budget) {
  if (!app.report.budgets_loaded.includes(budget)){
    app.report.budgets_loaded.push(budget);
    for (var i = 0; i < barrier_list.length; i++) {
      barrier_id = barrier_list[i];
      queryBarrierReport(project_uid, barrier_id, budget);
    }
  }
};

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

        queryAllBarrierReports(project_uid, app.report.barrier_list, budget);
      },
      error: function(response) {
        alert('Unable to load results on map.');
        // Hide spinner
        $('#map-spinner').hide();
      }
  });
};

queryBudgetAggregateReport = function(project_uid, budget){
  $('#agg-results-spinner').show();
  $.ajax({
    url: '/get_report_summary_by_budget/' + project_uid + '/' + budget + '/',
    type: 'GET',
    success: function(response) {
      $('#agg-report').html(response);
      $('#agg-results-spinner').hide();
    }
  })
};

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
  if (Object.keys(geojson).length > 0) {
    loadBarrierLayer(geojson);
  } else {
    queryBudgetGeoJSON(project_uid, budget);
    queryBudgetAggregateReport(project_uid, budget);
    // queryAllBarrierReports(project_uid, app.report.barrier_list, budget);
  }

};
