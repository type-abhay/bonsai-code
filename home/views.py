from django.shortcuts import render,redirect
from home.models import problems
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required# Create your views here.

@login_required
def show_problems(request):
    all_prblms=problems.objects.all()
    return HttpResponse(all_prblms)

@login_required
def load_prblms(request):
    all_prlls = problems.objects.all()

    context = {
        'all_prlls':all_prlls,
    }
    template = loader.get_template('all_prlls.html')

    return HttpResponse(template.render(context,request))


@login_required
def prblm_detail(request,req_problem_id):
    problem_id = problems.objects.get(id=req_problem_id)

    context = {
        'req_problem_id':problem_id
    }

    template = loader.get_template('prblm_detail.html')

    return HttpResponse(template.render(context,request))
