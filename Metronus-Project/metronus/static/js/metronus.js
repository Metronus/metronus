const error_div_class = "form-group required company_class form-class has-feedback has-error";
const error_input_icon = "form-control col-md-6 glyphicon glyphicon-remove";
const ok_div_class = "form-group required company_class form-class has-feedback has-success";
const ok_input_icon = "form-control col-md-6 glyphicon glyphicon-ok";

$(function() {
  new WOW().init();

  var prod = window.location.hostname.indexOf("metronus.es") !== -1;

  $("#flag_es").click(function() {
    if(prod) Cookies.set('lang', 'es-es', {domain: '.metronus.es'});
    else Cookies.set('lang', 'es-es');
    window.location.href = window.location.href;
  });

  $("#flag_en").click(function() {
    if(prod) Cookies.set('lang', 'en-us', {domain: '.metronus.es'});
    else Cookies.set('lang', 'en-us');
    window.location.href = window.location.href;
  });

  // Cuando el AJAX da error pero se cambia, se quita el error del ajax para limpiar
  $("input").on('input', function(){
    if($(this).parent().find(".ajax-error").is(":visible")){
      $(this).parent().find(".ajax-error").hide();
      $(this).removeClass('glyphicon-remove')
    }
  });

  //Lor numericos
  $('.precio').each(function(i) {
    $(this).val($(this).attr("value").replace(",", "."));
  });
});

function initAjax(field, field_str, url){
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
  if(field.val() == "" || field.hasClass('glyphicon-remove')){
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
  div.find("input").removeClass("glyphicon");
}

// Collapse the last collapsible if there is more than one
function autocollapse() {
  var collapse_buttons = $("a.collapse-link");
  if(collapse_buttons.length > 1) {
      collapse_buttons.last().click();
  }
}

// Añadir el icono de info a los tooltips de información
$(function() {
  $("div.help-tooltip > p").first().prepend("<span class='glyphicon glyphicon-info-sign'></span>&nbsp;");
  $("div.help-tooltip > p").slice(1).prepend("<span class='glyphicon glyphicon-info-sign' style='visibility: hidden;'></span>&nbsp;");
});
