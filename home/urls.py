from django.urls import path
from home.views import show_problems
from home.views import load_prblms
from home.views import prblm_detail

urlpatterns = [
    path("problem-old/", show_problems, name="all-problems"),
    path("problems/", load_prblms, name="all-problem-list"),
    path("problems/<int:req_problem_id>/", prblm_detail, name="Problems Page"),

]
