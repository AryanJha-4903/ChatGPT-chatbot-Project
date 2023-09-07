from django.shortcuts import render,redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
from .models import chat
from django.utils import timezone
import openai
from tenacity import (
      retry,
      stop_after_attempt,
      wait_random_exponential,   )  
openai_api_key='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'
openai.api_key=openai_api_key
@retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(6))

def ask_openai(message):
   response = openai.ChatCompletion.create(
      model='gpt-3.5-turbo',
      messages=[
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": message},
   ]
   )
   answer = response.choice[0].message.content.strip()
   return answer
 #Create your views here.
def chatbot(request):
   chats=chat.objects.filter(user=request.user)
   if request.method == 'POST':
      message=request.POST.get('message')
      response=ask_openai(message)
      Chat=chat(user=request.user,message=message,response=response,created_at=timezone.now())
      Chat.save()
      return JsonResponse({'message':message,'response':response})
   return render(request, 'chatbot.html',{'chats':chats})


def login(request):
   if request.method=='POST':
      username=request.POST['username']
      password=request.POST['password']
      user=auth.authenticate(request,username=username,password=password)
      if user is not None:
         auth.login(request, user)
         return redirect('chatbot')
      else:
         error_message='Invalid Username or Password'
         return render(request,'login.html',{'error_message': error_message})
   else:
      return render(request,'login.html')
def register(request):
   if request.method=='POST':
      username=request.POST['username']
      email=request.POST['email']
      password1=request.POST['password1']
      password2=request.POST['password2']
      if password1==password2:
         try:
            user=User.objects.create_user(username,email,password1)
            user.save()
            auth.login(request,user)
            return redirect('chatbot')
         except:
            error_message='Error while creating an account'
            return render(request,'register.html',{'error_message': error_message})
      else: 
         error_message='invalid password'
         return render(request,'register.html',{'error_message': error_message})
   return render(request,'register.html')

def logout(request):
   auth.logout(request)
   return redirect('login')