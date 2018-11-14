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
  } else {
    // re-enable focus-area selection (if on step 1)
    if ($('#step1').is(":visible")) {
      app.map.selection.select.setActive(true);
    }
  }
};

barrierClickSelectAction = function(feat) {
  // prevent hover from unselecting the clicked barrier
  app.map.barrierHoverInteraction.setActive(false);
  app.map.barrierHoverInteraction.getFeatures().clear();
  // We're using map clicks to watch for unselect
  app.map.selection.select.setActive(false);
  app.map.barrierSelected = true;
};

barrierClearSelectAction = function() {
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
      app.viewModel.scenarios.scenarioFormModel.updatedFilterResultsLayer
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
    barrierClearSelectAction();
  });
}


scenario_type_selection_made = function(selectionType) {
    var animateObj = {
        zoom: 8,
        center: [-13363592.377434019, 6154762.569701998],
        duration: 800
    }
    // var extent = new ol.extent.boundingExtent([[-121.1, 47], [-119, 49]]);
    // extent = ol.proj.transformExtent(extent, ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));
    if (selectionType === 'draw') {
        app.map.layer.draw.layer.setVisible(true);
        // app.map.removeInteraction(app.map.Pointer);
        // app.map.getView().animate(animateObj);
    } else {
        app.map.removeInteraction(app.map.draw.draw);
        app.map.layer.draw.layer.setVisible(false);
        // app.map.addInteraction(app.map.Pointer);
        // app.map.getView().animate(animateObj);
    }
}
