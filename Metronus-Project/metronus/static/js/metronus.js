const error_div_class = "form-group required company_class form-class has-feedback has-error";
const error_input_icon = "form-control col-md-6 glyphicon glyphicon-remove";
const ok_div_class = "form-group required company_class form-class has-feedback has-success";
const ok_input_icon = "form-control col-md-6 glyphicon glyphicon-ok";

$(function() {
  new WOW().init();

  var prod = window.location.hostname.indexOf("metronus.es") !== -1;

  function custom_reload() {
    var cur_href = window.location.href;
    if(cur_href.endsWith("#")) {
      window.location.href = cur_href.substring(0, cur_href.length - 1);
    } else {
      window.location.href = cur_href;
    }
  }

  $("#flag_es").click(function() {
    if(prod) Cookies.set('lang', 'es-es', {domain: '.metronus.es'});
    else Cookies.set('lang', 'es-es');
    custom_reload();
  });

  $("#flag_en").click(function() {
    if(prod) Cookies.set('lang', 'en-us', {domain: '.metronus.es'});
    else Cookies.set('lang', 'en-us');
    custom_reload();
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

  //search event
  $('#searcher').on('keyup',$.debounce(250, false, function() {
    var modelo=$('#searcher_model').val();
    search_list(modelo);
  }));
  //search event
  $('#search_button').on('click',function() {
    var modelo=$('#searcher_model').val();
    search_list(modelo);
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
  var indicator = $(field).next("i");
  var data = { };

  // If the field is incorrect by Bootstrap Validator or is empty, it is just incorrect
  if(field.val() == "" || indicator.hasClass('glyphicon-remove')){
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

    // If everything is OK, hide all help-block.with-errors
    div.find(".help-block.with-errors").each(function(){
      $(this).hide();
    });
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
//Hace una busqueda al modelo(project,department,etc.) con el valor del buscador
function search_list(modelo){
  //get value
  var buscador=document.getElementById("searcher");
  var cadena=buscador.value;
  //do search

  if(cadena == ""){
    cadena="all_true";
  }


  $.get({url:"/"+modelo+"/search/"+cadena+"/",
    success: function(data){

      $('#table_search').html($.parseHTML(data.trim()));

      simpletext = new RegExp("(" + cadena + ")","gi");

      //those with searchable class should contain only text,
      //otherwise magic will happen
      //not good magic, you know

      $('.searchable').each(function(i,el){
        var html=$(el).html();
        //highlight matches
        $(el).hide().html(html.replace(simpletext,"<strong>$1</strong>")).fadeIn();

      });
    }});
}
// Añadir el icono de info a los tooltips de información
$(function() {
  $("div.help-tooltip > p").first().prepend("<span class='glyphicon glyphicon-info-sign'></span>&nbsp;");
  $("div.help-tooltip > p").slice(1).prepend("<span class='glyphicon glyphicon-info-sign' style='visibility: hidden;'></span>&nbsp;");
});
