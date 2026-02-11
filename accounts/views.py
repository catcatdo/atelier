from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from .forms import SignUpForm, ProfileForm


class AdminLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from axes.helpers import get_client_ip_address, get_client_parameters
            from axes.models import AccessAttempt
            from django.conf import settings
            import django.utils.timezone as timezone

            ip = get_client_ip_address(self.request)
            cooloff = getattr(settings, 'AXES_COOLOFF_TIME', None)
            failure_limit = getattr(settings, 'AXES_FAILURE_LIMIT', 5)

            if cooloff is not None:
                from datetime import timedelta
                threshold = timezone.now() - timedelta(hours=cooloff)
                failures = AccessAttempt.objects.filter(
                    ip_address=ip,
                    failures_since_start__gte=failure_limit,
                    attempt_time__gte=threshold,
                ).exists()
            else:
                failures = AccessAttempt.objects.filter(
                    ip_address=ip,
                    failures_since_start__gte=failure_limit,
                ).exists()
            context['locked_out'] = failures
        except Exception:
            context['locked_out'] = False
        return context


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to the Atelier!')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})
