from typing import KeysView
from django.shortcuts import redirect, render
from django.http import HttpResponse, Http404, JsonResponse
from django.utils.http import  is_safe_url
from django.conf import settings
from .models import Tweet
from .forms import TweetForm
import random

# Create your views here.
def home_view(request, *args, **kwargs):
    return render(request, "pages/home.html", {}, status=200)


def tweet_create_view(request, *args, **kwargs):
    user = request.user
    if not user.is_authenticated:
        user = None
        if request.is_ajax():
            return JsonResponse({}, status=401)
        return redirect(settings.LOGIN_URL)
    form = TweetForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = user
        obj.save()
        if request.is_ajax():
            return JsonResponse(obj.serialize(), status=201)
        if (next_page := request.POST.get("next", None)) != None and is_safe_url(next_page, settings.ALLOWED_HOSTS):
            return redirect(next_page)
        form = TweetForm()
    if form.errors:
        if request.is_ajax():
            return JsonResponse(form.errors, status=400)
    return render(request, "components/form.html", {"form": form})


def list_view(request, *args, **kwargs):
    all_tweets = Tweet.objects.all()
    tweets_as_dict = [x.serialize() for x in all_tweets]
    data = {"isUser": False, "response": tweets_as_dict}
    return JsonResponse(data)

def detailed_view(request, tweet, *args, **kwargs):
    data = {"id": tweet}
    status = 200
    try:
        data["content"] = Tweet.objects.get(id=tweet).content
    except:
        status = 404
        data["message"] = "Not found"
    return JsonResponse(data, status=status)