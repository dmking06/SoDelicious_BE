from django.shortcuts import render

# Create your views here.
import decimal
import json

import cloudinary.uploader
import environ
import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views import generic

from users.decorators import superuser_only, unauthenticated_user
from comments.models import Comment
from .models import Recipe

env = environ.Env()
environ.Env.read_env()

# Items per page for Recipe Lists
ipp = 8

# Like icon details
liked = "blue"
unliked = "lightgrey"

# Sort icons
icon_up = "fa fa-angle-double-up"
icon_down = "fa fa-angle-double-down"

# For getting average rating
# Recipe.objects.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')


# Landing page
@unauthenticated_user
def landing_page(request):
    return render(request, 'recipes/landing_page.html')


# About Us page
def about_us_view(request):
    return render(request, 'recipes/about_us.html')


# Recipe List - also used for Liked and Edit recipes
class RecipeListView(generic.ListView):
    template_name = 'recipes/recipe_list.html'
    paginate_by = 1
    context_object_name = 'recipe_list'

    def get_queryset(self):
        path = self.request.path
        sort = get_order(self.request)
        recipes = Recipe.objects.order_by(sort)
        return recipes

    def get_context_data(self, **kwargs):
        context = super(RecipeListView, self).get_context_data(**kwargs)
        context['title'] = f"Recipe List"

        context['icon_up'] = icon_up
        context['icon_down'] = icon_down
        return context


# Recipe Detail
class RecipeDetailView(generic.DetailView):
    model = Recipe
    template_name = 'recipes/recipe.html'

    def get_context_data(self, **kwargs):
        context = super(RecipeDetailView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']

        # Comment list, paginated
        comments = Comment.objects.filter(recipe_id=pk)
        paginator = Paginator(comments, ipp)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj

        # Like button
        user = self.request.user
        recipe = Recipe.objects.get(pk=pk)
        if user.is_authenticated and recipe in user.likes.all():
            context['like_color'] = liked
        else:
            context['like_color'] = unliked

        # Stars
        recipe = self.object
        context['recipe'] = recipe
        # Split description into list of lines
        steps = recipe.steps.splitlines()
        context['list_lines'] = steps
        return context


# Recipe Modal pages
def modal_view(request):
    return render(request, 'recipes/recipe_modal.html')


# Like button
def like_button(request):
    if request.method == "POST":
        if request.POST.get("operation") == "like_submit" and request.is_ajax():
            likes_id = request.POST.get("likes_id", None)
            recipe = get_object_or_404(Recipe, pk=likes_id)

            # Check if user already liked recipe
            if recipe in request.user.likes.all():
                # Remove user like from recipe
                recipe.likes.remove(request.user)
                new_color = unliked
            else:
                # Add user like to recipe
                recipe.likes.add(request.user)
                new_color = liked

            # Create new context to feed back to AJAX call
            context = {"likes_count": recipe.likes.count(),
                       "new_color"  : new_color,
                       "likes_id"   : likes_id
                       }
            return HttpResponse(json.dumps(context), content_type='application/json')


# Liked Recipes - must be logged in to access this page
@login_required(login_url="users:login")
def liked_recipes_view(request):
    return RecipeListView.as_view()(request)


# Create star list
def get_stars(rating: decimal) -> list:
    whole_stars, half_stars = rating.as_tuple()[1]
    no_stars = rating.as_tuple()[0]
    stars = []
    if no_stars:
        stars = [0, 0, 0, 0, 0]
    else:
        for x in range(0, whole_stars):
            stars.append(1)
        if half_stars >= 5:
            stars.append(2)
        while len(stars) < 5:
            stars.append(0)
    return stars


# Get page sort
def get_order(request: requests) -> str:
    order_dict = {'dca': 'date_created',
                  'dcd': '-date_created',
                  'nma': 'name',
                  'nmd': '-name',
                  'apa': 'amazon_price',
                  'apd': '-amazon_price',
                  'epa': 'ebay_price',
                  'epd': '-ebay_price',
                  }

    # Get session sort if any
    sort = request.session.get('sort', "")

    # If a new sort was chosen, use that
    if request.GET.get('sort_by') is not None:
        sort = order_dict[request.GET.get('sort_by')]
        request.session['sort'] = sort

    # If sort is still blank, set default
    elif sort == "":
        sort = "-date_created"
        request.session['sort'] = sort

    return sort
