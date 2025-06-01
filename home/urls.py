from django.urls import path
from home.views import load_prblms
from home.views import prblm_detail
from home.views import prblm_page
from home.views import submit_code
from home.views import run_code
from home.views import Profile
from home.views import only_comp

# from home.views import callviews

urlpatterns = [
    path("problems/", load_prblms, name="all-problem-list"),
    path('edit-profile/', Profile, name='users-profile'),
    path('compiler/', only_comp, name='only-compiler'),
    path("problems/<int:req_problem_id>/", prblm_page, name="Compiler Problems Page"),
    path("problems/<int:req_problem_id>/output ",run_code, name="Output-Page"),
    path("problems/<int:req_problem_id>/submission  ", submit_code, name="callviews Page"),

]
