from django.urls import path
from home.views import load_prblms
from home.views import prblm_detail
from home.views import prblm_page
from home.views import submit_code
from home.views import run_code
from home.views import Profile
from home.views import only_comp
from home.views import create_problem_with_test_cases, create_problem,create_test_case, dashboard

# from home.views import callviews

urlpatterns = [
    path("problems/", load_prblms, name="all-problem-list"),
    path('edit-profile/', Profile, name='users-profile'),
    path('compiler/', only_comp, name='only-compiler'),
    path("problems/<int:req_problem_id>/", prblm_page, name="Compiler Problems Page"),
    path("problems/<int:req_problem_id>/output ",run_code, name="Output-Page"),
    path("problems/<int:req_problem_id>/submission  ", submit_code, name="callviews Page"),
    #new
    path('create-problem/', create_problem, name='create_problem'),
    path('create-test-case/',create_test_case, name='create_test_case'),
    path('create-combined/', create_problem_with_test_cases, name='create_problem_with_test_cases'),
    path('dashboard/', dashboard, name='dashydashy'),

]
