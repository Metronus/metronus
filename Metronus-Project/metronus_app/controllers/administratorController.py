from django.http import HttpResponseRedirect, JsonResponse
from django.core.exceptions import PermissionDenied
from metronus_app.forms.administratorForm import AdministratorForm
from metronus_app.forms.employeePasswordForm import EmployeePasswordForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from metronus_app.common_utils import check_image, get_current_admin_or_403,is_email_unique, email_in_use_logged,validate_pass
from django.contrib.auth import update_session_auth_hash


@login_required
def edit(request):
    """
    url = administrator/edit/

    parameters/returns:
    form: formulario de edicion de datos de administrador

    template: administrator_edit.html
    """
    errors=[]
    administrator = get_current_admin_or_403(request)

    if request.method == "GET":
        # Return a form filled with the administrator's data
        form = AdministratorForm(initial={
            'first_name': administrator.user.first_name,
            'last_name': administrator.user.last_name,
            'admin_email': administrator.user.email,
            'identifier': administrator.identifier,
            'phone': administrator.phone
        })
    elif request.method == "POST":
        # Process the received form
        form = AdministratorForm(request.POST, request.FILES)
        if form.is_valid():
            if not check_image(form, 'photo'):
                errors.append('company_imageNotValid')
            if not email_in_use_logged(form.cleaned_data['admin_email'], administrator):
                errors.append('companyRegister_adminEmailNotUnique')
            if not errors:
                # Update employee data
                administrator.identifier = form.cleaned_data["identifier"]
                administrator.phone = form.cleaned_data["phone"]

                if form.cleaned_data["photo"]:
                    administrator.picture = form.cleaned_data["photo"]

                # Update user data
                user = administrator.user
                user.first_name = form.cleaned_data["first_name"]
                user.last_name = form.cleaned_data["last_name"]
                user.email = form.cleaned_data["admin_email"]

                user.save()
                administrator.save()

                return HttpResponseRedirect('/company/view/')
            else:
                return render(request, 'company/administrator_edit.html',
                              {'form': form, 'errors': errors, 'pass_form': EmployeePasswordForm()})

    else:
        raise PermissionDenied

    return render(request, 'company/administrator_edit.html', {'form': form, 'pass_form': EmployeePasswordForm()})


def update_password(request):
    """
    url = administrator/updatePassword/

    parameters:
        currentpass: contraseña actual
        newpass1: contraseña a establecer
        newpass2: repetición de la contraseña

    returns:
        {'success': true/false: 'errors': [...]}

    errors:
        'formNotValid': si el formulario no es válido
        'passwordsDontMatch' : si las contraseñas no coinciden
        'currentPasswordInvalid" : si la contraseña actual no escorrecta

    template: ninguna (ajax)
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)

    if request.method == 'POST':
        # Process the form
        form = EmployeePasswordForm(request.POST)

        if form.is_valid():

            #Check password validation
            if not validate_pass(form.cleaned_data["currentpass"]):
                return JsonResponse({'success': False, 'errors': ['currentPasswordInvalid']})

            pass1 = form.cleaned_data["newpass1"]
            pass2 = form.cleaned_data["newpass2"]

            if pass1 != pass2:
                return JsonResponse({'success': False, 'errors': ['passwordsDontMatch']})

            user = admin.user
            user.set_password(pass1)
            user.save()
            update_session_auth_hash(request, user)

            return JsonResponse({'success': True, 'errors': []})
        else:
            # Invalid form
            return JsonResponse({'success': False, 'errors': ['formNotValid']})
