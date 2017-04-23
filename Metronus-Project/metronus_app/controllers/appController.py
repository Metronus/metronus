from django.shortcuts import render
from metronus_app.forms.contactForm import ContactForm
from metronus_app.common_utils import send_mail
from metronus.settings import DEFAULT_FROM_EMAIL
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.views import deprecate_current_app
from metronus_app.common_utils import check_user_email

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

            context = {
                "html": False
            }

            recipients = [DEFAULT_FROM_EMAIL]
            if copy_to_user:
                recipients.append(email)

            send_mail("Metronus Contact: "+subject+" - "+name, body, recipients, None, context, email)

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


@deprecate_current_app
@csrf_protect
def password_reset(request,
                   template_name='registration/password_reset_form.html',
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   extra_context=None,
                   html_email_template_name=None,
                   extra_email_context=None):
    """
    Deprecated. Request for new password
    """
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        errors = []
        if form.is_valid():
            if check_user_email(form.cleaned_data["email"]):
                opts = {
                    'use_https': request.is_secure(),
                    'token_generator': token_generator,
                    'from_email': from_email,
                    'email_template_name': email_template_name,
                    'subject_template_name': subject_template_name,
                    'request': request,
                    'html_email_template_name': html_email_template_name,
                    'extra_email_context': extra_email_context,
                }
                form.save(**opts)
                return HttpResponseRedirect(post_reset_redirect)
            else:
                errors.append('invalidEmail')
                return render(request, template_name, {'form': form, 'errors': errors})

    else:
        form = password_reset_form()
    context = {
        'form': form,
        'title': _('Password reset'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
