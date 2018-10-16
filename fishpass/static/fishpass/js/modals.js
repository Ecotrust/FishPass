$('#create-new-project-form').on('click', '#createProjectSubmit' , function(e) {
    e.preventDefault();
    var name = $('#id_name').val();
    if ($.trim(name) === "") {
        $('#invalid-name-message').show();
        return false;
    }
    //submitted = true;
    submitCreateProjectForm($("#create-new-project-form"));
});

submitCreateProjectForm = function($form) {
    var url = $form.attr('action'),
        data = new FormData();

    $form.find('input,select,textarea').each( function(index, input) {
        var $input = $(input);
        data.append($input.attr('name'), $input.val());
    });
    app.viewModel.scenarios.scenarioForm(false);
    $.ajax({
        url: url,
        data: data,
        cache: false,
        contentType: false,
        processData: false,
        type: 'POST',
        traditional: true,
        dataType: 'json',
        success: function(result) {
            // app.loadingAnimation.hide();
            // Redirect window to /report/SCENARIO_ID/
            app.panel.form.init(result['project_uid']);
            // document.location.href = '/fishpass/get_report/' + result['X-Madrona-Select'] + '/';
            // window.alert('DEBUG: All Done! This would send you to `/fishpass/get_report/' + result['X-Madrona-Select'] + '/`')
            $('#launch-modal').modal('hide');
        },
        error: function(result) {
            app.viewModel.scenarios.loadingMessage(null);
            // clearInterval(barTimer);
            if (result.status === 400) {
                $('#'+app.viewModel.currentTocId()+'-scenario-form > div').append(result.responseText);
                app.viewModel.scenarios.scenarioForm(true);
            } else {
                app.viewModel.scenarios.errorMessage(result.responseText.split('\n\n')[0]);
            }
            console.log(`%c form not submitted; %o`, 'color: salmon;', result);
        }
    });
};
