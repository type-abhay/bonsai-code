from django.shortcuts import render,redirect
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib import messages
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
# Create your views here.

def register_user(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.filter(username=username)

        if user.exists():
            messages.error(request,'User with this username already exists')
            return redirect("/accounts/register/")
        
        user = User.objects.create_user(username=username)

        user.set_password(password)

        user.save()
        
        messages.success(request, 'User created successfully, Please Login Below!')
        return redirect('/accounts/login/')
    
    template = loader.get_template('register.html')
    context = {}
    return HttpResponse(template.render(context,request))
    
    

def login_user(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request,'User with this username does not exist')
            return redirect('/accounts/login/')
        
        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request,'invalid password')
            return redirect('/accounts/login')
        

        login(request,user)

        return redirect('/home/problems/')
    
    template = loader.get_template('login.html')
    context ={}
    return HttpResponse(template.render(context,request))

def logout_user(request):
    logout(request)
    messages.success(request,'logout successful')
    return redirect('/accounts/login/')