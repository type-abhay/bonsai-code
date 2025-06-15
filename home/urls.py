from django.urls import path
from home.views import load_prblms
from home.views import prblm_detail
from home.views import prblm_page
from home.views import submit_code
from home.views import run_code
from home.views import Profile
from home.views import only_comp
from home.views import create_problem_with_test_cases, create_problem,create_test_case, dashboard, diff_probs, home, search_results, ChangePasswordView
# from home.views import callviews

urlpatterns = [
    path("problems/", load_prblms, name="all-problem-list"),
    path('edit-profile/', Profile, name='users-profile'),
    path('compiler/', only_comp, name='only-compiler'),
    path("problems/<int:req_problem_id>/", prblm_page, name="Compiler Problems Page"),
    path("problems/<int:req_problem_id>/output ",run_code, name="Output-Page"),
    path("problems/<int:req_problem_id>/submission  ", submit_code, name="Submission-Page"),
    #new
    path('create-problem/', create_problem, name='create_problem'),
    path('create-test-case/',create_test_case, name='create_test_case'),
    path('create-combined/', create_problem_with_test_cases, name='create_problem_with_test_cases'),
    path('dashboard/', dashboard, name='dashydashy'),
    path('problems/difficulty/<str:difficulty>/', diff_probs, name='difficulty_problems'),
    path('', home, name='home'),
    path('search/',search_results, name='search_results'),
    path('password-change/', ChangePasswordView.as_view(), name='password_change'),

]
