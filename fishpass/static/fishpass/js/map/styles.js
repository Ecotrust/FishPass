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
    }),
    Barrier: function(feature, resolution) {
        fill_color = feature.get('status_color');
        if (! fill_color || fill_color.length < 1) {
          fill_color = 'rgba(250,128,114,0.7)'; //Salmon
          status = feature.get('barrier_status');
          if (status && status.length > 1) {
            if (status == "Partial" || status == "Temporal & Partial") {
              fill_color = 'rgba(128,128,128,0.7)';
            } else if (status == "Total" || status == "Temporal & Total") {
              fill_color = 'rgba(255,0,0,0.7)';
            }
          }
        }
        user_override = feature.get('user_override');
        if (user_override) {
          stroke_color = 'yellow';
          stroke_width = 2;
          zIndex = 100;
        } else {
          stroke_color = 'black';
          stroke_width = 1;
          zIndex = 10;
        }
        return new ol.style.Style({
            image: new ol.style.Circle({
                radius: 6,
                fill: new ol.style.Fill({
                  color: fill_color,
                }),
                stroke: new ol.style.Stroke({
                  color: stroke_color,
                  width: stroke_width
                })
            }),
            zIndex: zIndex
        });
    },
    ReportPoint: function(feature, resolution) {
      var radius = 6;
      fill_color = feature.get('status_color');
      if (! fill_color || fill_color.length < 1) {
        status = feature.get('barrier_status');
        if (status && status.length > 1) {
          if (status == "Partial" || status == "Temporal & Partial") {
            fill_color = 'rgba(128,128,128,0.5)';
          } else if (status == "Total" || status == "Temporal & Total") {
            fill_color = 'rgba(255,0,0,0.5)';
          } else if (status == "Temporal") {
            fill_color = 'rgba(250,128,114,0.5)'; //Salmon
          } else {
            fill_color = 'rgba(250,128,114,0.5)'; //Salmon
          }
        } else {
          fill_color = 'rgba(250,128,114,0.5)'; //Salmon
        }
      }
      action = feature.get('action');
      if (action == 1 ) {
        stroke_color = 'green';
        zIndex = 100;
      } else {
        stroke_color = '#FA8072'
        zIndex = 0;
      }
      return new ol.style.Style({
          image: new ol.style.Circle({
              radius: radius,
              fill: new ol.style.Fill({
                color: fill_color,
              }),
              stroke: new ol.style.Stroke({
                color: stroke_color,
                width: 2
              })
          }),
          zIndex: zIndex
      });
    }
};
