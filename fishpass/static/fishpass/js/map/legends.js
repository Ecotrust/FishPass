insertLegend = function(layer, html) {
  legend_title_div = '<div data-toggle="collapse" class="' + layer.get('id') +
    '-legend-collapse-button legend-title" data-target="#' + layer.get('id') +
    '-legend-collapse" id="' + layer.get('id') + '-legend-header">' +
    layer.get('legend').title + '</div>';
  legend_html_container = '<div class="container collapse" id="' + layer.get('id') +
    '-legend-collapse" class="collapse">' + html +
    '</div>';
  $("#legend-collapse").append(legend_title_div);
  $("#legend-collapse").append(legend_html_container);
};

removeLegend = function(layerId) {
  $('#' + layerId + '-legend-header').remove();
  $('#' + layerId + '-legend-collapse').remove();
}

// Yanked and modified from MARCO.
getArcGISJSONLegend = function(layer) {
  url = layer.get('legend').url + 'legend?f=json';
  $.ajax({
      dataType: "json",
      url: url,
      type: 'GET',
      success: function(data) {
          html = "";
          if (data['layers']) {
              $.each(data['layers'], function(i, layerobj) {
                  if (parseInt(layerobj['layerId'], 10) === parseInt(layer.get('legend').lyr_id, 10)) {
                      $.each(layerobj['legend'], function(j, legendobj) {
                          var swatchURL = layer.get('legend').url + layer.get('legend').lyr_id +'/images/'+legendobj['url'],
                              label = legendobj['label'];
                          if (label === "") {
                              label = layerobj['layerName'];
                          }
                          html += '<div class="row"> \n' +
'                                    <div class="col-3">\n' +
'                                      <p><img class="legend-barrier" src="' + swatchURL + '"></p>\n' +
'                                    </div> <!-- column 1 -->\n' +
'                                    <div class="col-9">\n' +
'                                      <p>' + label + '</p>\n' +
'                                    </div> <!-- column 2 -->\n' +
'                                  </div>';
                      });
                  }
              });
              insertLegend(layer, html);
          }
      }
  });
}
