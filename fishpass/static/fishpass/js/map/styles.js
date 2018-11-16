app.map.styles = {
    Point: function(feature, resolution) {
      var radius = 5;
      if (resolution < 5) {
          radius = 12;
      } else if (resolution < 40) {
          radius = 7;
      }
      return new ol.style.Style({
        image: new ol.style.Circle({
            radius: radius,
            fill:  new ol.style.Fill({
                color: '#ffffff'
            }),
            stroke: new ol.style.Stroke({
                color: '#aaffff',
                width: 3,
            }),
        }),
        zIndex: 9
      });
    },
    PointSelected: new ol.style.Style({
        image: new ol.style.Circle({
            radius: 8,
            fill:  new ol.style.Fill({
                color: 'rgba(0,255,0,0.5)',
            }),
            stroke: new ol.style.Stroke({
                color: 'green',
                width: 3,
            }),
        }),
        zIndex: 10
    }),
    LineString: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#67b8c6',
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 8,
        }),
        zIndex: 2
    }),
    LineStringSelected: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#3a5675',
            width: 6,
        }),
        image: new ol.style.Circle({
            radius: 10,
            fill:  new ol.style.Fill({
                color: '#FCC'
            }),
            stroke: new ol.style.Stroke({
                color: '#3a5675',
                width: 5,
            }),
        }),
        zIndex: 4
    }),
    Polygon: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: 'rgba(0, 0, 0, 0)',
            // lineDash: [12],
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 0,   //Don't show!!!
            // width: 20,
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 0, 0, 0)'   //Don't show!!!
        }),
        zIndex: 2
    }),
    PolygonSelected: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#58595b',
            lineDash: [12],
            lineCap: 'cap',
            lineJoin: 'miter',
            width: 1,
        }),
        fill: new ol.style.Fill({
            color: 'rgba(93, 116, 82, 0.45)'
        }),
        zIndex: 4
    }),
    FocusArea: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#303030',
            lineCap: 'butt',
            lineJoin: 'miter',
            width: 1,
            miterLimit: 2
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 0, 0, 0)'
        }),
        zIndex: 4
    }),
    FocusAreaSelect: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#aa6600',
            lineCap: 'butt',
            lineJoin: 'miter',
            width: 2,
            miterLimit: 2
        }),
        fill: new ol.style.Fill({
            color: 'rgba(180, 80, 0, 0.8)'
        }),
        zIndex: 4
    }),
    ReportArea: new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#3A5675',
            lineCap: 'butt',
            lineJoin: 'miter',
            width: 3,
            miterLimit: 2
        }),
        fill: new ol.style.Fill({
            color: 'rgba(0, 0, 0, 0.4)'
        }),
        zIndex: 4
    }),
    transparent: new ol.style.Style({
      stroke: new ol.style.Stroke({
        color: 'transparent',
      }),
      fill: new ol.style.Fill({
        color: 'transparent'
      })
    })
};
