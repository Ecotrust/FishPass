var app = {
    /**
    * set app state for process method
    * init a process method
    * @param {string} method value from data-attr on html element
    */
    setState: function(method) {
        app.state.setMethod(method);
        app.init[method]();
    },
    scenarioInProgress: function() {
        if (app.state.step === 0 || app.state.method === 'reset') {
            return false;
        } else if (app.state.step === 1 && app.state.method === 'filter') {
            return false;
        } else {
            return true;
        }
    },
    promptToSave: function() {
        console.log('Save before starting over?');
    },
    // Promise wrapper to load scripts
    loadScript: function loadScript(src) {
      return new Promise(function(resolve, reject) {
        var script = document.createElement('script');
        script.src = src;
        // script.onload = () => resolve(script);
        script.onload = function() {
          return resolve(script);
        };
        // script.onerror = () => reject(new Error("Script load error: " + src));
        script.onerror = function() {
          return reject(new Error("Script load error: " + src));
        };
        document.head.append(script);
      })
    },
    loadProjectBarrierForm: function() {
      $.ajax( {
          url: 'fishpass/project_barrier_form/' + app.panel.form.project_id + '/' + app.map.selectedBarrier.pad_id + '/',
          method: 'GET',
          success: function(result) {
            $('#project-barrier-form-wrap').empty();
            title_html = app.map.selectedBarrier.site_name + " (" + app.map.selectedBarrier.stream_name +
            ') - <a href="' + page_context.BIOS_LINK +
            app.map.selectedBarrier.pad_id + '" target="_blank">View in BIOS</a>';
            $('#project-barrier-modal').find('.modal-title').html(title_html);
            $('#project-barrier-form-wrap').html(result);
            $('#project-barrier-form').children('.form-error').hide();
            $('#project-barrier-form-submit').on('click', app.saveProjectBarrierForm);
            $('#project-barrier-form-reset').on('click', app.resetProjectBarrierForm);
            $('#project-barrier-modal').modal('show');
          },
          error: function(result) {
            $('#project-barrier-form').children('.form-error').html(result.responseText);
            $('#project-barrier-form').children('.form-error').show();
          }
      });
    },
    resetProjectBarrierForm: function() {
      $.ajax( {
          url: 'fishpass/project_barrier_form_reset/' + app.panel.form.project_id + '/' + app.map.selectedBarrier.pad_id + '/',
          method: 'GET',
          success: function(result) {
            app.viewModel.scenarios.scenarioFormModel.updatedFilterResultsLayer.getSource().getFeatureById(app.map.selectedBarrier.pad_id).set('user_override', false);
            $('#project-barrier-form-wrap').empty();
            $('#project-barrier-form-wrap').html(result);
            $('#project-barrier-form').children('.form-error').hide();
            $('#project-barrier-form-submit').on('click', app.saveProjectBarrierForm);
            $('#project-barrier-form-reset').on('click', app.resetProjectBarrierForm);
          },
          error: function(result) {
            $('#project-barrier-form').children('.form-error').html(result.responseText);
            $('#project-barrier-form').children('.form-error').show();
          }
      });
    },
    saveProjectBarrierForm: function() {
      $form = $('#project-barrier-form');
      $.ajax( {
        url: 'fishpass/project_barrier_form/' + app.panel.form.project_id + '/' + app.map.selectedBarrier.pad_id + '/',
        data: $form.serialize(),
        type: 'POST',
        success: function(result) {
          app.viewModel.scenarios.scenarioFormModel.updatedFilterResultsLayer.getSource().getFeatureById(app.map.selectedBarrier.pad_id).set('user_override', true);
          if (result.success) {
            $('#project-barrier-modal').modal('hide');
          } else if(result.form) {
            $('#project-barrier-form').html(result.form);
          } else {
            $('#project-barrier-form').children('.form-error').html('Error ' + result.status + ": " + result.message);
            $('#project-barrier-form').children('.form-error').show();
          }
        },
        error: function(result) {
          $('#project-barrier-form').children('.form-error').html(result.responseText);
          $('#project-barrier-form').children('.form-error').show();
        }
      })
    },
    loadProjectBarrierStatusForm: function() {
      $.ajax( {
          url: 'fishpass/project_barrier_status_form/' + app.panel.form.project_id + '/',
          method: 'GET',
          success: function(result) {
            $('#project-barrier-status-form-wrap').empty();
            $('#project-barrier-status-form-wrap').html(result);
            $('#project-barrier-status-form').children('.form-error').hide();
            $('#project-barrier-status-form-submit').on('click', app.saveProjectBarrierStatusForm);
            $('#project-barrier-status-form-reset').on('click', app.resetProjectBarrierStatusForm);
            $('#project-barrier-status-modal').modal('show');
          },
          error: function(result) {
            $('#project-barrier-status-form').children('.form-error').html(result.responseText);
            $('#project-barrier-status-form').children('.form-error').show();
          }
      });
    },
    resetProjectBarrierStatusForm: function() {
      $.ajax( {
          url: 'fishpass/project_barrier_status_form_reset/' + app.panel.form.project_id + '/',
          method: 'GET',
          success: function(result) {
            $('#project-barrier-status-form-wrap').empty();
            $('#project-barrier-status-form-wrap').html(result);
            $('#project-barrier-status-form').children('.form-error').hide();
            $('#project-barrier-status-form-submit').on('click', app.saveProjectBarrierStatusForm);
            $('#project-barrier-status-form-reset').on('click', app.resetProjectBarrierStatusForm);
          },
          error: function(result) {
            $('#project-barrier-status-form').children('.form-error').html(result.responseText);
            $('#project-barrier-status-form').children('.form-error').show();
          }
      });
    },
    saveProjectBarrierStatusForm: function() {
      $form = $('#project-barrier-status-form');
      $.ajax( {
        url: 'fishpass/project_barrier_status_form/' + app.panel.form.project_id + '/',
        data: $form.serialize(),
        type: 'POST',
        success: function(result) {
          if (result.success) {
            $('#project-barrier-status-modal').modal('hide');
          } else {
            $('#project-barrier-status-form').children('.form-error').html('Error ' + result.status + ": " + result.message);
            $('#project-barrier-status-form').children('.form-error').show();
          }
        },
        error: function(result) {
          $('#project-barrier-status-form').children('.form-error').html(result.responseText);
          $('#project-barrier-status-form').children('.form-error').show();
        }
      })
    },
    loadProjectBarrierTypeForm: function() {
      $.ajax( {
          url: 'fishpass/project_barrier_type_form/' + app.panel.form.project_id + '/',
          method: 'GET',
          success: function(result) {
            $('#project-barrier-type-form-wrap').empty();
            $('#project-barrier-type-form-wrap').html(result);
            $('#project-barrier-type-form').children('.form-error').hide();
            $('#project-barrier-type-form-submit').on('click', app.saveProjectBarrierTypeForm);
            $('#project-barrier-type-form-reset').on('click', app.resetProjectBarrierTypeForm);
            $('#project-barrier-type-modal').modal('show');
          },
          error: function(result) {
            $('#project-barrier-type-form').children('.form-error').html(result.responseText);
            $('#project-barrier-type-form').children('.form-error').show();
          }
      });
    },
    resetProjectBarrierTypeForm: function() {
      $.ajax( {
          url: 'fishpass/project_barrier_type_form_reset/' + app.panel.form.project_id + '/',
          method: 'GET',
          success: function(result) {
            $('#project-barrier-type-form-wrap').empty();
            $('#project-barrier-type-form-wrap').html(result);
            $('#project-barrier-type-form').children('.form-error').hide();
            $('#project-barrier-type-form-submit').on('click', app.saveProjectBarrierTypeForm);
            $('#project-barrier-type-form-reset').on('click', app.resetProjectBarrierTypeForm);
          },
          error: function(result) {
            $('#project-barrier-type-form').children('.form-error').html(result.responseText);
            $('#project-barrier-type-form').children('.form-error').show();
          }
      });
    },
    saveProjectBarrierTypeForm: function() {
      $form = $('#project-barrier-type-form');
      $.ajax( {
        url: 'fishpass/project_barrier_type_form/' + app.panel.form.project_id + '/',
        data: $form.serialize(),
        type: 'POST',
        success: function(result) {
          if (result.success) {
            $('#project-barrier-type-modal').modal('hide');
          } else {
            $('#project-barrier-type-form').children('.form-error').html('Error ' + result.status + ": " + result.message);
            $('#project-barrier-type-form').children('.form-error').show();
          }
        },
        error: function(result) {
          $('#project-barrier-type-form').children('.form-error').html(result.responseText);
          $('#project-barrier-type-form').children('.form-error').show();
        }
      })
    },
    getBarrierTests: function() {
      $.ajax( {
          url: 'fishpass/get_scenario_barrier_status/' + app.panel.form.project_id + '/',
          // data: {
          //   project_id: app.panel.form.project_id
          // },
          success: function(result) {
            console.log(result);
          }
      });
      $.ajax( {
          url: 'fishpass/get_scenario_barrier_type/' + app.panel.form.project_id + '/',
          // data: {
          //   project_id: app.panel.form.project_id
          // },
          success: function(result) {
            console.log(result);
          }
      });
    }
}

focusAreaHoverAction = function(feat, layer) {
  if (feat && $('#step1').is(":visible")) {
    app.map.focusAreaInfo.tooltip('hide')
            .css({
              left: app.map.cursorCoords[0] + 'px',
              top: (app.map.cursorCoords[1]-15) + 'px'
            })
            .attr('data-original-title', feat.get(layer.hoverField))
            .tooltip('show');
    app.map.showFocusAreaInfo = true;
  } else {
    app.map.focusAreaInfo.tooltip('hide');
    app.map.showFocusAreaInfo = false;
  }
}

$('#map').mousemove(function(event) {
  app.map.cursorCoords = [event.pageX, event.pageY];
  if (app.map.hasOwnProperty('showFocusAreaInfo') && app.map.showFocusAreaInfo) {
    app.map.focusAreaInfo.tooltip('hide')
    .css({
      left: app.map.cursorCoords[0] + 'px',
      top: (app.map.cursorCoords[1]-15) + 'px'
    })
    .tooltip('show');
  }
})

function selectSpatialOrganization(event) {
  var unitType = event.target.value.toLowerCase();
  if (app.map.layer.hasOwnProperty(unitType)) {
    // Clear all features from selection layer
    layernames = Object.keys(app.mapbox.layers);
    for (var i = 0; i < layernames.length; i++) {
      app.map.disableLayer(layernames[i]);
    }
    // Clear "Target Area" field and re-trigger filtering.
    app.clearTargetAreaInput();
    app.map.enableLayer(unitType);
    app.map.selection.spatialOrganizationSelection = newInteractionForLayer(app.map.layer[unitType].layer);
    app.map.selection.setSelect(app.map.selection.spatialOrganizationSelection);

  }
};

function spatialOrgLoad() {

  $('#map').prepend('<div id="focus-area-info"></div>');
  app.map.focusAreaInfo = $('#focus-area-info');
  app.map.focusAreaInfo.tooltip({
    animation: false,
    trigger: 'manual'
  });

  var selection_layers = [
    'huc02',
    'huc04',
    'huc06',
    'huc08',
    'huc10',
    'huc12',
    'county',
    'boundary',
    'region',
    'coho',
    'chinook',
    'chinook_spring',
    'chinook_fall',
    'steelhead'
  ];
  app.map.focusAreaHoverInteractions = {}
  for (var i = 0; i < selection_layers.length; i++) {
    layer = selection_layers[i];
    app.map.focusAreaHoverInteractions[layer] = new ol.interaction.Select({
      condition: ol.events.condition.pointerMove,
      layers: [
        app.map.layer[layer].layer
      ],
      style: app.map.styles.FocusAreaHover
    });
    app.map.addInteraction(app.map.focusAreaHoverInteractions[layer]);
  }

  // RDH: I couldn't get the scoping right to make this work in the previous loop.
  app.map.focusAreaHoverInteractions.huc02.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.huc02);
  });
  app.map.focusAreaHoverInteractions.huc04.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.huc04);
  });
  app.map.focusAreaHoverInteractions.huc06.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.huc06);
  });
  app.map.focusAreaHoverInteractions.huc08.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.huc08);
  });
  app.map.focusAreaHoverInteractions.huc10.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.huc10);
  });
  app.map.focusAreaHoverInteractions.huc12.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.huc12);
  });
  app.map.focusAreaHoverInteractions.county.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.county);
  });
  app.map.focusAreaHoverInteractions.boundary.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.boundary);
  });
  app.map.focusAreaHoverInteractions.region.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.region);
  });
  app.map.focusAreaHoverInteractions.coho.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.coho);
  });
  app.map.focusAreaHoverInteractions.chinook.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.chinook);
  });
  app.map.focusAreaHoverInteractions.chinook_spring.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.chinook_spring);
  });
  app.map.focusAreaHoverInteractions.chinook_fall.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.chinook_fall);
  });
  app.map.focusAreaHoverInteractions.steelhead.on('select', function(event) {
    focusAreaHoverAction(event.selected[0], app.map.layer.steelhead);
  });

  document.getElementById('id_spatial_organization').onchange = selectSpatialOrganization;

  app.clearTargetAreaInput = function() {
    document.getElementById('id_target_area').value = '';
    app.viewModel.scenarios.scenarioFormModel.filters.target_area_input = null;
    app.map.selection.focusArea = [];
    app.map.layer.focusArea.clearFeatures();
    if (app.map.selection.hasOwnProperty('spatialOrganizationSelection')) {
      app.map.selection.spatialOrganizationSelection.getFeatures().clear();
      app.map.removeInteraction(app.map.selection.spatialOrganizationSelection);
    }
    app.viewModel.scenarios.scenarioFormModel.updateFilterResults();
  }

  app.updateAllFilters = function() {
    app.viewModel.scenarios.scenarioFormModel.updateFilters('target_area');
    app.viewModel.scenarios.scenarioFormModel.updateFilters('treat_downstream');
    if ($("#id_ownership_input")[0].checked) {
      app.viewModel.scenarios.scenarioFormModel.updateFilters('ownership_input');
    }
  }

  app.initSpatialOrg = function() {
    var focus_area_input = document.getElementById('id_target_area').value;
    var focus_area_string_list = focus_area_input.split(',');
    app.viewModel.scenarios.scenarioFormModel.filters.target_area_input = focus_area_input;
    app.map.selection.focusArea = [];
    for (var i = 0; i < focus_area_string_list.length; i++) {
      app.map.selection.focusArea.push(parseInt(focus_area_string_list[i]));
    }
    if (app.map.selection.focusArea.length > 0 && !isNaN(app.map.selection.focusArea[0])) {
      app.request.get_focus_area_geojson_by_ids(app.map.selection.focusArea, function(result){
        // response contains GeoJSON object
        app.map.layer.focusArea.addFeatures(result);
      });
    } else {
      app.map.selection.focusArea = [];
    }
    unitType = document.getElementById('id_spatial_organization').value.toLowerCase();
    app.map.enableLayer(unitType);
    app.map.selection.spatialOrganizationSelection = newInteractionForLayer(app.map.layer[unitType].layer);
    app.map.selection.setSelect(app.map.selection.spatialOrganizationSelection);
    app.updateAllFilters();
    app.viewModel.scenarios.scenarioFormModel.updateFilterResults();
  }

  app.addIdToTargetAreaInput = function() {
    document.getElementById('id_target_area').value = app.map.interaction.focusAreaSelection;
  }
};

//
//
// scenario_type_selection_made = function(selectionType) {
//     var animateObj = {
//         zoom: 8,
//         center: [-13363592.377434019, 6154762.569701998],
//         duration: 800
//     }
//     // var extent = new ol.extent.boundingExtent([[-121.1, 47], [-119, 49]]);
//     // extent = ol.proj.transformExtent(extent, ol.proj.get('EPSG:4326'), ol.proj.get('EPSG:3857'));
//     if (selectionType === 'draw') {
//         app.map.layer.draw.layer.setVisible(true);
//         // app.map.removeInteraction(app.map.Pointer);
//         // app.map.getView().animate(animateObj);
//     } else {
//         app.map.removeInteraction(app.map.draw.draw);
//         app.map.layer.draw.layer.setVisible(false);
//         // app.map.addInteraction(app.map.Pointer);
//         // app.map.getView().animate(animateObj);
//     }
// }


baseInit = function() {
    app.map.selection.setSelect(app.map.selection.selectNoneSingleClick);
    app.map.closePopup();
    app.map.draw.disable();
    app.map.popupLock = false;
    app.map.setBoundaryLayer(app.map.layer.boundary.layer);
}

setInit = function() {
    baseInit();
    if (app.map.hasOwnProperty('mask')) {
        app.map.mask.set('active', false);
    }
    app.map.clearLayers();
    app.map.enableLayer('boundary');

    app.state.setStep(0);
    app.map.layer.draw.layer.getSource().clear();
};

initBudgetToggle = function() {
  if ($('#id_budget_type').val() == 'budget') {
    $('.ranged-budget-form').hide();
    $('.fixed-budget-form').show();
  } else {
    $('.fixed-budget-form').hide();
    $('.ranged-budget-form').show();
  }
}

formSetup = function() {

  $('#id_budget').parent().parent().addClass('fixed-budget-form');
  $('#id_budget_min').parent().parent().addClass('ranged-budget-form');
  $('#id_budget_max').parent().parent().addClass('ranged-budget-form');
  $('#id_batch_increment').parent().parent().addClass('ranged-budget-form');

  if (!app.viewModel.scenarios.scenarioFormModel.filters.hasOwnProperty('assign_cost')) {
    app.viewModel.scenarios.scenarioFormModel.filters['assign_cost'] = $('#id_assign_cost')[0].checked;
  }

  $('#id_budget_type').on('change', initBudgetToggle);
  initBudgetToggle();
}

reportInit = function() {

}

app.init = {
    'select': function() {
        setInit();
        app.map.selection.setSelect(app.map.selection.selectSelectSingleClick);
        app.map.enableLayer('streams');
        scenario_type_selection_made('select');
    },
    'filter': function() {
        setInit();
        app.map.selection.setSelect(app.map.selection.selectFilterSingleClick);
        // app.map.enableLayer('huc12');
        scenario_type_selection_made('filter');
    },
    'draw': function() {
        setInit();
        // app.map.enableLayer('huc10');
        app.map.selection.setSelect(app.map.selection.selectNoneSingleClick);
        scenario_type_selection_made('draw');
    },
    'hydro': function() {
        reportInit();
        app.state.setStep('hydro');
        app.panel.results.showHydro();
    },
    'aggregate': function() {
        reportInit();
        app.state.setStep('aggregate');
        app.panel.results.showAggregate();
    }
}

app.resultsInit = function(id) {
    app.map.geoSearch.closeSearchBox();
    app.panel.results.init();
    if (!id) {
        id = app.viewModel.scenarios.scenarioList()[0].uid;
    } else if (!id.includes('ucsrb')) {
        id = 'fishpass_project_' + id;
        app.viewModel.scenarios.addScenarioToMap(null, {
            uid: id
        });
    }
    app.loadingAnimation.panel.show();
    app.request.get_results(id,false)
        .done(function(response) {
            app.panel.results.responseResultById(response);
            app.map.layer.resultPoints.layer.getSource().clear();
            var layerAdded = false;
            app.map.getLayers().forEach(function(i) {
                if (i.get('id') === 'resultPoints') {
                    layerAdded = true;
                }
            });
            if (!layerAdded) {
                app.map.addLayer(app.map.layer.resultPoints.layer);
            }
            // run this after function is called for performance
            window.setTimeout(function() {
              app.map.setBoundaryLayer(app.map.layer.boundary.layer);
              app.map.layer.boundary.layer.setVisible(true);
              app.map.addFocusAreaToMap(response.focus_area);
              app.map.addDownstreamPptsToMap(response.pourpoints);
            }, 500);
        })
        .catch(function(response) {
            console.log('%c failed to get results: %o', 'color: salmon;', response);
        });
    app.nav.hideSave();
    app.nav.showResultsNav();
    $('#subnav-sign-in-modal').addClass('d-none');
}

initFiltering = function() {
    setTimeout(function() {
        if ($('#step1').length > 0) {
            $('#button_next').on('click', app.panel.stepControl);
            $('#button_prev').on('click', app.panel.stepControl);
            app.initSpatialOrg();
        } else {
            initFiltering();
        }
    }, 300);
};

drawingIsSmallEnough = function(areaInMeters) {
    maxAcres = app.map.draw.maxAcres;
    metersPerAcre = 4046.86;
    return maxAcres*metersPerAcre > areaInMeters;
}

app.panel = {
    hide: function() {
        app.panel.element.hidden = true;
        app.nav.hideSave();
    },
    show: function() {
        app.panel.element.hidden = false;
    },
    loading: {
        show: function() {
            $('.panel .loading-animation').removeClass('hide');
            $('.panel .loading-animation').addClass('show');
        },
        hide: function() {
            $('.panel .loading-animation').removeClass('show');
            $('.panel .loading-animation').addClass('hide');
        }
    },
    moveLeft: function() {
        app.panel.show();
        app.panel.getElement.classList.add('left');
        app.panel.getElement.classList.remove('right');
        app.state.panel.position = 'left'; // set state
    },
    moveRight: function() {
        app.panel.show();
        app.panel.getElement.classList.add('right');
        app.panel.getElement.classList.remove('left');
        app.state.panel.position = 'right'; // set state
    },
    setContent: function(content) {
        app.panel.show();
        app.state.panel.content = content;
        app.panel.getPanelContentElement.innerHTML = content;
    },
    toggleSize: function() {
        var appPanel = app.panel.getElement;
        if (appPanel.classList.contains('expanded')) {
            appPanel.classList.remove('expanded');
        } else {
            appPanel.classList.add('expanded');
        }
        if (app.panel.results.chart.obj) {
            app.panel.results.chart.resize();
        }
    },
    form: {
        init: function(project_id) {
            app.panel.moveLeft();
            app.panel.form.scenario = app.viewModel.scenarios.createNewScenario('/features/project/'+ project_id + "/form/");
            app.panel.form.project_id= project_id;
            // app.nav.showSave();
            initFiltering();
        },
    },
    summary: {
        init: function() {
            document.getElementById('chartResult').innerHTML = app.panel.results.styleSummaryResultsAsRows(app.panel.results.summary);
        }
    },
    results: {
        init: function() {
            app.panel.getPanelContentElement.innerHTML = app.nav.stepActions.initial;
            app.panel.moveLeft();
            if (app.state.nav === 'tall') {
                app.state.navHeight('short');
            }
        },
        name: ''
    },
    stepControl: function() {
      selectFocusAreaStepId = 'step1';
      setTimeout(function(){
        if ($('#' + selectFocusAreaStepId).is(":visible")) {
          app.map.selection.select.setActive(true);
          app.viewModel.scenarios.scenarioFormModel.stopShowingFilteringResults();
          $('.ol-geo-search').hide();
        } else {
          app.map.selection.select.setActive(false);
          if (!app.viewModel.scenarios.scenarioFormModel.showingFilteringResults()) {
            app.viewModel.scenarios.scenarioFormModel.showFilteringResults();
            app.viewModel.scenarios.scenarioFormModel.updatedFilterResultsLayer.setVisibility(true);
          }
          $('.ol-geo-search').show();
        }
      }, 300);
    },
    element: function() { // returns a function. to edit dom element don't forget to invoke: element()
      return this.getElement;
    },

    panelContentElement: function() { // returns a function. to edit dom element don't forget to invoke: panelContentElement()
      return this.getPanelContentElement;
    },
    get getElement() {
        return document.getElementById('panel');
    },
    get getPanelContentElement() {
        return document.getElementById('panel-content');
    }
}

enableDrawing = function() {
    app.map.draw.enable();
    app.map.geoSearch.openSearchBox();
}

app.filterDropdownContent = '<div class="dropdown">\n' +
'        <button class="btn btn-sm ml-2 btn-outline-light dropdown-toggle" type="button" id="forestUnit" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Select unit</button>\n' +
'        <div class="dropdown-menu forest-unit-dropdown" aria-labelledby="forestUnit">\n' +
'            <div id="forest-listener">\n' +
'                <button class="dropdown-item" type="button" data-layer="huc10">HUC 10</button>\n' +
'                <button class="dropdown-item" type="button" data-layer="huc12">HUC 12</button>\n' +
'                <button class="dropdown-item" type="button" data-layer="RMU">Forest Plan Mgmt Alloc</button>\n' +
'            </div>\n' +
'        </div>\n' +
'    </div>\n' +
'    <script>\n' +
'        (function() {\n' +
'            $("#forest-listener button").on("click", function(event) {\n' +
'                event.preventDefault();\n' +
'                $("#forest-listener").children().each(function(i) {\n' +
'                    if ($(this)[0].dataset.layer !== event.target.dataset.layer) {\n' +
'                        app.map.disableLayer($(this)[0].dataset.layer);\n' +
'                    }\n' +
'                });\n' +
'                var eventLayer = event.target.dataset.layer;\n' +
'                app.map.toggleLayer(eventLayer);\n' +
'                app.state.setStep(1);\n' +
'            });\n' +
'        })();\n' +
'    </script>';

app.nav = {
    setState: function(height) {
        app.state.navHeight(height);
    },
    showResultsNav: function() {
        document.getElementById('results-nav').classList.remove('d-none');
        document.getElementById('process-nav').classList.add('d-none');
        document.querySelectorAll('#file-nav .results-nav-item').forEach(function(i, arr) {
            i.classList.remove('d-none')
        });
    },
    hideResultsNav: function() {
        document.getElementById('results-nav').classList.add('d-none');
        document.getElementById('process-nav').classList.remove('d-none');
        document.querySelectorAll('#file-nav .results-nav-item').forEach(function(i, arr) {
            i.classList.add('d-none')
        });
    },
    showStartOver: function() {
        document.getElementById('nav-start-over').classList.remove('d-none');
    },
    showSave: function() {
        document.getElementById('nav-anon-save').classList.remove('d-none');
    },
    saveElement: function() {
        return document.getElementById('nav-anon-save');
    },
    showAnonSave: function() {
        document.getElementById('subnav-sign-in-modal').classList.remove('d-none');
    },
    hideSave: function() {
        document.getElementById('nav-anon-save').classList.add('d-none');
    },
    short: function() {
        // style nav
        $('.nav-wrap').addClass('icons-only');
        $('.map-wrap').addClass('short-nav');
        $('.overlay').addClass('fade-out short-overlay');
        setTimeout(function() {
            $('#process-nav').addClass('justify-content-start');
            $('#process-nav').removeClass('justify-content-center');
            $('.overlay').removeClass('fade-out');
        }, 1000);
    },
    tall: function() {
        $('.nav-wrap').removeClass('icons-only');
        $('.nav-wrap').removeClass('short-nav');
        setTimeout(function() {
            $('#process-nav').removeClass('justify-content-start');
            $('#process-nav').addClass('justify-content-center');
        }, 1000);
    },
    instructions: {
        initial: '<h2 class="mx-auto w-50 text-center">Start by deciding how you want <br/>to interact with the map</h2>',
        reset: 'Decide how you want to interact with the map',
        select: [
            'Zoom in and select a stream segment to evaluate changes in flow',
            'select one of the highlighted pour points to evaluate changes in flow associated with management activity upstream',
            'Select filters to narrow your treatment region',
        ],
        filter: [
            'Select area to manage based on: ' + app.filterDropdownContent,
            'Select forest unit to filter or change selection: ' + app.filterDropdownContent,
            'Select filters to narrow your treatment area',
        ],
        draw: [
            'Zoom in to area of interest or use the geocoder to search for places by name.<br />Click on the map to start drawing the boundary of your management area.',
            'Add additional points then double-click to finish; Re-select point to edit',
        ],
        result: 'Explore evaluation results',
        aggregate: 'Select virtual gauging station ( <span style="height: 20px; background: #fff; border: 2px solid #67b8c6; border-radius: 50%; box-shadow: 0 0 4px #333, 0 0 4px #999; width: 20px; margin: 4px 10px; display: inline-block;"></span> ) to view predicted changes in flow.',
        hydro: 'Your hydrologic results',
    },
    stepActions: {
        initial: '<div id="scenarios"></div><div id="scenario_form"></div><div id="draw_form"></div><div id="results"></div>',
        reset: function() {
            app.panel.getPanelContentElement.innerHTML = app.nav.stepActions.initial;
            app.panel.moveRight();
            app.nav.hideSave();
            app.map.removeLayer(app.map.layer.selectedFeature.layer);
            app.map.removeLayer(app.map.layer.resultPoints.layer);
            app.map.geoSearch.closeSearchBox();
            if (app.map.mask) {
                app.map.mask.set('active', false);
            }
            closeConfirmSelection(true,true);
        },
        select: [
            false,
            false,
            app.panel.form.init
        ],
        filter: [
            false,
            false,
            app.panel.form.init
        ],
        draw: [
            enableDrawing,
            false     //TODO: ??? enable editing?
        ],
        results: function() {
            app.nav.hideSave();
            if (app.state.nav !== 'short') {
                app.state.navHeight('short');
            }
        },
        aggregate: function() {
            // Trigger a click on navigation so arrow appears
            $('button[data-method=aggregate]').click()

        },
        hydro: function() {
            $('button[data-method=hydro]').click()
        }
    }
}

app.loadingAnimation = {
    show: function() {
        $('#loading-modal').modal('show');
    },
    hide: function() {
        $('#loading-modal').modal('hide');
    },
    panel: {
        show: function() {

        },
        hide: function() {

        }
    }
}
// using jQuery to get CSRF Token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/**
* Application AJAX requests object and methods
* {get_results} results for treatment scenario
* {get_segment_by_bbox} segment by bounding box
* {get_segment_by_id} segment by id
* {get_pourpoint_by_id} pourpoint by id
* {filter_results} filter results
*
*/
app.request = {
    /**
     * [Get spatial organization layer feature geojson]
     * @method
     * @param  {[type]} unitType [Focus Area Type (layer)]
     * @param  {[type]} unitId [Focus Area's Unit ID]
     * @param  {[type]} callback [Function to run on success]
     * @return {[type]}       [GeoJSON]
     */
    get_focus_area_geojson_by_type: function(unitType, unitId, callback) {
        // TODO write view to get spatial organiation layer
        return $.ajax({
            url: '/fishpass/get_focus_area_geojson_by_type',
            data: {
                unitType: unitType,
                unitId: unitId
            },
            dataType: 'json',
            success: function(response) {
                callback(response);
            },
            error: function(response) {
                console.log('%cfail @ get planning units response: %o', 'color: red', response);
            }
        })
    },
    /**
     * [Get spatial organization layer features]
     * @method
     * @param  {[type]} fa_ids [list of Focus Area IDs]
     * @param  {[type]} callback [Function to run on success
     * @return {[type]}       [GeoJSON]
     */
    get_focus_area_geojson_by_ids: function(fa_ids, callback) {
        // TODO write view to get spatial organiation layer
        return $.ajax({
            url: '/fishpass/get_focus_area_geojson_by_ids',
            data: {
                fa_ids: fa_ids
            },
            dataType: 'json',
            success: function(response) {
                callback(response);
            },
            error: function(response) {
                console.log('%cfail @ get planning units response: %o', 'color: red', response);
            }
        })
    },
    /**
    * get results for treatment scenario
    * @param  {[number]} id treatment scenario id [on scenario this is created]
    * @return {[json]} result data
    */
    get_results: function(id,exportResults) {
        if (!id) {
            id = app.map.selectedFeature.getProperties().ppt_ID;
        }
        return $.ajax({
            url: '/get_results_by_scenario_id',
            data: {
                id: id,
                // export: exportResults
            },
            dataType: 'json',
            success: function(response) {
                return response;
            },
            error: function(response) {
                console.log('%cfail @ get planning units response: %o', 'color: red', response);
            }
        })
    },
    get_barrier_layer: function() {
      return $.ajax({
          url: '/fishpass/get_barrier_layer/',
          dataType: 'json',
          success: function(response) {
              return response;
          },
          error: function(response) {
              console.log('%cfail @ get downstream pourpoints: %o', 'color: red', response);
          }
      })
    },
    get_downstream_pour_points: function(id) {
        if (!id) {
            id = app.map.selectedFeature.getProperties().ppt_ID;
        }
        return $.ajax({
            url: '/get_downstream_pour_points',
            data: {
                pourpoint_id: id
            },
            dataType: 'json',
            success: function(response) {
                return response;
            },
            error: function(response) {
                console.log('%cfail @ get downstream pourpoints: %o', 'color: red', response);
            }
        })
    },
    get_hydro_results_by_pour_point_id: function(feature, scenarioId) {
        if (feature.getProperties().ppt_ID) {
            var pp_id = feature.getProperties().ppt_ID;
        } else if (feature.getProperties().id) {
            var pp_id = feature.getProperties().id;
        } else {
            var pp_id = feature.getProperties().ppt_id
        }
        app.map.selectedPourPoint = feature;
        if (!scenarioId) {
            treatmentId = app.state.scenarioId;
        }
        return $.ajax({
            url: '/get_hydro_results_by_pour_point_id',
            data: {
                pourpoint_id: pp_id,
                treatment_id: treatmentId,
            },
            dataType: 'json',
            success: function(response) {
                return response;
            },
            error: function(response) {
                console.log('%cfail @ get hydro results for pourpoint: %o', 'color: red', response);
            }
        });
    },
    /**
    * Planning Units
    * scenario planning units to filter upon
    * @return {[json]} features list
    */
    get_planningunits: function() {
        return $.ajax('/scenario/get_planningunits')
        .done(function(response) {
            return response;
        })
        .fail(function(response) {
            console.log('%cfail @ get planning units response: %o', 'color: red', response);
        });
    },
    get_user_scenarios: function() {
        return $.ajax('/get_user_scenario_list/')
        .done(function(response) {
            return response;
        })
        .fail(function(response) {
            console.log('%cfail @ get scenarios: %o', 'color: red', response);
        });
    },
    get_scenarios: function() {
        return $.ajax('/ucsrb/get_scenarios/')
        .done(function(response) {
            return response;
        })
        .fail(function(response) {
            console.log('%cfail @ get scenarios: %o', 'color: red', response);
        });
    },
    /**
    * get stream segments by bounding box
    * @param {Array} bbox coords from map view
    */
    get_segment_by_bbox: function(bbox) {
        return $.ajax({
            url: '/get_segment_by_bbox',
            data: {
                bbox_coords: bbox
            },
            dataType: 'json'
        })
        .done(function(response) {
            return response;
        })
        .fail(function(response) {
            console.log('%cfail @ get segment by bbox: %o', 'color: red', response);
            return false;
        });
    },
    /**
    * Request stream segement by id
    * @param {number|int} id
    * @returns {Object} stream segement
    * @property segment name id geometry pourpoints[id, geometry, name]
    */
    get_segment_by_id: function(id) {
        return $.ajax('/segment/' + id)
        .done(function(response) {
            return response;
        })
        .fail(function(response) {
            console.log('%cfail @ segment by id: %o', 'color: red', response);
        });
    },
    /**
    * Request pourpoint by id
    * @param {number|int} id
    * @returns {Object} pourpoint
    * @property name id acres point_geometry area_geometry
    */
    get_pourpoint_by_id: function(id) {
        return $.ajax('pourpoint/' + id)
        .done(function(response) {
            return response;
        })
        .fail(function(response) {
            console.log('%cfail @ get pourpoint id: %o', 'color: red', response);
        });
    },
    get_focus_area: function(feature, callback) {
        app.map.selectedFeature = feature;
        var props = app.map.selectedFeature.getProperties();
        var layer = app.mapbox.layers[props.layer.split('.shp')[0]].map_layer_id;
        var idField = app.mapbox.layers[props.layer.split('.shp')[0]].id_field;
        var id = props[idField];
        return $.ajax({
            url: '/ucsrb/get_focus_area',
            data: {
                id: id,
                layer: layer,
            },
            dataType: 'json',
            success: function(response) {
                app.state.setFocusArea(response);
                callback(feature, response.geojson);
            },
            error: function(response, status) {
                console.log('%cfail @ get focus area: %o', 'color: red', response);
                callback(null, response);
                return status;
            }
        })
    },
    get_focus_area_at: function(feature, layerName, callback) {
        /**
        * This is sloppy, but I don't know how to get the geometry from a VectorTile feature.
        * @todo {Priority low} find try and set geometry from vector tile
        */
        point = feature.getFlatCoordinates();
        return $.ajax({
            url: '/ucsrb/get_focus_area_at',
            data: {
                point: point,
                layer: layerName,
            },
            dataType: 'json',
            success: function(response) {
                callback(feature, response);
            },
            error: function(response, status) {
                console.log('%cfail @ get focus area at point: %o', 'color: red', response);
                callback(null, response);
            }
        })
    },
    /**
    * get a pourpoint's basin
    * @param  {number} pp_id [id]
    * @return {[GeoJSON]} drainage basin
    */
    get_basin: function(feature, callback) {
        var pp_id = feature.getProperties().ppt_ID;
        app.map.selectedFeature = feature;
        return $.ajax({
            url: '/ucsrb/get_basin',
            data: {
                pourPoint: pp_id,
            },
            dataType: 'json',
            success: function(response) {
                app.state.setFocusArea(response);
                callback(feature, response.geojson);
                return response;
            },
            error: function(response, status) {
                console.log('%cfail @ get basin: %o', 'color: red', response);
                // we don't have the ppt basins yet, just get a HUC12 for now.
                app.request.get_focus_area_at(app.map.selectedFeature, 'HUC12', function(feature, hucFeat) {
                    vectors = (new ol.format.GeoJSON()).readFeatures(hucFeat.geojson, {
                        dataProjection: 'EPSG:3857',
                        featureProjection: 'EPSG:3857'
                    });
                    // set property id with hucFeat.id
                    vector = vectors[0].getGeometry();
                    vector.set('layer', 'huc12_3857');
                    vector.set('HUC_12', hucFeat.id.toString());
                    app.request.get_focus_area(vector, 'HUC12', callback);
                });
                return status;
            }
        })
    },
    saveDrawing: function(draw_name, draw_desc) {
        var drawFeatures = app.map.draw.source.getFeatures();
        var geojsonFormat = new ol.format.GeoJSON();
        var featureJson = geojsonFormat.writeFeatures(drawFeatures);

        return $.ajax({
            url: '/ucsrb/save_drawing',
            data: {
                drawing: featureJson,
                // TODO: Set name/description with form
                name: draw_name,
                description: draw_desc
            },
            dataType: 'json',
            method: 'POST',
            success: function(response) {
                app.map.draw.disable();
                app.nav.hideSave();
                if (app.state.nav !== 'short') {
                    app.state.navHeight('short');
                    app.state.setStep('results'); // go to results
                }
                var vectors = (new ol.format.GeoJSON()).readFeatures(response.geojson, {
                    dataProjection: 'EPSG:3857',
                    featureProjection: 'EPSG:3857'
                });
                // Remove drawing from layer
                var draw_source = app.map.layer.draw.layer.getSource();
                draw_source.removeFeature(draw_source.getFeatures()[0]);
                app.map.addScenario(vectors);
                app.panel.results.init('fishpass_project_' + response.id);
                app.resultsInit('fishpass_project_' + response.id);
                app.state.scenarioId = response.id;
                app.state.setStep('results');
            },
            error: function(response, status) {
                console.log('%cfail @ save drawing: %o', 'color: red', response);
                alert(response.responseJSON.error_msg);
                app.panel.draw.finishDrawing();
            }
        })
    },
    filter_results: function(pourpoint) {
        $.ajax({
            url: "/api/filter_results",
            data: {
                ppid: pourpoint
            },
        })
    },
    saveIntermediateScenario: function(data) {
        $.ajax({
            url: '/scenario/project/save',
            type: 'POST',
            data: data,
            dataType: 'json',
            success: function(response, status) {
                return status;
            },
            error: function(response, status) {
                console.log('%cfailed save state: %o', 'color: red', response);
                return status;
            }
        })
    },
    saveState: function() {
        $.ajax({
            url: '/scenario/project/save',
            type: 'POST',
            data: app.saveState,
            dataType: 'json',
            success: function(response, status) {
                return status;
            },
            error: function(response, status) {
                console.log('%cfail @ save state: %o', 'color: red', response);
                return status;
            }
        })
    },
    deleteScenario: function(id) {
        return $.ajax({
            url: '/scenario/delete_design/fishpass_project_' + id + '/',
            type: 'POST',
            data: {
                uid: id
            },
            success: function(response, status) {
                return status;
            },
            error: function(response, status) {
                console.log('%failed to deleted: %o', 'color: red', response);
                return status;
            }
        })
    }
}
