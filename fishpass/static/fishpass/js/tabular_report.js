$(document).ready( function () {
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

loadBarriers = function(geoJSON, project_uid, budget) {
  loadBarrierLayer(geoJSON);
  $.ajax({
    url: '/get_barrier_table_headers/',
    type: 'GET',
    dataType: 'json',
    success: function(response) {
      var header_list = response.header_list;
      loadBarrierTable(header_list, project_uid, budget);
    }
  })
};

queryBarrierReport = function(project_uid, barrier_id, budget) {
  $.ajax({
      url: '/get_barrier_report_list/' + project_uid + '/' + barrier_id + '/' + budget + '/',
      type: 'GET',
      success: function(response) {
        t = $('#barrier-table').DataTable();
        // for each feature, get barrier info and create the row and apply an ID corresponding to the FEATURE ID
        t.row.add(response.barrier_list).node().id = barrier_id;
        // for each row (or feature if in same loop) add click action to select and zoom to map feature when row is selected
          // In old solution, IDs were like "barrier-{{PAD ID}}-{{budget}}-tab" to be selected on map-click
          // We need both click on table impacts map, click on map impacts table.
        if (app.total_report_rows == t.rows().count()) {
          $('#table-spinner').hide();
          t.draw();
        } else {
          $('.dataTables_empty').html(t.rows().count() + ' of ' + app.total_report_rows + ' records loaded...');
        }
      },
      error: function(response) {
        console.log('Unable to get barrier results');
      }
  });
};

loadBarrierTable = function(headers, project_uid, budget) {
  // clear barrier table
  $('#barrier-table').html('');
  // create barrier table header row/columns
  var columns = []
  for (var i = 0; i < headers.length; i++){
    columns.push({ title: headers[i]});
  }
  if ( $.fn.DataTable.isDataTable( '#barrier-table' ) ) {
    $("#barrier-table").DataTable().destroy();
  }
  $('#barrier-table').DataTable(
    {
      // "bPaginate": false,
      // "info": false,
      "columns": columns
    }
  );
  barrierFeatures = app.map.layer.barriers.layer.getSource().getFeatures();
  app.report_rows_added = 0;
  app.total_report_rows = barrierFeatures.length;
  for (var i = 0; i < app.total_report_rows; i++){
    feature = barrierFeatures[i];
    bar_id = feature.get('id');
    feature.setId(bar_id);
    queryBarrierReport(project_uid, bar_id, budget);
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
        loadBarriers(response, project_uid, budget);
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

getBudgetReport = function(e){
  $('.budget-button.selected').removeClass('selected');
  $('#' + e.id).addClass('selected');
  //clear table
  $('#barrier-table').html('');
  $('#table-spinner').show()
  href_array = window.location.href.split('/');
  project_uid = href_array.pop();
  while (project_uid.length < 1) {
    project_uid = href_array.pop();
  }
  budget = e.id.split('-')[1];
  app.report.current_budget = budget;
  //reset agg results
  queryBudgetAggregateReport(project_uid, budget);
  //reset map
  $('#map-spinner').show()
  queryBudgetGeoJSON(project_uid, budget);
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
    loadBarriers(geojson, project_uid, budget);
  } else {
    queryBudgetAggregateReport(project_uid, budget);
    queryBudgetGeoJSON(project_uid, budget);
    // queryAllBarrierReports(project_uid, app.report.barrier_list, budget);
  }

};
