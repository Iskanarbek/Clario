from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from .models import (
    DifficultyLevel, Term, RuleTheory, Problem, 
    TestQuestion, UserProgress
)
import random

def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    user_count = User.objects.count()
    
    return render(request, 'myapp/index.html', {"user_count": user_count})



def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            return render(request, 'myapp/register.html', {'error': 'Username already exists'})
        
        # Create user
        user = User.objects.create_user(username=username, password=password)
        
        # Authenticate user immediately after creation
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # logs in user and sets session properly

            # Initialize UserProgress
            level_1, created = DifficultyLevel.objects.get_or_create(level=1)
            UserProgress.objects.get_or_create(user=user, defaults={'current_level': level_1})
            
            return redirect('dashboard')
        else:
            return render(request, 'myapp/register.html', {'error': 'Authentication failed. Try again.'})
    
    return render(request, 'myapp/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'myapp/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'myapp/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def dashboard(request):
    user_progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        defaults={'current_level': DifficultyLevel.objects.get_or_create(level=1)[0]}
    )

    has_started_learning = (
        user_progress.placement_test_taken or
        user_progress.terms_studied.exists() or
        user_progress.rules_studied.exists() or
        user_progress.problems_solved.exists()
    )

    return render(request, "myapp/dashboard.html", {
        "user_progress": user_progress,
        "has_started_learning": has_started_learning
    })


@login_required
def start_from_zero(request):
    try:
        user_progress = UserProgress.objects.get(user=request.user)
    except UserProgress.DoesNotExist:
        # Create user progress if it doesn't exist
        level_1, created = DifficultyLevel.objects.get_or_create(level=1)
        user_progress = UserProgress.objects.create(user=request.user, current_level=level_1)
        
    
    level_1, created = DifficultyLevel.objects.get_or_create(level=1)
    user_progress.current_level = level_1
    user_progress.placement_test_taken = False
    user_progress.placement_test_score = 0
    user_progress.save()
    
    return redirect('learning_content')

@login_required
def learning_content(request):
    try:
        user_progress = UserProgress.objects.get(user=request.user)
    except UserProgress.DoesNotExist:
        # Create user progress if it doesn't exist
        level_1, created = DifficultyLevel.objects.get_or_create(level=1)
        user_progress = UserProgress.objects.create(user=request.user, current_level=level_1)
    
    current_level = user_progress.current_level
    
    # Get content based on progression logic
    terms_studied_count = user_progress.terms_studied.count()
    rules_studied_count = user_progress.rules_studied.count()
    
    # Determine what to show next based on progression logic
    if terms_studied_count % 5 == 0 and terms_studied_count > 0 and rules_studied_count < (terms_studied_count // 5):
        # Show a rule/theory after every 5 terms
        content_type = 'rule'
        content = RuleTheory.objects.filter(difficulty=current_level).exclude(
            id__in=user_progress.rules_studied.all()
        ).first()
    elif (terms_studied_count % 10 == 0 and terms_studied_count > 0 and 
          rules_studied_count % 2 == 0 and rules_studied_count > 0):
        # Show a problem after every 10 terms and 2 rules
        content_type = 'problem'
        content = Problem.objects.filter(difficulty=current_level).exclude(
            id__in=user_progress.problems_solved.all()
        ).first()
    else:
        # Show a term by default
        content_type = 'term'
        content = Term.objects.filter(difficulty=current_level).exclude(
            id__in=user_progress.terms_studied.all()
        ).first()
    
    # If no content of the determined type, try other types
    if not content:
        if content_type == 'term':
            content = RuleTheory.objects.filter(difficulty=current_level).exclude(
                id__in=user_progress.rules_studied.all()
            ).first()
            content_type = 'rule' if content else None
        
        if not content:
            content = Problem.objects.filter(difficulty=current_level).exclude(
                id__in=user_progress.problems_solved.all()
            ).first()
            content_type = 'problem' if content else None
    
    # If still no content, check if user can progress to next level
    if not content:
        next_level_num = current_level.level + 1
        if next_level_num <= 5:
            next_level, created = DifficultyLevel.objects.get_or_create(level=next_level_num)
            user_progress.current_level = next_level
            user_progress.save()
            return redirect('learning_content')
    
    if not content:
        return render(request, 'myapp/learning_content.html', {
            'no_content': True,
            'user_progress': user_progress
        })
    
    if content_type == 'term':
        template = 'myapp/term_detail.html'
    elif content_type == 'rule':
        template = 'myapp/rule_detail.html'
    else:
        template = 'myapp/problem_detail.html'
    
    return render(request, template, {
        'content': content,
        'content_type': content_type,
        'user_progress': user_progress
    })

@login_required
def mark_term_studied(request, term_id):
    try:
        user_progress = UserProgress.objects.get(user=request.user)
    except UserProgress.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User progress not found'})
    
    if request.method == 'POST':
        term = get_object_or_404(Term, id=term_id)
        user_progress.terms_studied.add(term)
        user_progress.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def mark_rule_studied(request, rule_id):
    try:
        user_progress = UserProgress.objects.get(user=request.user)
    except UserProgress.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User progress not found'})
    
    if request.method == 'POST':
        rule = get_object_or_404(RuleTheory, id=rule_id)
        user_progress.rules_studied.add(rule)
        user_progress.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

@login_required
def check_problem_answer(request, problem_id):
    try:
        user_progress = UserProgress.objects.get(user=request.user)
    except UserProgress.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User progress not found'})
    
    if request.method == 'POST':
        problem = get_object_or_404(Problem, id=problem_id)
        user_answer = request.POST.get('answer', '').upper()
        
        is_correct = user_answer == problem.correct_answer
        
        if is_correct:
            user_progress.problems_solved.add(problem)
            user_progress.save()
        
        return JsonResponse({
            'status': 'success',
            'is_correct': is_correct,
            'correct_answer': problem.correct_answer,
            'explanation': problem.explanation
        })
    return JsonResponse({'status': 'error'})


@login_required
def placement_test(request):
    try:
        user_progress = UserProgress.objects.get(user=request.user)
    except UserProgress.DoesNotExist:
        # Create user progress if it doesn't exist
        level_1, created = DifficultyLevel.objects.get_or_create(level=1)
        user_progress = UserProgress.objects.create(user=request.user, current_level=level_1)
    
    if request.method == 'POST':
        # Calculate score
        questions = TestQuestion.objects.all()
        total_questions = questions.count()
        
        if total_questions == 0:
            return redirect('dashboard')
        
        correct_answers = 0
        for question in questions:
            answer_key = f'question_{question.id}'
            user_answer = request.POST.get(answer_key, '').upper()
            
            if user_answer == question.correct_answer:
                correct_answers += 1
        
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Determine level based on score with proper ranges
        if score < 20:
            level_num = 1
        elif score < 40:
            level_num = 2
        elif score < 60:
            level_num = 3
        elif score < 80:
            level_num = 4
        else:
            level_num = 5  # Only 80-100% gets level 5
        
        # Update user progress
        level, created = DifficultyLevel.objects.get_or_create(level=level_num)
        user_progress.current_level = level
        user_progress.placement_test_taken = True
        user_progress.placement_test_score = score
        user_progress.save()
        
        return redirect('learning_content')
    
    # Get all test questions
    questions = TestQuestion.objects.all()
    if not questions.exists():
        return render(request, 'myapp/placement_test.html', {
            'error': 'No test questions available. Please contact administrator.'
        })
    
    return render(request, 'myapp/placement_test.html', {
        'questions': questions
    })
    
    
@login_required
def placement_test(request):
    try:
        user_progress = UserProgress.objects.get(user=request.user)
    except UserProgress.DoesNotExist:
        # Create user progress if it doesn't exist
        level_1, created = DifficultyLevel.objects.get_or_create(level=1)
        user_progress = UserProgress.objects.create(user=request.user, current_level=level_1)
    
    if request.method == 'POST':
        # Calculate score
        questions = TestQuestion.objects.all()
        total_questions = questions.count()
        
        if total_questions == 0:
            return redirect('dashboard')
        
        correct_answers = 0
        for question in questions:
            answer_key = f'question_{question.id}'
            user_answer = request.POST.get(answer_key, '').upper()
            
            if user_answer == question.correct_answer:
                correct_answers += 1
        
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Determine level based on score with proper ranges
        if score < 20:
            level_num = 1
        elif score < 40:
            level_num = 2
        elif score < 60:
            level_num = 3
        elif score < 80:
            level_num = 4
        else:
            level_num = 5  # Only 80-100% gets level 5
        
        # Update user progress
        level, created = DifficultyLevel.objects.get_or_create(level=level_num)
        user_progress.current_level = level
        user_progress.placement_test_taken = True
        user_progress.placement_test_score = score
        user_progress.save()
        
        # Show results page instead of redirecting immediately
        return render(request, 'myapp/test_results.html', {
            'score': score,
            'level': level,
            'correct': correct_answers,
            'total': total_questions
        })
    
    # Get all test questions
    questions = TestQuestion.objects.all()
    if not questions.exists():
        return render(request, 'myapp/placement_test.html', {
            'error': 'No test questions available. Please contact administrator.'
        })
    
    return render(request, 'myapp/placement_test.html', {
        'questions': questions
    })





def search(request):

    terms = Term.objects.all()
    rules = RuleTheory.objects.all()

    return render(request, "myapp/search.html", {

        "terms": terms,
        "rules": rules
    })



from django.contrib.auth.models import User

def base_context(request):
    return {
        "user_count": User.objects.count()
    }
