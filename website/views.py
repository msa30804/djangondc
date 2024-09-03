from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import OriginateForm
from .models import Originate
from django.db.models import Q 

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

###<--------------------------------- Originator module views-------------------------->###
@login_required
def originator_view(request):
    user = request.user

    # Count pending requests created by the user
    pending_count = Originate.objects.filter(created_by=user, is_completed=False).count()

    # Count under clearance requests: requests created by the user that are not completed and cleared by at least one other user
    under_clearance_count = Originate.objects.filter(
        created_by=user,
        is_completed=False,
        cleared_by__isnull=False
    ).exclude(cleared_by=user).count()

    # Count admin clearance requests: requests created by the user that are not completed and for the Administration department
    adm_cases_count = Originate.objects.filter(
        created_by=user,
        dept="Administration",
        is_completed=False
    ).count()

    # Count completed requests
    completed_count = Originate.objects.filter(
        created_by=user,
        is_completed=True
    ).count()

    # List of pending requests
    pending_requests = Originate.objects.filter(created_by=user, is_completed=False)

    # List of completed requests
    completed_requests = Originate.objects.filter(created_by=user, is_completed=True)

    context = {
        'pending_count': pending_count,
        'under_clearance_count': under_clearance_count,
        'adm_cases_count': adm_cases_count,
        'completed_count': completed_count,
        'pending_requests': pending_requests,
        'completed_requests': completed_requests,
    }

    return render(request, 'originator.html', context)


@login_required
def originate_view(request):
    if request.method == 'POST':
        form = OriginateForm(request.POST)
        if form.is_valid():
            originate = form.save(commit=False)
            originate.created_by = request.user
            originate.is_completed = False  # Ensure the request is not marked as completed
            originate.save()
            return redirect('pending')  # Redirect to the pending view after creation
    else:
        form = OriginateForm()
    return render(request, 'originate_form.html', {'form': form})


@login_required
def pending_view(request):
    # Query the Originate model for pending requests created by the current user
    pending_requests = Originate.objects.filter(created_by=request.user, is_completed=False)
    
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
    # Retrieve the search query from GET parameters
    search_query = request.GET.get('search', '')

    # Base queryset: requests created by the user, not completed, and cleared by at least one other user
    queryset = Originate.objects.filter(
        created_by=request.user,
        is_completed=False,
        cleared_by__isnull=False
    ).exclude(
        cleared_by=request.user
    ).distinct()

    # If there's a search query, filter the queryset
    if search_query:
        queryset = queryset.filter(
            Q(hr_no__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(appt__icontains=search_query) |
            Q(dept__icontains=search_query)
        )

    context = {
        'under_clearance_requests': queryset,
        'search_query': search_query,  # Pass search query to template for input value
    }
    return render(request, 'under_clearance.html', context)


@login_required
def under_clearance_detail_view(request, pk):
    # Fetch the specific request ensuring it's created by the current user and is under clearance
    originate_request = get_object_or_404(
        Originate,
        pk=pk,
        created_by=request.user,
        is_completed=False
    )

    # Fetch departments that have cleared the request
    cleared_departments = originate_request.cleared_by.values_list('profile__department', flat=True).distinct()

    # Determine which departments have not yet cleared the request
    not_cleared_departments = set(ALL_DEPARTMENTS) - set(cleared_departments)

    context = {
        'originate_request': originate_request,
        'cleared_departments': cleared_departments,
        'not_cleared_departments': not_cleared_departments,
        'all_departments': ALL_DEPARTMENTS,
    }
    return render(request, 'under_clearance_detail.html', context)


###<---------------------------------------Mark module views---------------------------------->###
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
def pending_marked_view(request):
    # Get requests created by other users that the current user needs to clear
    pending_requests = Originate.objects.exclude(created_by=request.user).filter(is_completed=False).exclude(cleared_by=request.user)

    if request.method == 'POST':
        record_id = request.POST.get('record_id')
        if record_id:
            record = get_object_or_404(Originate, id=record_id)
            if record.is_completed:
                # If already completed, do not allow to clear
                messages.error(request, "Request is already completed.")
            else:
                # Clear the request
                record.cleared_by.add(request.user)
                record.check_completion()  # Check if the record is completed
                messages.success(request, "Request has been marked as cleared.")
            return redirect('pending_marked')

    context = {'pending_requests': pending_requests}
    return render(request, 'pending_marked.html', context)


@login_required
def marked_view(request):
    # Get requests that the current user has cleared but are not yet completed
    marked_requests = Originate.objects.filter(cleared_by=request.user, is_completed=False)
    
    context = {'marked_requests': marked_requests}
    return render(request, 'marked.html', context)


# Define all departments (you can modify this list as per your requirements)
ALL_DEPARTMENTS = ['HR', 'Finance', 'IT', 'Administration', 'Marketing', 'Sales','Planning','Media','BT','Planning','Security','Operations','Engineers']
