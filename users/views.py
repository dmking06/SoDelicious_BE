import environ

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import smart_text, smart_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .decorators import unauthenticated_user
from .forms import RegisterForm, LoginForm, ProfileForm
from .models import Profile
from .tokens import account_activation_token

User = get_user_model()

app_name = "So Delicious"

env = environ.Env(
        # set casting, default value
        SEND_EMAIL=(bool, True)
        )
# reading .env file
environ.Env.read_env()

# Send email or instant verification
send_email = env.bool('SEND_EMAIL')


# Login - only unauthenticated users can see this page
@unauthenticated_user
def login_view(request):
    # Check if request was POST
    if request.method == 'POST':
        # Get username & password
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, email=email, password=password)

        # Verify user is valid
        if user is not None:
            # Login user
            login(request, user)

            # redirect to Homepage:
            return redirect('landing_page')
        else:
            # Display error message
            messages.error(request, "Invalid login. Please try again.")

    # Render login page with any bound data and error messages
    context = {'form': LoginForm()}
    return render(request, 'users/login.html', context)


# Register - only unauthenticated users can see this page
@unauthenticated_user
def register_view(request):
    # Create blank form
    form = RegisterForm()

    # Check if request was POST
    if request.method == 'POST':
        # Populate the form with POST data
        form = RegisterForm(request.POST)

        # Verify form data is valid
        if form.is_valid():
            # Deactivate user until email is verified
            user = form.save(commit=False)
            user.is_active = False

            # Save the User model
            user.save()

            # If send_email is true, an email will be sent,
            # and user must go to link to activate account.
            if send_email:
                # Create verification email
                current_site = get_current_site(request)
                subject = f"Activate your {app_name} Account"
                message = render_to_string('users/activation_email.html',
                                           {
                                               'user'  : user,
                                               'scheme': request.scheme,
                                               'domain': current_site.domain,
                                               'uid'   : urlsafe_base64_encode(smart_bytes(user.pk)),
                                               'token' : account_activation_token.make_token(user),
                                               })

                # Send email
                user.email_user(subject, message)

                # Redirect to login page
                messages.success(request, f'A verification email has been sent to {user.email}.')
                messages.success(request, f'Please verify your email to complete registration.')
                return redirect('users:login')

            # If send_email is False, the user will be activated automatically
            else:
                # Activate the user
                user.is_active = True
                user.save()
                # Login the user
                login(request, user)
                messages.success(request, f'Your account has been confirmed.')
                return redirect('landing_page')

    # Render the form with any bound data
    context = {'form': form}
    return render(request, 'users/register.html', context)


# Activate user - idb64 and token are supplied by the url
@unauthenticated_user
def activate_view(request, uidb64, token):
    if request.method == 'GET':
        # Retrieve user using the uid
        try:
            uid = smart_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

        # If user cannot be retrieved, catch the error
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as err:
            user = None
            print(f"User is none:\n{err}")

        # If user is found, verify the token
        if user is not None and account_activation_token.check_token(user, token):
            # Activate the user and log them in
            user.is_active = True
            user.save()

            # Create confirmation email
            current_site = get_current_site(request)
            subject = f"{app_name} Registration complete."
            message = render_to_string('users/confirmation_email.html',
                                       {
                                           'user'  : user,
                                           'app'   : app_name,
                                           'scheme': request.scheme,
                                           'domain': current_site.domain,
                                           })

            # Send email
            user.email_user(subject, message)

            # Login the user
            login(request, user)
            messages.success(request, f'Your account has been confirmed.')
            return redirect('landing_page')

        # If user is not found, show error message
        else:
            messages.warning(request, 'The confirmation link was invalid, '
                                      'possibly because it has already been used.')
            return redirect('landing_page')


# Logout
def logout_view(request):
    # Logout user and send to login page
    logout(request)
    messages.info(request, "Successfully logged out.")
    return redirect("users:login")


# User Info - must be logged in to access this page
@login_required(login_url="users:login")
def user_info_view(request):
    # Get current user and profile
    user = request.user
    profile = Profile.objects.get(user=user)

    # Create form with current user info
    form = ProfileForm(initial={'email': user.email,
                                'full_name': profile.full_name,
                                'subscribed': profile.subscribed
                                })

    # Check if request was POST
    if request.method == 'POST':
        # Load the form using POST data
        form = ProfileForm(request.POST,
                           initial={'email': user.email,
                                    'full_name': profile.full_name,
                                    'subscribed': profile.subscribed
                                    })

        # Verify form data is valid
        if form.is_valid() and form.has_changed():
            print("valid and changed")
            # Save the updates and reload page with data
            user.email = form.cleaned_data['email']
            user.save()
            profile.full_name = form.cleaned_data['full_name']
            profile.subscribed = form.cleaned_data['subscribed']
            profile.save()
            messages.success(request, "Updated user profile.")
            return redirect('users:user_info')

    # Render the form with any bound data
    context = {'form': form}
    return render(request, 'users/user_info.html', context)
