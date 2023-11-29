import openai
from django.shortcuts import render, redirect
#from django.template import loader
from django.http import JsonResponse

from django.contrib import auth
from django.contrib.auth.models import User
from .models import Chat

from django.utils import timezone

openai_api_key = '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'
openai.api_key = openai_api_key


# def ask_openai(message):
#     response = openai.ChatCompletion.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system", "content": "You are an helpful assistant."},
#             {"role": "user", "content": message},
#         ]
#     )
#     print(response)
   # answer = response.choices[0].message.content.strip()
   # return answer


def ask_openai(message):
    # OpenAI API call logic here
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message},
            ]
        )
        return response.choices[0].message['content']
    except openai.error.OpenAIError as e:
         # Handle API errors here
        return f"An error occurred: {str(e)}"

# Create your views here.
def chatbot(request):
    chats = Chat.objects.filter(user=request.user)

    if request.method == 'POST':
        message = request.POST.get('message')
        response = ask_openai(message)

        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()
        return JsonResponse({'message': message, 'response': response})
    return render(request, 'templates\chatbot.html', {'chats': chats})


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password'
            return render(request, 'templates\login.html', {'error_message': error_message})
    else:
        return render(request, 'templates\login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect('chatbot')
            except:
                error_message = 'Error creating account'
                return render(request, 'templates/register.html', {'error_message': error_message})
        else:
            error_message = 'Password dont match'
            return render(request, 'templates/register.html', {'error_message': error_message})
    return render(request, 'templates/register.html')


def logout(request):
    auth.logout(request)
    return redirect('login')
