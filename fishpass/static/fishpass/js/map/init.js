app.map = mapSettings.getInitMap();

app.map.getView().setCenter([-13277300, 4497600]);
app.map.getView().setZoom(6);
app.map.getView().setMinZoom(5);
app.map.getView().setMaxZoom(19);

app.map.zoomToExtent = function zoomToExtent(extent) {
  ol.Map.prototype.getView.call(this).fit(extent, {duration: 1600});
}
