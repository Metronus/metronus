const error_div_class = "form-group required company_class form-class has-feedback has-error";
const error_input_icon = "form-control col-md-6 glyphicon glyphicon-remove";
const ok_div_class = "form-group required company_class form-class has-feedback has-success";
const ok_input_icon = "form-control col-md-6 glyphicon glyphicon-ok";

$( document ).ready(function() {
  new WOW().init();

  $("#flag_es").click(function() {
    Cookies.set('lang', 'es-es');
    location.reload(true);
  });

  $("#flag_en").click(function() {
    Cookies.set('lang', 'en-us');
    location.reload(true);
  });
});

function initAjax(field, field_str, url){
  field.parent().find(".ajax-error").hide()
  field.change(function(){
    ajaxValidation($(this), field_str, url);
  });
}

// It sets all the necessary to perform ajax validations
function ajaxValidation(field, field_str, url){
  var div = $(field).parent().parent();
  var msg_div = $(field).parent().find(".ajax-error");
  var data = { };

  // If the field is incorrect by Bootstrap Validator or is empty, it is just incorrect
  if(field.val() == "" || field.hasClass('has-error')){
    return;
  }

  data[field_str] = field.val();

  $.ajax({
    url: url,
    data: data,
    dataType: 'json',
    success: function (data) {
      setValidationState(data.is_taken, div, msg_div);
    }
  });
}

// AUXILIAR FUNCTION TO SET VALIDATION STATE
function setValidationState(error, div, message){
  if(error){
    div.removeClass().addClass(error_div_class);
    div.find("input").removeClass().addClass(error_input_icon);
    div.find("i").removeClass("glyphicon-ok").addClass("glyphicon-remove");
    message.show();
  } else {
    div.removeClass().addClass(ok_div_class);
    div.find("input").removeClass().addClass(ok_input_icon);
    div.find("i").removeClass("glyphicon-remove").addClass("glyphicon-ok");
    message.hide();
  }
}
