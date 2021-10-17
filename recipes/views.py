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
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DetailView, ListView

from users.decorators import superuser_only, unauthenticated_user
from users.models import Profile
from comments.models import Comment
from .models import Recipe, Category, Rating

env = environ.Env()
environ.Env.read_env()

# Items per page for Recipe Lists
ipp = 8

# Like icon details
liked = "gold"
unliked = "lightgrey"

# Sort icons
icon_up = "fa fa-angle-double-up"
icon_down = "fa fa-angle-double-down"


# For getting average rating
# Recipe.objects.annotate(avg_rating=Avg('ratings__rating')).order_by('-avg_rating')


# Landing page
def landing_page(request):
    latest_recipes = Recipe.objects.all().order_by('-date_created')[:4]

    for recipe in latest_recipes:
        temp = recipe.album.images.filter(default=True).first()
        if temp is None:
            recipe.image = None
        else:
            recipe.image = temp.image.url
    context = {'latest_recipes': latest_recipes}
    return render(request, 'recipes/landing_page.html', context)


# About Us page
def about_us_view(request):
    return render(request, 'recipes/about_us.html')


# Search bar
class SearchResultsView(ListView):
    model = Recipe
    template_name = 'recipes/search_results.html'
    context_object_name = 'recipe_list'

    def get_queryset(self):
        query = self.request.GET.get('keyword')
        recipe_list = Recipe.objects.filter(
                Q(name__icontains=query) |
                Q(category__name__icontains=query) |
                Q(submitted_by__full_name__icontains=query) |
                Q(description__icontains=query) |
                Q(ingredients__icontains=query)
                ).order_by("name")
        return recipe_list


# Category List
class CategoryListView(ListView):
    template_name = 'recipes/category_list.html'
    paginate_by = ipp
    context_object_name = 'category_list'

    def get_queryset(self):
        path = self.request.path
        categories = Category.objects.order_by("name")
        return categories

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['title'] = f"Category List"

        context['icon_up'] = icon_up
        context['icon_down'] = icon_down
        return context


# Category Detail
class CategoryDetailView(DetailView):
    model = Category
    template_name = 'recipes/category.html'


# Recipe List - also used for Liked and Edit recipes
class RecipeListView(ListView):
    template_name = 'recipes/recipe_list.html'
    paginate_by = ipp
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
class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe.html'

    def get_context_data(self, **kwargs):
        context = super(RecipeDetailView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        recipe = self.object

        # Comment list, paginated
        comments = Comment.objects.filter(recipe_id=pk)
        paginator = Paginator(comments, ipp)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['page_obj'] = page_obj

        # Like button
        user = self.request.user
        context['like_color'] = unliked
        if user.is_authenticated:
            profile = Profile.objects.get(user=user)
            recipe = Recipe.objects.get(pk=pk)
            if recipe in profile.likes.all():
                context['like_color'] = liked

        # Overall Rating
        recipe_rating = Rating.objects.filter(recipe=recipe)
        if recipe_rating:
            overall_rating = decimal.Decimal(recipe.get_avg_rating())
        else:
            overall_rating = decimal.Decimal(0)
        overall_stars = get_stars(overall_rating)
        context['overall_rating'] = overall_stars

        # User Rating
        rating = 0
        if user.is_authenticated:
            user_rating = Rating.objects.filter(profile=profile, recipe=recipe).first()
            if user_rating:
                rating = user_rating.rating

        colors = []
        for x in range(1, 6):
            if x <= rating:
                colors.append('gold')
            else:
                colors.append('lightgrey')

        context['colors'] = colors

        # Split description into list of lines
        ingredients = recipe.ingredients.splitlines()
        context['ingredient_lines'] = ingredients
        steps = recipe.steps.splitlines()
        context['step_lines'] = steps
        return context


# Like button
def like_button(request):
    if request.method == "POST":
        if request.POST.get("operation") == "like_submit" and request.is_ajax():
            likes_id = request.POST.get("likes_id", None)
            recipe = get_object_or_404(Recipe, pk=request.POST.get("recipe_id"))
            profile = Profile.objects.get(user=request.user)

            # Check if user already liked recipe
            if recipe in profile.likes.all():
                # Remove user like from recipe
                recipe.likes.remove(profile)
                new_color = unliked
            else:
                # Add user like to recipe
                recipe.likes.add(profile)
                new_color = liked

            # Create new context to feed back to AJAX call
            context = {"likes_count": recipe.likes.count(),
                       "new_color"  : new_color,
                       "likes_id"   : likes_id
                       }
            return HttpResponse(json.dumps(context), content_type='application/json')


# User rating
def rating_button(request):
    if request.method == "POST":
        if request.POST.get("operation") == "rating_submit" and request.is_ajax():
            ratings_id = request.POST.get("ratings_id", None)
            recipe = get_object_or_404(Recipe, pk=request.POST.get("recipe_pk"))

            # Update/create recipe ranking
            rating, created = Rating.objects.update_or_create(
                    recipe=recipe,
                    profile=Profile.objects.get(user=request.user),
                    )

            rating.rating = int(ratings_id)
            rating.save()

            # Get colors for user rating stars
            colors = []
            for x in range(1, 6):
                if x <= rating.rating:
                    colors.append('gold')
                else:
                    colors.append('lightgrey')

            # Create new context to feed back to AJAX call
            context = {"colors": colors}
            return HttpResponse(json.dumps(context), content_type='application/json')


# Liked Recipes - must be logged in to access this page
@login_required(login_url="users:login")
def liked_recipes_view(request):
    return RecipeListView.as_view()(request)


# Create star list
def get_stars(rating: decimal) -> list:
    stars = []
    nums = rating.as_tuple()[1]
    for x in range(0, nums[0]):
        stars.append(1)
    if len(nums) > 1 and nums[1] >= 5:
        stars.append(2)
    while len(stars) < 5:
        stars.append(0)

    # whole_stars, half_stars = rating.as_tuple()[1]
    # no_stars = rating.as_tuple()[0]
    # stars = []
    # if no_stars:
    #     stars = [0, 0, 0, 0, 0]
    # else:
    #     whole_stars, half_stars = rating.as_tuple()[1]
    #     for x in range(0, whole_stars):
    #         stars.append(1)
    #     if half_stars >= 5:
    #         stars.append(2)
    #     while len(stars) < 5:
    #         stars.append(0)
    return stars


# Get page sort
def get_order(request: requests) -> str:
    order_dict = {'dca': 'date_created',
                  'dcd': '-date_created',
                  'nma': 'name',
                  'nmd': '-name',
                  }

    # Get session sort if any
    sort = request.session.get('sort', "")

    # If a new sort was chosen, use that
    if request.GET.get('sort_by') is not None:
        sort = order_dict[request.GET.get('sort_by')]
        request.session['sort'] = sort

    # If sort is still blank, set default
    elif sort == "":
        sort = "name"
        request.session['sort'] = sort

    return sort
