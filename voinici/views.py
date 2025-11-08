from django.shortcuts import render

def home(request):
    return render(request, "home.html")

def inclined_plane_view(request):
    return render(request, 'theory/inclined_plane.html')


def collision_view(request):
    return render(request, 'theory/collision.html')

def pendulum_view(request):
    return render(request, 'theory/pendulum.html')