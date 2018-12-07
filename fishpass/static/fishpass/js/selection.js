app.map.selection = {
  select: null,
  focusArea: [],
  setSelect: function(selectInteraction) {
    app.map.removeInteraction(app.map.selection.select);
    app.map.selection.select = selectInteraction;
    app.map.addInteraction(app.map.selection.select);
    app.map.selection.select.on('select', function(event) {
      var layer = app.map.selection.select.getLayer(event.selected[0]).get('id')
      if (event.selected.length > 0) {
        app.map.layer[layer].selectAction(event.selected[0]);
      }
    });
  }
};

app.map.interaction = {
  selectNone: new ol.interaction.Select({
    layers: []
  })
}

function newInteractionForLayer(layer) {
  return new ol.interaction.Select({
    layers: [
      layer
    ],
    style: app.map.styles.transparent
  })
}

barrierHoverSelectAction = function(feat) {
  if (feat) {
    // prevent user clicks on barrier from triggering focus area selection
    app.map.selection.select.setActive(false);
    var pixel = map.getPixelFromCoordinate(feat.getGeometry().getCoordinates());
    app.map.barrierInfo.tooltip('hide')
            .css({
              left: pixel[0] + 'px',
              top: (pixel[1]-15) + 'px'
            })
            .attr('data-original-title', feat.get('site_name') + " (" + feat.get('stream_name') +")")
            .tooltip('show');
  } else {
    // re-enable focus-area selection (if on step 1)
    if ($('#step1').is(":visible")) {
      app.map.selection.select.setActive(true);
    }
    app.map.barrierInfo.tooltip('hide');
  }
};

barrierClickSelectAction = function(feat) {
  // prevent hover from unselecting the clicked barrier
  app.map.barrierHoverInteraction.setActive(false);
  app.map.barrierHoverInteraction.getFeatures().clear();
  // We're using map clicks to watch for unselect
  app.map.selection.select.setActive(false);
  app.map.barrierSelected = true;
  app.map.barrierInfo.tooltip('hide');

  app.map.getView().setCenter(feat.getGeometry().getCoordinates());
  app.map.selectedBarrier = feat.getProperties();
  feat.setId(feat.get('pad_id'));
  app.initProjectSpecificBarrier();

};

app.map.barrierClearSelectAction = function() {
  app.map.barrierInfo.tooltip('hide');
  // if click selection exists
  if (app.map.barrierSelected) {
    //clear it out
    app.map.barrierClickInteraction.getFeatures().clear();
    app.map.barrierHoverInteraction.getFeatures().clear();
    app.map.barrierSelected = false;

    // re-enable hover
    app.map.barrierHoverInteraction.setActive(true);
    // app.map.barrierClickInteraction.setActive(true);
    setTimeout(function() {
      // double-check that new click didn't just select a new point
      if (!app.map.barrierSelected) {
        // re-enable focus-area selection (if on step 1)
        if ($('#step1').is(":visible")) {
          app.map.selection.select.setActive(true);
        }
      }
    }, 500);
  }
}

function barrierLayerLoad() {
  app.map.barrierHoverInteraction = new ol.interaction.Select({
    condition: ol.events.condition.pointerMove,
    layers: [
      app.viewModel.scenarios.scenarioFormModel.updatedFilterResultsLayer,
      app.map.layer.barriers.layer
    ],
    style: app.map.styles.PointSelected
  });

  app.map.barrierClickInteraction = new ol.interaction.Select({
    layers: [
      app.viewModel.scenarios.scenarioFormModel.updatedFilterResultsLayer
    ],
    style: app.map.styles.PointSelected
  });

  app.map.barrierSelected = false;

  $('#map').prepend('<div id="barrier-info"></div>');
  app.map.barrierInfo = $('#barrier-info');
  app.map.barrierInfo.tooltip({
    animation: false,
    trigger: 'manual'
  });

  app.map.addInteraction(app.map.barrierHoverInteraction);
  app.map.addInteraction(app.map.barrierClickInteraction);
  app.map.barrierClickInteraction.on('select', function(event) {
    barrierClickSelectAction(event.selected[0]);
  });
  app.map.barrierHoverInteraction.on('select', function(event) {
    barrierHoverSelectAction(event.selected[0]);
  });
  app.map.on('click', function(event) {
    event.preventDefault();
    event.stopPropagation();
    app.map.barrierClearSelectAction();
  });
  $('#project-barrier-modal').on('hidden.bs.modal', app.map.barrierClearSelectAction);
}
