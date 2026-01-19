from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PatientSignUpForm


def signup_view(request):
    if request.method == "POST":
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Compte créé avec succès. Vous pouvez maintenant vous connecter.")
                return redirect("login")
            except Exception as e:
                messages.error(request, f"Une erreur s'est produite lors de l'inscription : {str(e)}")
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = PatientSignUpForm()
    return render(request, "registration/signup.html", {"form": form})
