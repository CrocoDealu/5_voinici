from django.shortcuts import render

def home(request):
    return render(request, "home.html")

def inclined_plane_view(request):
    return render(request, 'theory/inclined_plane.html')


def collision_view(request):
    return render(request, 'theory/collision.html')

def quiz_view(request):
    quiz_file = request.GET.get('quiz', 'collision_quiz.json')  # default quiz file
    context = {
        "quiz_file": quiz_file
    }
    return render(request, 'quizes/quiz_page.html', context)

def pendulum_view(request):
    return render(request, 'theory/pendulum.html')