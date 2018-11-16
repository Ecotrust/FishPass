app.map.scaleLine = new ol.control.ScaleLine();
app.map.scaleLine.setUnits('us');
app.map.addControl(app.map.scaleLine);

app.map.layerSwitcher = new ol.control.LayerSwitcher({
  tipLabel: 'Layers'
});

app.map.layerSwitcher.overlays = {};

app.map.toggleMapControls = function(show) {
    if (show) {
        $('.ol-control').removeClass('hide');
    } else {
        $('.ol-control').addClass('hide');
    }
}

app.map.enableLayer = function(layerName) {
  app.map.layer[layerName].layer.setVisible(true);
  $('#'+ app.map.layerSwitcher.overlays[layerName].checkboxId).prop('checked', true);
};

app.map.disableLayer = function(layerName) {
  app.map.layer[layerName].layer.setVisible(false);
  if (app.map.layerSwitcher.overlays[layerName]) {
    $('#'+ app.map.layerSwitcher.overlays[layerName].checkboxId).prop('checked', false);
  }
};

app.map.toggleLayer = function(layerName) {
  if ($('#'+ app.map.layerSwitcher.overlays[layerName].checkboxId).prop('checked')){
    app.map.disableLayer(layerName);
  } else {
    app.map.enableLayer(layerName);
  }
};

app.map.clearLayers = function() {
  var layerNames = Object.keys(app.map.layer);
  for (var i = 0; i < layerNames.length; i++) {
    app.map.disableLayer(layerNames[i]);
  }
}
