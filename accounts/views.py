from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.db.models import Q
from .models import CustomUser, VerifiedEmail, Problem, Submission, SubmissionTestCaseResult
from .judge0 import submit_code_to_judge0, get_submission_result
from django.core.mail import send_mail
from functools import wraps
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import random
import time
import re


def home(request):
    if request.user.is_authenticated:
        return redirect('explore')
    return render(request, 'index.html')

@login_required
def premium(request):
    return render(request, 'premium.html', {'title':"Premium"})

def terms(request):
    return render(request, 'terms.html', {'title':"Terms and Conditions"})

def privacypolicy(request):
    return render(request, 'privacypolicy.html', {'title':"PrivacyPolicy"})

def explore(request):
    return render(request, 'explore.html', {'title':"Explore"})

def dsadashboard(request):
    return render(request, 'dsadashboard.html', {'title':"Dsa-Dashboard"})

def sqldashboard(request):
    return render(request, 'sqldashboard.html', {'title':"Sql-Dashboard"})


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not re.match(r'^[A-Za-z0-9_]{3,30}$', username):
            return render(request, 'signup.html', {
                'error': 'Invalid Username'
            })

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'signup.html', {'error': 'Invalid email address'})

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'Email already exists'})

        if len(password) < 8:
            return render(request, 'signup.html', {'error': 'Password must be at least 8 characters'})

        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        request.session['pending_signup'] = {
            'username': username,
            'email': email,
            'password': password
        }

        code = f'{random.randint(100000, 999999)}'
        request.session['verification_code'] = code
        request.session['last_verification_sent'] = time.time()
        request.session.set_expiry(60 * 15)

        send_mail(
            subject='Verify Your email - Codehub',
            message=f'Use this code to verify your email: {code}',
            from_email='codehub@gmail.com',
            recipient_list=[email],
            fail_silently=False
        )

        return redirect('verifyemail')

    return render(request, 'signup.html', {'title': 'Signup'})


def login(request):
    if request.method == 'POST':
        identifier = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')

        if not re.match(r'^[A-Za-z0-9_]{3,30}$', identifier):
            return render(request, 'login.html', {
                'error': 'Invalid Username'
            })

        user = authenticate(request, username=identifier, password=password)

        if user and user.check_password(password):
            auth_login(request,user)
            if remember_me:
                request.session.set_expiry(60 * 60 * 24 * 30)
            else:
                request.session.set_expiry(0)
            return redirect('/')
        else:
            return render(request, 'login.html',{'error':'Invalid Username or Password'})
        
    else:
        return render(request, 'login.html', {'title': 'Login'})
    


def logout(request):
    auth_logout(request)
    return redirect('login')

def forgotpassword(request):
    return render(request, 'forgotpassword.html', {'title': 'Forgot Password'})

def send_verification_email(user):
    code = f'{random.randint(100000,999999)}'
    VerifiedEmail.objects.update_or_create(user = user, defaults={'code':code})

    send_mail(
        subject='Verify Your email - Codehub',
        message=f'Use this code to verify your email {code}',
        from_email='codehub@gmail.com',
        recipient_list=[user.email],
        fail_silently=False)
    
def verifyemail(request):
    if request.method == "POST":
        entered_code = request.POST.get('code')
        stored_code = request.session.get('verification_code')
        signup_data = request.session.get('pending_signup')

        if not signup_data or not stored_code:
            return redirect('signup') 
        
        if not entered_code.isdigit():
            return render(request, 'verification.html', {'error': 'Code must be numeric'})

        if entered_code == stored_code:
            user = CustomUser.objects.create_user(
                username=signup_data['username'],
                email=signup_data['email'],
                password=signup_data['password']
            )
            user.is_verified = True
            user.save()

            del request.session['pending_signup']
            del request.session['verification_code']

            auth_login(request, user)
            return redirect('/')
        else:
            return render(request, 'verification.html', {'error': 'Verification code does not match'})

    return render(request, 'verification.html', {'title': 'Email Verification'})




def email_verification_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_verified:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('verification')
    return wrapper

def resend_verification_email(request):
    last_sent = request.session.get('last_verification_sent')
    now = time.time()

    if last_sent and now - last_sent < 60:
        wait_time = int(60 - (now - last_sent))
        return render(request, 'verification.html', {'error': f'Please wait {wait_time} seconds before resending the code.'})
    
    signup_data = request.session.get('pending_signup')
    if not signup_data:
        return redirect('signup')

    email = signup_data.get('email')
    code = f'{random.randint(100000, 999999)}'
    request.session['verification_code'] = code
    request.session['last_verification_sent'] = now

    send_mail(
        subject='Verify Your email - Codehub',
        message=f'Use this code to verify your email: {code}',
        from_email='codehub@gmail.com',
        recipient_list=[email],
        fail_silently=False
    )

    return redirect('verifyemail')




def problem_list(request):

    query = request.GET.get('q', '').strip()
    top_users = CustomUser.objects.order_by('-points')[:10]

    if query:
        words = query.split()
        q_objects = Q()

        for word in words:
            q_objects |= Q(title__icontains=word)

        matching_problems = Problem.objects.filter(q_objects).distinct()
        non_matching_problems = Problem.objects.exclude(id__in=matching_problems.values_list('id', flat=True))

        problems = list(matching_problems) + list(non_matching_problems)
    else:
        problems = Problem.objects.all()

    return render(request, "question.html", {
        "problems": problems,
        "title": "Problems",
        "top_users": top_users
    })


@login_required
def submit_solution(request, problem_slug):
    problem = get_object_or_404(Problem, slug=problem_slug)
    test_case_results = None
    submission = None

    if request.method == "POST":
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        submissions_today_count = Submission.objects.filter(
            user=request.user,
            problem=problem,
            submitted_at__gte=today_start
        ).count()

        if submissions_today_count >= 3:
            return render(request, 'submit_solution.html', {
                'title': 'CodeSubmit',
                'problem': problem,
                'submission': submission,
                'test_case_results': test_case_results,
                'error': "You have reached the daily submission limit of 3 for this problem."
            })

        already_solved = Submission.objects.filter(
            user=request.user,
            problem=problem,
            status="Accepted"
        ).exists()

        code = request.POST.get('code')
        language_id = int(request.POST.get('language_id'))

        submission = Submission.objects.create(
            user=request.user,
            problem=problem,
            code=code,
            language_id=language_id,
            status="RUNNING"
        )

        all_passed = True
        max_time = 0
        max_memory = 0
        last_output = ""

        for testcase in problem.testcases.all():
            token = submit_code_to_judge0(
                sourcecode=code,
                language_id=language_id,
                stdin=testcase.input_data,
                expected_output=testcase.expected_output,
                time_limit=problem.time_limit,
                memory_limit=problem.memory_limit
            )

            result = get_submission_result(token)

            if result is None:
                status_desc = 'System Error'
                output = ''
                time_used = 0
                memory_used = 0
                all_passed = False
            else:
                status_desc = result.get("status", {}).get('description', 'Unknown')
                output = result.get('stdout', "")
                time_used = float(result.get('time') or 0)
                memory_used = int(result.get('memory') or 0)

            if status_desc != 'Accepted':
                all_passed = False

            SubmissionTestCaseResult.objects.create(
                submission=submission,
                testcase=testcase,
                output=output,
                status=status_desc,
                time=time_used,
                memory=memory_used
            )

            max_time = max(max_time, time_used)
            max_memory = max(max_memory, memory_used)
            last_output = output

            if not all_passed:
                break

        LANGUAGE_MAP = {
            71: 'Python 3',
            54: 'C++',
            62: 'Java',
        }

        submission.status = 'Accepted' if all_passed else status_desc
        submission.language_name = LANGUAGE_MAP.get(language_id, 'Unknown')
        submission.time = max_time or None
        submission.memory = max_memory or None
        submission.output = last_output
        submission.save()

        if all_passed and not already_solved:
            request.user.points += problem.points
            request.user.save()

        test_case_results = submission.testcase_results.all()

    return render(request, 'submit_solution.html', {
        'title': 'CodeSubmit',
        'problem': problem,
        'submission': submission,
        'test_case_results': test_case_results
    })



def leaderboard_view(request):
    top_users = CustomUser.objects.order_by('-points')[:10]  # Top 10 by points
    return render(request, 'question.html', {
        'title': 'Leaderboard',
        'top_users': top_users
    })

DSA_TOPICS = ['home', 'array', 'linkedlist', 'trees']

def dsa_topic_content(request, topic_name):
    if topic_name not in DSA_TOPICS:
        raise Http404("Topic not found")
    return render(request, f"dsa/partials/{topic_name}.html")      


SQL_TOPICS = ['home', 'basic', 'processing']

def sql_topic_content(request, topic_name):
    if topic_name not in SQL_TOPICS:
        raise Http404("Topic not found")
    return render(request, f"sql/partials/{topic_name}.html")