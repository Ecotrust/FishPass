// app.map = mapSettings.getInitMap();
app.map = new madronaMap({
  target: 'map',
  // interactions: ol.interaction.defaults({mouseWheelZoom:false}),
  layers: [
    new ol.layer.Group({
      'title': 'Base maps',
      layers: [
        new ol.layer.Tile({
          title: 'OSM Base Layer',
          source: new ol.source.OSM(),
          name: 'OSM Base Layer',
          type: 'base'
        }),
        new ol.layer.Tile({
          title: 'ESRI Topo',
          source: new ol.source.XYZ({
            url: 'http://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.png'
          }),
          name: 'OSM Base Layer',
          type: 'base'
        })
      ],
    }),
    new ol.layer.Group({
      title: 'Overlays',
      layers: []
    })
  ],
  view: new ol.View({
    center: [0, 0],
    zoom: 2
  })
});

// app.map.getView().setCenter([-13277300, 4497600]);
// app.map.getView().setZoom(6);
// app.map.getView().setMinZoom(5);
// app.map.getView().setMaxZoom(19);

app.map.zoomToExtent = function zoomToExtent(extent) {
  ol.Map.prototype.getView.call(this).fit(extent, {duration: 1600});
}
