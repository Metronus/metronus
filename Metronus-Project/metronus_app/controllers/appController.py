from django.shortcuts import render
from django.core.exceptions                      import PermissionDenied
from django.http import HttpResponseRedirect
from metronus_app.forms.contactForm import ContactForm
from metronus_app.common_utils import send_mail
from metronus.settings import DEFAULT_FROM_EMAIL


def index(request):
    """
    returns:
    to be redirected after login

    template:
    app_index.html
    """
    if not request.user.is_authenticated():
        return HttpResponseRedirect("/login/")

    return render(request, "app_index.html")


def contact(request):
    """
    parameters/returns:
    form: formulario de contacto para la empresa

    template:
    contact_form.html
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ContactForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            body = form.cleaned_data['body']

            copy_to_user = form.cleaned_data['copy_to_user']

            context = {}

            send_mail(subject+" - "+name, body, copy_to_user if [DEFAULT_FROM_EMAIL,email] else [DEFAULT_FROM_EMAIL,email], None, context, email)

            # redirect to a new URL:
            return HttpResponseRedirect('/contact-done/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ContactForm()

    return render(request, 'contact_form.html', {'form': form})


def contact_done(request):
    """
    returns:
    to be redirected after contact form

    template:
    contact_done.html
    """
    return render(request, "contact_done.html")
