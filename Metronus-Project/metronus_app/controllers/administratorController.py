from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.exceptions import  PermissionDenied
from metronus_app.forms.administratorForm import AdministratorForm
from metronus_app.model.administrator import Administrator
from metronus_app.common_utils import get_current_admin_or_403
from django.shortcuts import render


def edit(request, username):
    """
    url = administrator/edit/<username>

    parameters/returns:
    form: formulario de edicion de datos de administrador

    template: administrator_edit.html
    """

    administrator = get_object_or_404(Administrator, user__username=username, user__is_active=True)

    if request.method == "GET":
        # Return a form filled with the administrator's data
        form = AdministratorForm(initial={
            'first_name': administrator.user.first_name,
            'last_name': administrator.user.last_name,
            'email': administrator.user.email,
            'identifier': administrator.identifier,
            'phone': administrator.phone
        })
    elif request.method == "POST":
        # Process the received form
        
        form = AdministratorForm(request.POST)
        if form.is_valid() and checkPasswords(form):
            
            # Update employee data
            administrator.identifier = form.cleaned_data["identifier"]
            administrator.phone = form.cleaned_data["phone"]

            # Update user data
            user = administrator.user
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]

            # If a new password has been specified, change the current one and notify the user
            if form.cleaned_data["password1"]:
                user.set_password(form.cleaned_data["password1"])
                notify_password_change(user.email)

            user.save()
            administrator.save()

            return HttpResponseRedirect('/administrator/view/' + username + '/')

    else:
        raise PermissionDenied

    return render_to_response('administrator_edit.html', {'form': form})


def view(request, username):
    """
    url = administrator/view/<username>

    parameters/returns:
    administrator: datos del administrador

    template: company_view.html
    """

    # Check that the user is logged in and it's an administrator
    admin = get_current_admin_or_403(request)

    admin2 = get_object_or_404(Administrator, username=username)

    # Check that the admin has permission to view that company
    if admin2.company_id != admin.company_id:
        raise PermissionDenied

    return render(request, 'administrator_view.html', {'admin': admin2})


def delete(request, username):
    """
    url = administrator/delete/<username>

    parameters/returns:
    Nada, redirecciona a la vista de la compañía

    template: ninguna
    """
    pass  # TODO


def checkPasswords(form):
    return form.cleaned_data['password1'] == form.cleaned_data['password2']


def notify_password_change(email):
    """

    POR_DETERMINAR

    url = ..

    parameters/returns: ..

    template: ..
    """

    pass # TODO