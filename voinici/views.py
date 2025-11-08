from django.shortcuts import render

def home(request):
    return render(request, "home.html")

def inclined_plane_view(request):
    return render(request, 'theory/inclined_plane.html')


def collision_view(request):
    return render(request, 'theory/collision.html')


def collision_quiz_view(request):
    # Render the collision quiz page (static/JS-driven quiz)
    return render(request, 'quizes/collision_quiz.html')

def pendulum_quiz_view(request):
    # Render the pendulum quiz page (static/JS-driven quiz)
    return render(request, 'quizes/pendulum_quiz.html')

def pendulum_view(request):
    return render(request, 'theory/pendulum.html')