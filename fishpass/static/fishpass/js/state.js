app.state = {
    method: 'initial',
    scenarioId: null,
    panel: {
        content: '',
        position: '',
        height: ''
    },
    instructions: '',
    focusArea: {
        method: '',
        geometry: null,
        id: null
    },
    nav: 'tall',
    step: 0,
    formModel: null,
    setMethod: function(method) {
        this.method = method;
    },
    navHeight: function(height) {
        // set state height value
        this.nav = height;

        if (height === 'short') {
            // set nav to befinning height
            app.nav.short();
        } else if (height === 'tall') {
            // set nav to use small icons and reduce height
            app.nav.short();
        }
    },
    instructions: function(instruction) {
        $('#instruction').html(instruction);
    },
    setStep: function(val) {
        // set state step value
        this.step = val;

        // update navigation based on step
        // reset, initial, ...
        if (app.nav.stepActions[val]) {
            app.nav.stepActions[val]();
        // select, filter, ...
      } else if (app.nav.stepActions[app.state.getMethod()][val]) {
            app.nav.stepActions[app.state.getMethod()][val]();
        }

        // update instructions content based on step
        // reset, initial, ...
        if (app.nav.instructions[val]) {
            app.state.instructions(app.nav.instructions[val]);
        // select, filter, ...
      } else if (app.nav.instructions[app.state.getMethod()][val]) {
            app.state.instructions(app.nav.instructions[app.state.getMethod()][val]);
        }

        //TODO: Recognize and trigger filtering/drawing steps.
    },
    setFocusArea: function(focusAreaObject) {
        this.focusArea.method = this.method;
        this.focusArea.id = focusAreaObject.id;
        this.focusArea.geometry = focusAreaObject.geojson;
    },
    showMapControls: function(show) {
        app.map.toggleMapControls(show);
    },
    getMethod: function() {
        return this.method;
    },
    panelContent: function() {
        return this.panel.content;
    },
    focusAreaState: function() {
        return this.focusArea;
    },
    getFormModel: function() {
        return this.formModel;
    },
    saveState: function() {
        return {
            method: this.method,
            focusArea: this.focusArea,
            nav: this.nav,
            step: this.step,
        }
    }
}
