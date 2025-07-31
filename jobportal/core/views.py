from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from .forms import CustomUserCreationForm, JobForm, ApplicationForm
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Job, Application
from django.db.models import Q, Count
from .forms import EducationalQualificationForm
from .models import EducationalQualification
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST


EDU_RANK = {
    'postdoc': 6, 'phd': 5, 'masters': 4, 'graduation': 3, 'diploma': 2, 'college': 1, 'school': 0
}


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.role == 'employer':
        job_list = Job.objects.filter(posted_by=request.user).annotate(app_count=Count('application'))
        paginator = Paginator(job_list, 5)  # Show 5 jobs per page
        page_number = request.GET.get('page')
        jobs = paginator.get_page(page_number)
        return render(request, 'core/employer_dashboard.html', {'jobs': jobs})
    else:
        status = request.GET.get('status')
        applications_list = Application.objects.filter(applicant=request.user)
        if status in ['pending', 'approved', 'rejected']:
            applications_list = applications_list.filter(status=status)
        paginator = Paginator(applications_list, 5)  # 5 per page, adjust as needed
        page_number = request.GET.get('page')
        applications = paginator.get_page(page_number)
        return render(request, 'core/applicant_dashboard.html', {
            'applications': applications,
            'selected_status': status,
        })



@login_required
def post_job(request):
    if request.user.role != 'employer':
        return redirect('dashboard')
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            return redirect('dashboard')
    else:
        form = JobForm()
    return render(request, 'core/post_job.html', {'form': form})

def job_list(request):
    query = request.GET.get('q')
    jobs = Job.objects.all()
    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(company_name__icontains=query) |
            Q(location__icontains=query)
        )
    if not request.user.is_authenticated and 'apply_redirect' in request.GET:
        messages.info(request, "Please login or register to apply for jobs.")

    paginator = Paginator(jobs, 5)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.get_page(1)

    return render(request, 'core/job_list.html', {
        'jobs': page_obj,
        'query': query,
        'messages': messages.get_messages(request),
    })




@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    # Prevent duplicate application
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.error(request, "You have already applied for this job.")
        return redirect('job_list')
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            return redirect('dashboard')
    else:
        form = ApplicationForm()
    return render(request, 'core/apply_job.html', {'form': form, 'job': job})



@login_required
def job_applicants(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applicants = Application.objects.filter(job=job)
    EDU_RANK = {
        'postdoc': 6, 'phd': 5, 'masters': 4, 'graduation': 3,
        'diploma': 2, 'college': 1, 'school': 0
    }

    if request.method == 'POST':
        app_id = request.POST.get('application_id')
        action = request.POST.get('action')
        application = get_object_or_404(Application, id=app_id, job=job)
        if action == 'approve':
            application.status = 'approved'
        elif action == 'reject':
            application.status = 'rejected'
        application.save()
        return redirect('job_applicants', job_id=job.id)

    for app in applicants:
        quals = list(app.applicant.qualifications.all())
        app.highest_degree = None
        if quals:
            app.highest_degree = max(quals, key=lambda q: EDU_RANK.get(q.degree, -1)).degree

    return render(request, 'core/job_applicants.html', {
        'job': job,
        'applicants': applicants,
    })





def home(request):
    return render(request, 'core/job_list.html', {'jobs': Job.objects.all()})

@login_required
def applicant_profiles(request):
    if request.user.role != 'employer':
        return redirect('dashboard')
    from .models import EducationalQualification
    EDU_RANK = {
        'postdoc': 6, 'phd': 5, 'masters': 4, 'graduation': 3,
        'diploma': 2, 'college': 1, 'school': 0
    }
    applicants = CustomUser.objects.filter(role='applicant', qualifications__isnull=False).distinct()
    ranked = sorted(
        applicants,
        key=lambda u: (
            max([EDU_RANK.get(q.degree, -1) for q in u.qualifications.all()], default=-1),
            u.experience_years or 0
        ),
        reverse=True
    )
    return render(request, 'core/applicant_profiles.html', {'applicants': ranked})



@login_required
def view_resumes(request):
    if request.user.role != 'employer':
        return redirect('dashboard')
    resumes = Application.objects.select_related('applicant', 'job') \
        .filter(job__posted_by=request.user) \
        .order_by('-applied_at')
    return render(request, 'core/resume_list.html', {'resumes': resumes})


@login_required
def manage_qualifications(request):
    if request.user.role != 'applicant':
        return redirect('dashboard')

    EDU_RANK = {
            'postdoc': 6, 'phd': 5, 'masters': 4, 'graduation': 3,
            'diploma': 2, 'college': 1, 'school': 0
        }
    qualifications = sorted(
            request.user.qualifications.all(),
            key=lambda q: (
                q.year if q.year is not None else 0,
                EDU_RANK.get(q.degree, -1)
            ),
            reverse=True
    )
    form = EducationalQualificationForm()
    edit_id = None

    if request.method == 'POST':
        if 'experience_years' in request.POST:
            try:
                experience = int(request.POST['experience_years'])
                request.user.experience_years = experience
                request.user.save()
            except ValueError:
                messages.error(request, "Invalid experience value. Please enter a number.")

        if 'delete_id' in request.POST:
            EducationalQualification.objects.filter(id=request.POST['delete_id'], applicant=request.user).delete()
            messages.success(request, "Qualification deleted successfully.")
            return redirect('manage_qualifications')

        elif 'edit_id' in request.POST:
            edit_id = request.POST['edit_id']
            qual = EducationalQualification.objects.get(id=edit_id, applicant=request.user)
            form = EducationalQualificationForm(instance=qual)

        elif 'update_id' in request.POST:
            update_id = request.POST['update_id']
            qual = EducationalQualification.objects.get(id=update_id, applicant=request.user)
            form = EducationalQualificationForm(request.POST, instance=qual)
            if form.is_valid():
                new_degree = form.cleaned_data['degree']
                if EducationalQualification.objects.filter(degree=new_degree, applicant=request.user).exclude(id=qual.id).exists():
                    messages.error(request, "You already have a qualification with this degree.")
                else:
                    form.save()
                    messages.success(request, "Qualification updated successfully.")
                    return redirect('manage_qualifications')

        else:
            form = EducationalQualificationForm(request.POST)
            if form.is_valid():
                new_degree = form.cleaned_data['degree']
                if EducationalQualification.objects.filter(degree=new_degree, applicant=request.user).exists():
                    messages.error(request, "You already have a qualification with this degree.")
                else:
                    qual = form.save(commit=False)
                    qual.applicant = request.user
                    qual.save()
                    messages.success(request, "Qualification added successfully.")
                    return redirect('manage_qualifications')

    return render(request, 'core/manage_qualifications.html', {
        'form': form,
        'qualifications': qualifications,
        'edit_id': edit_id,
        'experience_years': request.user.experience_years
    })



@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully.')
            return redirect('dashboard')
    else:
        form = JobForm(instance=job)
    return render(request, 'core/edit_job.html', {'form': form, 'job': job})



@login_required
@require_POST
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    job.delete()
    messages.success(request, 'Job deleted successfully.')
    return redirect('dashboard')


