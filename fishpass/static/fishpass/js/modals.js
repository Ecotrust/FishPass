$('#create-new-project-form').on('click', '#createProjectSubmit' , function(e) {
    e.preventDefault();
    var name = $('#id_name').val();
    if ($.trim(name) === "") {
        $('#invalid-name-message').show();
        return false;
    }
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
            app.panel.form.init(result['project_uid']);
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

$('.view-project-link').on('click', function(e) {
  app.loadingAnimation.show();
});

$('.edit-form-link').on('click', function(e) {
    e.preventDefault();
    var uid = this.getAttribute('uid');
    app.panel.form.init(uid);
    $("#launch-modal").modal('hide');
});

$('.init-delete').on('click', function(e) {
  // Reset all button statuses
  $('.confirm-delete').addClass('d-none');
  $('.init-delete').removeClass('d-none');
  dataId = this.getAttribute('data-id');
  confirmButton = $('#confirm-delete-' + dataId)
  $(this).addClass('d-none');
  confirmButton.removeClass('d-none');
});

$('.confirm-delete').on('click', function(e) {
  dataId = this.getAttribute('data-id');
  $(this).addClass('d-none');
  $('#delete-status-' + dataId).removeClass('d-none');
  $.ajax({
      url: `/scenarios/delete_design/${dataId}/`,
      type: 'POST',
      data: {
          uid: dataId
      },
      success: function(response, status) {
          $("#row-" + dataId).remove();
      },
      error: function(response, status) {
          alert(`failed to delete: %o`, response);
          $('#delete-status-' + dataId).addClass('d-none');
          $('#delete-'+dataId).removeClass('d-none');
      }
  });
});
