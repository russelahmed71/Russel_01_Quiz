import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Quiz, Question, Option, Participant, Moderator
from .forms import RegistrationForm, ParticipantForm, ModeratorForm, QuizForm

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        role = request.POST.get('role')
        
        if form.is_valid():
            if role == 'participant':
                p_form = ParticipantForm(request.POST)
                if p_form.is_valid():
                    user = form.save(commit=False)
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                    
                    profile = p_form.save(commit=False)
                    profile.user = user
                    profile.save()
                    
                    login(request, user)
                    return redirect('dashboard')
            
            elif role == 'moderator':
                m_form = ModeratorForm(request.POST)
                if m_form.is_valid():
                    user = form.save(commit=False)
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                    
                    profile = m_form.save(commit=False)
                    profile.user = user
                    profile.save()
                    
                    login(request, user)
                    return redirect('dashboard')
    
    form = RegistrationForm()
    p_form = ParticipantForm()
    m_form = ModeratorForm()
    return render(request, 'register.html', {'form': form, 'p_form': p_form, 'm_form': m_form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    quizzes = Quiz.objects.all()
    participant = Participant.objects.filter(user=request.user).first()
    moderator = Moderator.objects.filter(user=request.user).first()
    is_mod = False
    position = None

    if request.user.is_superuser:
        is_mod = True
        if not moderator:
            moderator = Moderator.objects.create(user=request.user, name="Superuser Admin")
    elif moderator:
        is_mod = True

    if participant:
        all_participants = Participant.objects.order_by('-score')
        rank = 1
        for p in all_participants:
            if p.id == participant.id:
                position = rank
                break
            rank = rank + 1

    return render(request, 'dashboard.html', {
        'quizzes': quizzes,
        'participant': participant,
        'moderator': moderator,
        'position': position,
        'is_mod': is_mod
    })

@login_required
def take_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    
    if request.method == 'POST':
        score = 0
        questions = quiz.questions.all()
        
        for q in questions:
            button_name = 'question_' + str(q.id)
            selected_option_id = request.POST.get(button_name)
            
            if selected_option_id:
                chosen_option = Option.objects.get(id=selected_option_id)
                if chosen_option.is_correct == True:
                    score = score + 10
        
        participant = Participant.objects.get(user=request.user)
        participant.score = participant.score + score
        participant.save()
        return redirect('dashboard')

    questions = list(quiz.questions.all())
    random.shuffle(questions)
    
    quiz_data = []
    for q in questions:
        options = list(q.options.all())
        random.shuffle(options)
        quiz_data.append({'question': q, 'options': options})

    return render(request, 'take_quiz.html', {'quiz': quiz, 'quiz_data': quiz_data})

@login_required
def add_quiz(request):
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.created_by = Moderator.objects.get(user=request.user)
            quiz.save()
            return redirect('dashboard')
    else:
        form = QuizForm()
        
    return render(request, 'quiz_form.html', {'form': form, 'title': 'Add Quiz'})

@login_required
def edit_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = QuizForm(instance=quiz)
        
    return render(request, 'quiz_form.html', {'form': form, 'title': 'Edit Quiz'})

@login_required
def delete_quiz(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    
    if request.method == 'POST':
        quiz.delete()
        return redirect('dashboard')
        
    return render(request, 'quiz_confirm_delete.html', {'quiz': quiz})

@login_required
def add_question(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    
    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        option1 = request.POST.get('option1')
        option2 = request.POST.get('option2')
        option3 = request.POST.get('option3')
        option4 = request.POST.get('option4')
        correct_option = request.POST.get('correct_option')

        question = Question.objects.create(quiz=quiz, question_text=question_text)

        if option1 != "":
            Option.objects.create(question=question, option_text=option1, is_correct=(correct_option == "1"))

        if option2 != "":
            Option.objects.create(question=question, option_text=option2, is_correct=(correct_option == "2"))

        if option3 != "":
            Option.objects.create(question=question, option_text=option3, is_correct=(correct_option == "3"))

        if option4 != "":
            Option.objects.create(question=question, option_text=option4, is_correct=(correct_option == "4"))

        return redirect('dashboard')

    return render(request, 'add_question.html', {'quiz': quiz})
