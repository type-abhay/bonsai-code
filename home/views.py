from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.decorators import login_required
from home.forms import CodeSubmissionForm, UpdateUserForm, UpdateProfileForm
from home.models import problems, test_cases, UserSubmission
from django.conf import settings
import os
import uuid
import subprocess
import filecmp
from pathlib import Path
from .utils import APICALL
import re
import markdown
from django.contrib import messages
from .forms import ProblemsForm, TestCasesForm,TestCasesFormWID
#time out
from func_timeout import func_set_timeout, FunctionTimedOut, func_timeout
#heatmap
from django.db.models import Count
from django.db.models.functions import TruncDate
import pandas as pd
import datetime
import numpy as np
import plotly.graph_objects as go
# password
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin

# Create your views here.
# plotly, func_timeout, pandas, numpy


class ChangePasswordView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'change-password.html'
    success_message = "Successfully Changed Your Password"
    success_url = reverse_lazy('password_change')




def home(request):
    return render(request, 'home.html')

@login_required
def Profile(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='users-profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'edit-profile.html', {'user_form': user_form, 'profile_form': profile_form})

@login_required
def dashboard(request):
    if request.user.role == 'setter':
        user = request.user
        user_problems = problems.objects.filter(created_by=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)
        context = {
            'problems': user_problems,
            'user': user,
        }
        return render(request, 'my-prob.html', context)

    else:
        user = request.user
        plot_div = generate_github_style_heatmap(user)
            
        profile_form = UpdateProfileForm(instance=request.user.profile)
        total_submissions = UserSubmission.objects.filter(user=user).count()
        context = {
            'plot_div': plot_div,
            'user': user,
            'total_submissions': total_submissions,
            'has_submissions': total_submissions > 0
        }
        return render(request, 'dashboard.html', context)

# COUNTS FOR HEATMAP :)

def get_user_daily_submissions(user):
    """Optimized query for daily submission counts"""
    qs = (UserSubmission.objects
          .filter(user=user)
          .annotate(day=TruncDate('submitted_at'))
          .values('day')
          .annotate(count=Count('id'))
          .order_by('day'))
    return {item['day']: item['count'] for item in qs}



def generate_github_style_heatmap(user, year=None):
    today = datetime.date.today()
    if year is None:
        year = today.year
    
    #WEEKS CALC
    start_date = datetime.date(year, 1, 1)
    days_to_sunday = (start_date.weekday() + 1) % 7
    start_date = start_date - datetime.timedelta(days=days_to_sunday)
    
    end_date = datetime.date(year, 12, 31)
    days_from_saturday = (6 - end_date.weekday()) % 7
    end_date = end_date + datetime.timedelta(days=days_from_saturday)
    
    #DATE & SUB
    all_dates = pd.date_range(start=start_date, end=end_date)
    submission_counts = get_user_daily_submissions(user)
    counts = [submission_counts.get(date.date(), 0) for date in all_dates]
    
    
    df = pd.DataFrame({
        'date': all_dates,
        'count': counts,
    })
    
    #index and day
    df['week_index'] = ((df['date'] - df['date'].min()).dt.days // 7)
    df['dow'] = (df['date'].dt.dayofweek + 1) % 7 
    
    #matrix
    n_weeks = df['week_index'].max() + 1
    matrix = np.zeros((7, n_weeks))
    customdata_matrix = np.empty((7, n_weeks), dtype=object)
    
    #enterdata
    for _, row in df.iterrows():
        if 0 <= row['week_index'] < n_weeks:
            matrix[row['dow'], row['week_index']] = row['count']
            #date for hover
            date_str = row['date'].strftime('%B %d, %Y')
            customdata_matrix[row['dow'], row['week_index']] = date_str
    
    #coloring shi
    colorscale = [
        [0, '#B9B9B9'],      # No
        [0.2, '#c6e48b'],    # Low  
        [0.4, '#7bc96f'],    # Medium-low
        [0.6, '#239a3b'],    # Medium
        [0.8, '#196127'],    # High
        [1, '#0d4429']       # Very high
    ]
    
    zmax_value = matrix.max()
    if zmax_value == 0:
        zmax_value = 1

    #creating heatmap shi
    fig = go.Figure(data=go.Heatmap(
        z=matrix,
        customdata=customdata_matrix,  # date matrix
        colorscale=colorscale,
        showscale=False,
        hoverongaps=False,
        hovertemplate='<b>%{customdata}</b><br>Submissions: %{z}<extra></extra>',
        xgap=6,
        ygap=6,
        zmin=0,
        zmax=zmax_value
    ))
    
    #settings
    fig.update_layout(
        title={
            'text': f'{year} Submission Activity',
            'x': 0.5,
            'y' : 0.95,
            'font' : dict(family='Space Grotesk, sans-serif', size=20, color='white'),
        },
        xaxis={
            'title': '',
            'showticklabels': False,
            'showgrid': False,
            'zeroline': False
        },
        yaxis={
            'title': '',
            'tickmode': 'array',
            'tickvals': list(range(7)),
            'ticktext': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
            'showgrid': False,
            'zeroline': False,
            'autorange': 'reversed'
        },
        plot_bgcolor='rgba(255, 255, 255, 0)',
        paper_bgcolor='rgba(255, 255, 255, 0.2)',
        height=240,
        margin=dict(l=0, r=20, t=40, b=20),
        font=dict(size=12, color='white')
    )
    
    return fig.to_html(
        full_html=False, 
        include_plotlyjs='cdn',
        config={'displayModeBar': False}
    )

# ---HEATMAPS END---

# ---PROBLEMS TYPE SHI---

def load_prblms(request):
    all_prlls = problems.objects.all()
    context = {
        'all_prlls':all_prlls,
    }
    template = loader.get_template('all_prlls.html')
    return HttpResponse(template.render(context,request))

@login_required
def diff_probs(request, difficulty):
    """Filter problems by difficulty level"""
    valid_difficulties = [choice[0] for choice in problems.DIFF_CHOICES]
    
    if difficulty not in valid_difficulties:
        raise Http404("Invalid difficulty level")
    
    diff_probs = problems.objects.filter(difficulty=difficulty)
    difficulty_display = dict(problems.DIFF_CHOICES).get(difficulty, difficulty)
    
    context = {
        'all_prlls': diff_probs,
        'difficulty': difficulty,
        'difficulty_display': difficulty_display,
        'page_title': f'{difficulty_display} Problems'
    }
    return render(request, 'all_prlls.html', context)


@login_required
def search_results(request):
    query = request.GET.get('q')
    if query:
        results = problems.objects.filter(
            Q(prblmname__icontains=query) | Q(difficulty__icontains=query)
        )
    else:
        results = problems.objects.none()
    return render(request, 'search-result.html', {'results': results})


@login_required
def prblm_page(request,req_problem_id):
    if request.method == "POST":
        if 'RUN' in request.POST:
            form = CodeSubmissionForm(request.POST)
            if form.is_valid():
                if not form.cleaned_data['code']:
                    form.add_error('code', 'This field is required.')
                
                else:                    
                    submission = form.save()
                    print(submission.language)
                    print(submission.code)                
                    try:
                        # output = run_code(submission.language, submission.code, submission.input_data)
                        output = func_timeout(10, run_code, args=(submission.language, submission.code, submission.input_data))
                        submission.output_data = output
                        if not submission.input_data:
                            submission.input_data = "N/A"
                        submission.save()
                        return render(request, "result.html", {"submission": submission})

                    except FunctionTimedOut:
                        #Timeout error
                        submission.output_data = "Time Limit Exceeded, check for infinte loops/recursion."
                        if not submission.input_data:
                            submission.input_data = "N/A"
                        submission.save()
                        return render(request, "result.html", {"submission": submission})
            else:
                form = CodeSubmissionForm()  # If 'RUN' not in POST, show empty form

        elif 'SUBMIT' in request.POST:
            form = CodeSubmissionForm(request.POST)
            if form.is_valid():
                submission = form.save()
                print(submission.language)
                print(submission.code)
                tc_instances = test_cases.objects.filter(prblm_id=req_problem_id)
                for test_case in tc_instances:
                    input_string = test_case.input_data
                    output_string = test_case.output_data
                    # Split and clean the data
                    input_list = [item.strip() for item in input_string.split(',')]
                    output_list = [item.strip() for item in output_string.split(',')]

                print(input_list)
                print(output_list)
                n=len(input_list)
                flag = 1
                for i in range(n):
                    try:
                        # output = submit_code(submission.language, submission.code, input_list[i],output_list[i])
                        output = func_timeout(10, submit_code, args=(submission.language, submission.code, input_list[i],output_list[i]))
                        if output == 0:
                            res = (f"REJECTED! \nFailed Test Case: " + str(i+1))
                            flag = 1
                            break
                        elif output == 1:
                            res = "ACCEPTED"
                            flag = 0
                    
                    except FunctionTimedOut:
                        flag = 1
                        #Timeout error
                        submission.output_data = "Time Limit Exceeded, check for infinte loops/recursion."
                        submission.save()
                        return render(request, "sub-result.html", {"submission": submission})

                if flag==0:
                    UserSubmission.objects.create(user=request.user)
                submission.output_data = res
                if not submission.input_data:
                    submission.input_data = "N/A"
                submission.save()
                return render(request, "sub-result.html", {"submission": submission})

        elif 'AIREV':
            form = CodeSubmissionForm(request.POST)
            if form.is_valid():
                submission = form.save()
                problem = problems.objects.get(id=req_problem_id)
                print(submission.language)
                print(submission.code)                
                print("debug info: ABOUT TO CALL THIS AI SHIIIIIIIII")
                # Call Together AI API for code review
                output = APICALL(submission.language, submission.code,problem.prblmname)                
                submission.output_data = markdown.markdown(output,extensions=['fenced_code', 'codehilite'])
                submission.save()
                print("debug info: AI SHIIIIIIIII CALL SUCCESS")
                return render(request, "airev.html", {"submission": submission})
         
        
        problem_obj = problems.objects.get(id=req_problem_id)
        context = {
            'req_problem_id': problem_obj,
            'passform': form,
        }
        return render(request, "prblm_detail.html", context)

    else:
        form = CodeSubmissionForm()
        problem_obj = problems.objects.get(id=req_problem_id)
        context = {
            'req_problem_id': problem_obj,
            'passform': form,
        }
        return render(request, "prblm_detail.html", context)

# IDE


def only_comp(request):
    if request.method == "POST":
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            if not form.cleaned_data['code']:
                    form.add_error('code', 'This field is required.')
                    context = {'passform': form}
                    template = loader.get_template('only-comp.html')
                    return HttpResponse(template.render(context, request))
            else:

                submission = form.save()           
                print(submission.language)
                print(submission.code)                
                try:
                    # output = run_code(submission.language, submission.code, submission.input_data)
                    output = func_timeout(10, run_code, args=(submission.language, submission.code, submission.input_data))
                    submission.output_data = output
                    if not submission.input_data:
                        submission.input_data = "N/A"
                    submission.save()
                    return render(request, "result.html", {"submission": submission})

                except FunctionTimedOut:
                    #Timeout error
                    submission.output_data = "Time Limit Exceeded, check for infinte loops/recursion."
                    if not submission.input_data:
                        submission.input_data = "N/A"
                    submission.save()
                    return render(request, "result.html", {"submission": submission})
        else:
            form = CodeSubmissionForm()
            context = {'passform': form}
            template = loader.get_template('only-comp.html')
            return HttpResponse(template.render(context,request)) 

    else:
        form = CodeSubmissionForm()
        context = {'passform': form}
        template = loader.get_template('only-comp.html')
        return HttpResponse(template.render(context,request))

@login_required
def prblm_detail(request,req_problem_id):
    problem_id = problems.objects.get(id=req_problem_id)
    submit(request,req_problem_id)

    context = {
        'req_problem_id':problem_id
    }
    template = loader.get_template('home/prblm_detail.html')
    return HttpResponse(template.render(context,request))


# //RUN CODE BUTTON//
def run_code(language, code, input_data):
    print("INPUT" + input_data)
    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs"]

    for directory in directories:
        dir_path = project_path / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

    codes_dir = project_path / "codes"
    inputs_dir = project_path / "inputs"
    outputs_dir = project_path / "outputs"

    unique = str(uuid.uuid4())

    code_file_name = f"{unique}.{language}"
    input_file_name = f"{unique}.txt"
    output_file_name = f"{unique}.txt"

    code_file_path = codes_dir / code_file_name
    input_file_path = inputs_dir / input_file_name
    output_file_path = outputs_dir / output_file_name

    with open(code_file_path, "w") as code_file:
        code_file.write(code)

    with open(input_file_path, "w") as input_file:
        input_file.write(input_data)

    with open(output_file_path, "w") as output_file:
        pass  # empty file

    if language == "c":
        executable_path = codes_dir / unique
        compile_result = subprocess.run(["gcc", str(code_file_path), "-o", str(executable_path)])
        if compile_result.returncode == 0:
            with open(input_file_path, "r") as input_file:
                with open(output_file_path, "w") as output_file:
                    subprocess.run(
                        [str(executable_path)],
                        stdin=input_file,
                        stdout=output_file,
                    )
    
    elif language == "cpp":
        executable_path = codes_dir / unique
        compile_result = subprocess.run(["g++", str(code_file_path), "-o", str(executable_path)])
        if compile_result.returncode == 0:
            with open(input_file_path, "r") as input_file:
                with open(output_file_path, "w") as output_file:
                    subprocess.run(
                        [str(executable_path)],
                        stdin=input_file,
                        stdout=output_file,
                    )

    elif language == "py":
        
        with open(input_file_path, "r") as input_file:
            with open(output_file_path, "w") as output_file:
                subprocess.run(
                    ["python", str(code_file_path)],
                    stdin=input_file,
                    stdout=output_file,
                )

    
    with open(output_file_path, "r") as output_file:
        output_data = output_file.read()

    return output_data
    pass




# // SUBMIT CODE //
def submit_code(language, code, input_data,test_comp):
    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs","tests"]
    print("TEST:" + test_comp)

    for directory in directories:
        dir_path = project_path / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

    codes_dir = project_path / "codes"
    inputs_dir = project_path / "inputs"
    outputs_dir = project_path / "outputs"
    testcase_dir = project_path / "tests"

    unique = str(uuid.uuid4())
    #print("input data:" + input_data)

    code_file_name = f"{unique}.{language}"
    input_file_name = f"{unique}.txt"
    output_file_name = f"{unique}.txt"
    test_file_name = f"{unique}.txt"

    code_file_path = codes_dir / code_file_name
    input_file_path = inputs_dir / input_file_name
    output_file_path = outputs_dir / output_file_name
    test_file_path = testcase_dir / test_file_name

    with open(code_file_path, "w") as code_file:
        code_file.write(code)

    with open(input_file_path, "w") as input_file:
        input_file.write(input_data)

    with open(test_file_path, "w") as test_file:
        test_file.write(test_comp)

    with open(output_file_path, "w") as output_file:
        pass  # empty file

    if language == "c":
        executable_path = codes_dir / unique
        compile_result = subprocess.run(["gcc", str(code_file_path), "-o", str(executable_path)])
        if compile_result.returncode == 0:
            with open(input_file_path, "r") as input_file:
                with open(output_file_path, "w") as output_file:
                    subprocess.run(
                        [str(executable_path)],
                        stdin=input_file,
                        stdout=output_file,
                    )
    
    elif language == "cpp":
        executable_path = codes_dir / unique
        compile_result = subprocess.run(["g++", str(code_file_path), "-o", str(executable_path)])
        if compile_result.returncode == 0:
            with open(input_file_path, "r") as input_file:
                with open(output_file_path, "w") as output_file:
                    subprocess.run(
                        [str(executable_path)],
                        stdin=input_file,
                        stdout=output_file,
                    )

    elif language == "py":
        with open(input_file_path, "r") as input_file:
            with open(output_file_path, "w") as output_file:
                subprocess.run(
                    ["python", str(code_file_path)],
                    stdin=input_file,
                    stdout=output_file,
                )

    #cleaning op data
    with open(output_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    clean_content = re.sub(r'\s+', '', content)
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    # Read op data
    with open(output_file_path, "r") as output_file:
        output_data = output_file.read()

    with open(test_file_path, "r") as test_file:
        out_data = test_file.read()

    print("OUTPUT\n"+ output_data)
    print("TEST CASE\n"+ out_data)
    result = filecmp.cmp(output_file_path,test_file_path, shallow=False)
    if (result==True):
        return 1
    
    else:
        return 0
    
    
# Problem Setter Part 
#First function don't have a frontend cause I didn't feel the need, maybe I'd make one for testcases(done)

def create_problem(request):
    if request.method == 'POST':
        if request.user.role != 'setter':
            return redirect('/home/problems')
        form = ProblemsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Problem created successfully!')
            return redirect('create_problem')
    else:
        form = ProblemsForm()
    
    return render(request, 'create_problem.html', {'form': form})

def create_test_case(request):
    if request.method == 'POST':
        if request.user.role != 'setter':
            return redirect('home/problems')
        form = TestCasesFormWID(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Test case created successfully!')
            return redirect('create_test_case')
    else:
        form = TestCasesFormWID()
    
    return render(request, 'create_test_case.html', {'form': form})


def create_problem_with_test_cases(request):
    if request.method == 'POST':
        if hasattr(request.user, 'role') and request.user.role != 'setter':
            return redirect('problems')
        
        problem_form = ProblemsForm(request.POST, prefix='problem')
        test_case_form = TestCasesForm(request.POST, prefix='testcase')
        
        if problem_form.is_valid() and test_case_form.is_valid():
            # ALWAYS REMEMBER SAVE THE PROBLEM FIRST WITHOUT COMMIT AS I NEED TO ADD THE USER_ID LATER!
            problem = problem_form.save(commit=False)
            problem.created_by = request.user
            problem.save()
            
            # also testcases need prbml_id so problem is saved first
            test_case = test_case_form.save(commit=False)
            test_case.prblm_id = problem 
            test_case.save()
            
            messages.success(request, 'Problem and test case created successfully!')
            return redirect('create_problem_with_test_cases')
        else:
            #debug (0_0)
            if not problem_form.is_valid():
                print("Problem form errors:", problem_form.errors)
            if not test_case_form.is_valid():
                print("Test case form errors:", test_case_form.errors)
    else:
        problem_form = ProblemsForm(prefix='problem')
        test_case_form = TestCasesForm(prefix='testcase')
    
    return render(request, 'create-combined.html', {
        'problem_form': problem_form,
        'test_case_form': test_case_form
    })


def edit_problem(request, pk):
    problem = get_object_or_404(problems, pk=pk)

    # Get the first related test case (or None if not found)
    test_case_instance = test_cases.objects.filter(prblm_id=problem).first()

    if request.method == 'POST':
        form = ProblemsForm(request.POST, instance=problem)
        test_form = TestCasesForm(request.POST, instance=test_case_instance)
        if form.is_valid() and test_form.is_valid():
            form.save()
            test_case = test_form.save(commit=False)
            test_case.prblm_id = problem  # Ensure FK is set
            test_case.save()
            messages.success(request, 'Problem and test case updated successfully!')
            return redirect('edit-problem', pk=problem.pk)
    else:
        form = ProblemsForm(instance=problem)
        test_form = TestCasesForm(instance=test_case_instance)

    return render(request, 'edit-problem.html', {
        'problem_form': form,
        'test_case_form': test_form,
    })


def delete_problem(request, pk):
    problem = get_object_or_404(problems, pk=pk)
    problem.delete()  # This will also delete all related TestCase objects if on_delete=CASCADE
    messages.success(request, "Problem and its test cases deleted successfully!")
    return redirect('dashydashy')