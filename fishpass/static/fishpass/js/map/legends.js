insertLegend(layer, html) {
  legend_title_div = '<div data-toggle="collapse" class="' + layer.id +
    '-legend-collapse-button legend-title" data-target="#' + layer.id +
    '-legend-collapse">' + layer.legend.title + '</div>';
  legend.html_container = '<div class="container" id="' + layer.id +
    '-legend-collapse" class="collapse show">' + html +
    '</div>'/
  $("#app-legend").append(legend_title_div);
  $("#app-legend").append(legend_html_container);
}

// Yanked and modified from MARCO.
getArcGISJSONLegend = function(layer) {
  url = layer.legend.url + 'legend?f=json';
  $.ajax({
      dataType: "json",
      url: url,
      type: 'GET',
      success: function(data) {
          html = {};
          if (data['layers']) {
              $.each(data['layers'], function(i, layerobj) {
                  if (parseInt(layerobj['layerId'], 10) === parseInt(layer.legend.lyr_id, 10)) {
                      html.legend = {'elements': []};
                      $.each(layerobj['legend'], function(j, legendobj) {
                          var swatchURL = layer.legend.url + layer.legend.lyr_id +'/images/'+legendobj['url']),
                              label = legendobj['label'];
                          if (label === "") {
                              label = layerobj['layerName'];
                          }
                          html.legend['elements'].push({'swatch': swatchURL, 'label': label});
                          //console.log(self.legend);
                      });
                  }
              });
              insert_legend(layer, html);
          } else {
              //debugger;
          }
      }
  });
}

app.map.showLegend = function(layer) {
  if (layer.hasOwnProperty('legend')) {
    if (layer.legend.type == 'esrijson') {
      getArcGISJSONLegend(layer);
    }
  }
}
