from django.shortcuts import render,redirect
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from home.forms import CodeSubmissionForm, UpdateUserForm, UpdateProfileForm
from home.models import problems, test_cases
from django.conf import settings
import os
import uuid
import subprocess
import filecmp
from pathlib import Path
import re
# Create your views here.


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
def load_prblms(request):
    all_prlls = problems.objects.all()

    context = {
        'all_prlls':all_prlls,
    }
    template = loader.get_template('all_prlls.html')
    return HttpResponse(template.render(context,request))


@login_required
def prblm_page(request,req_problem_id):
    if request.method == "POST":
        if 'RUN' in request.POST:
            form = CodeSubmissionForm(request.POST)
            if form.is_valid():
                submission = form.save()
                print(submission.language)
                print(submission.code)                
                output = run_code(submission.language, submission.code, submission.input_data)
                submission.output_data = output
                submission.save()
                return render(request, "result.html", {"submission": submission})
        
        elif 'SUBMIT' in request.POST:
            form = CodeSubmissionForm(request.POST)
            if form.is_valid():
                submission = form.save()
                print(submission.language)
                print(submission.code)
                input_instance = test_cases.objects.get(pk=1)
                input_string = input_instance.input_data
                input_list = input_string.split(',')
                print(input_list)
                output_instance = test_cases.objects.get(pk=1)
                output_string = output_instance.output_data
                output_list = output_string.split(',')
                cleaned_list = [item.strip() for item in output_list]
                print(cleaned_list)
                n=len(cleaned_list)
                for i in range(n):
                    output = submit_code(submission.language, submission.code, input_list[i],cleaned_list[i])
                    if output == 0:
                        res = "REJECTED"
                        break
                    res = "ACCEPTED"
                submission.output_data = res
                submission.save()
                return render(request, "result.html", {"submission": submission})
    else:
        form = CodeSubmissionForm()
        problem_id = problems.objects.get(id=req_problem_id)
        context = {
        'req_problem_id':problem_id,
        'passform': form,
        }
        
    template = loader.get_template('prblm_detail.html')
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
        pass  # This will create an empty file

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
        # Code for executing Python script
        with open(input_file_path, "r") as input_file:
            with open(output_file_path, "w") as output_file:
                subprocess.run(
                    ["python", str(code_file_path)],
                    stdin=input_file,
                    stdout=output_file,
                )

    # Read the output from the output file
    with open(output_file_path, "r") as output_file:
        output_data = output_file.read()

    return output_data




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
        pass  # This will create an empty file

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
        # Code for executing Python script
        with open(input_file_path, "r") as input_file:
            with open(output_file_path, "w") as output_file:
                subprocess.run(
                    ["python", str(code_file_path)],
                    stdin=input_file,
                    stdout=output_file,
                )

    #clean the output file for comparison
    with open(output_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    clean_content = re.sub(r'\s+', '', content)
    with open(output_file_path, 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    # Read the output from the output file
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
    
    
