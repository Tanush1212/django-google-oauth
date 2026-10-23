import requests
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.shortcuts import render

FACT_URL = "https://uselessfacts.jsph.pl/api/v2/facts/today?language=en"
FACT_CACHE_SECONDS = 60 * 60  # the "fact of the day" only changes daily


def get_fact():
    """Return today's useless fact, calling the API at most once per hour."""
    fact = cache.get("useless_fact")
    if fact is None:
        try:
            response = requests.get(FACT_URL, timeout=5)
            response.raise_for_status()
            fact = response.json()["text"]
            cache.set("useless_fact", fact, FACT_CACHE_SECONDS)
        except (requests.RequestException, KeyError, ValueError):
            fact = None  # the page still works if the API is down
    return fact


def home(request):
    return render(request, "core/home.html", {"fact": get_fact()})


@login_required
def profile(request):
    # allauth stores the user info Google returned in SocialAccount.extra_data.
    google = request.user.socialaccount_set.filter(provider="google").first()
    data = google.extra_data if google else {}
    context = {
        "name": data.get("name") or request.user.get_full_name(),
        "email": data.get("email") or request.user.email,
        "picture": data.get("picture"),
    }
    return render(request, "core/profile.html", context)
