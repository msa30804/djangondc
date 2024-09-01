from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import OriginateForm
from .models import Originate

def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You Have Been Logged In!")
            return redirect('home')
        else:
            messages.error(request, "There Was An Error Logging In, Please Try Again...")
            return redirect('home')

    return render(request, 'home.html')

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('home')

@login_required
def originator_view(request):
    pending_requests = Originate.objects.filter(created_by=request.user, is_completed=False)
    completed_requests = Originate.objects.filter(created_by=request.user, is_completed=True)
    context = {
        'pending_requests': pending_requests,
        'completed_requests': completed_requests,
    }
    return render(request, 'originator.html', context)

@login_required
def mark_view(request):
    # Exclude records created by the logged-in user
    originate_records = Originate.objects.exclude(created_by=request.user).filter(is_completed=False)
    
    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        if record_id:
            record = get_object_or_404(Originate, id=record_id)
            record.cleared_by.add(request.user)
            record.check_completion()
            return redirect('mark')

    context = {'originate_records': originate_records}
    return render(request, 'mark.html', context)

@login_required
def pending_view(request):
    pending_requests = Originate.objects.filter(created_by=request.user, is_completed=False, cleared_by__isnull=True)
    context = {'pending_requests': pending_requests}
    return render(request, 'pending.html', context)

@login_required
def completed_view(request):
    completed_requests = Originate.objects.filter(created_by=request.user, is_completed=True)
    context = {'completed_requests': completed_requests}
    return render(request, 'completed.html', context)

@login_required
def adm_clearance_view(request):
    adm_clearance_requests = Originate.objects.filter(created_by=request.user, dept="Administration", is_completed=False)
    context = {'adm_clearance_requests': adm_clearance_requests}
    return render(request, 'adm_clearance.html', context)

@login_required
def under_clearance_view(request):
    # Get requests created by the logged-in user that are not completed
    # and have been cleared by at least one other user
    under_clearance_requests = Originate.objects.filter(
        created_by=request.user,
        is_completed=False,
        cleared_by__isnull=False
    ).exclude(cleared_by=request.user)  # Exclude requests cleared by the current user
    
    context = {'under_clearance_requests': under_clearance_requests}
    return render(request, 'under_clearance.html', context)


@login_required
def originate_view(request):
    if request.method == 'POST':
        form = OriginateForm(request.POST)
        if form.is_valid():
            originate = form.save(commit=False)
            originate.created_by = request.user
            originate.save()
            return redirect('originator')
    else:
        form = OriginateForm()
    return render(request, 'originate_form.html', {'form': form})

