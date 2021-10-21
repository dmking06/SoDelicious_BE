# Create your views here.
import decimal
import json
import random
import re

import environ
import requests
# from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import EmailValidator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DetailView, ListView

from comments.models import Comment
from recipes.forms import SubscribeForm
from users.models import Profile
from .models import Recipe, Category, Rating, Subscribed

env = environ.Env()
environ.Env.read_env()

# Items per page for Recipe Lists
ipp = 10

# Like icon details
liked = "gold"
unliked = "lightgrey"

# Sort icons
icon_up = "fa fa-angle-double-up"
icon_down = "fa fa-angle-double-down"

# Site title
title = "So Delicious"

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
    context = {'item_list': latest_recipes,
               'title': "SoDelicious - Ethnic-Inspired Recipes",
               'header': "Latest Recipes",
               'type': 'recipe',
               }
    return render(request, 'recipes/general_list.html', context)


# About Us page
def about_us_view(request):
    return render(request, 'recipes/about_us.html')


# Contact Us page
def contact_us_view(request):
    return render(request, 'recipes/contact_us.html')


# Search bar
class SearchResultsView(ListView):
    paginate_by = ipp
    template_name = 'recipes/general_list.html'
    context_object_name = 'item_list'

    def get_queryset(self):
        query = self.request.GET.get('keyword')
        recipe_list = Recipe.objects.filter(
                Q(name__icontains=query) |
                Q(category__name__icontains=query) |
                Q(submitted_by__full_name__icontains=query) |
                Q(description__icontains=query) |
                Q(ingredients__icontains=query)
                ).order_by("name")

        # Get image for recipes
        for recipe in recipe_list:
            temp = recipe.album.images.filter(default=True).first()
            if temp is None:
                recipe.image = None
            else:
                recipe.image = temp.image.url
        return recipe_list

    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        context['title'] = f"Search Results - {title}"
        context['header'] = f"Search Results for \"{self.request.GET.get('keyword')}\""
        context['type'] = "recipe"
        context['icon_up'] = icon_up
        context['icon_down'] = icon_down
        return context


# Category List
class CategoryListView(ListView):
    template_name = 'recipes/general_list.html'
    paginate_by = ipp
    context_object_name = 'item_list'

    def get_queryset(self):
        path = self.request.path
        categories = Category.objects.order_by("name")

        # Get image from first recipe in category
        for category in categories:
            recipe = Recipe.objects.filter(category=category).first()
            if recipe is not None:
                temp = recipe.album.images.filter(default=True).first()
                if temp is None:
                    category.image = None
                else:
                    category.image = temp.image.url
            else:
                category.image = temp.image.url
        return categories

    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        context['title'] = f"Recipe Categories - {title}"
        context['header'] = f"Recipe Categories"
        context['type'] = "category"
        context['icon_up'] = icon_up
        context['icon_down'] = icon_down
        return context


# Category Detail
class CategoryDetailView(DetailView):
    model = Category
    paginate_by = ipp
    template_name = 'recipes/general_list.html'

    def get_context_data(self, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        category = self.object

        recipes = []
        for recipe in category.recipe_set.all():
            # Get image for recipe
            temp = recipe.album.images.filter(default=True).first()
            if temp is None:
                recipe.image = None
            else:
                recipe.image = temp.image.url
            recipes.append(recipe)

        context['item_list'] = recipes
        context['title'] = f"{category} Recipes - {title}"
        context['header'] = f"{category} Recipes"
        context['type'] = "recipe"
        context['icon_up'] = icon_up
        context['icon_down'] = icon_down
        return context


# Recipe List - also used for Liked and Edit recipes
class RecipeListView(ListView):
    template_name = 'recipes/general_list.html'
    paginate_by = ipp
    context_object_name = 'item_list'

    def get_queryset(self):
        path = self.request.path
        sort = get_order(self.request)
        recipes = Recipe.objects.order_by(sort)

        # Get image for recipe
        for recipe in recipes:
            temp = recipe.album.images.filter(default=True).first()
            if temp is None:
                recipe.image = None
            else:
                recipe.image = temp.image.url
        return recipes

    def get_context_data(self, **kwargs):
        context = super(RecipeListView, self).get_context_data(**kwargs)
        context['title'] = f"Recipes - {title}"
        context['header'] = f"Recipes"
        context['type'] = "recipe"
        context['icon_up'] = icon_up
        context['icon_down'] = icon_down
        return context


# Recipe Detail
class RecipeDetailView(DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'

    def get_context_data(self, **kwargs):
        context = super(RecipeDetailView, self).get_context_data(**kwargs)
        pk = self.kwargs['pk']
        recipe = self.object

        # Get image
        temp = recipe.album.images.filter(default=True).first()
        if temp is None:
            recipe.image = None
        else:
            recipe.image = temp.image.url
            context['recipe_image'] = recipe.image

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
        update_avg_rating(recipe)
        overall_rating = recipe.average_rating
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

        # Split ingredients into list of lines
        ingredients = recipe.ingredients.splitlines()
        context['ingredient_lines'] = ingredients

        # Bold ingredients in steps
        for x in ingredients:
            recipe.steps = re.sub(re.escape(x), f"<b>{x}</b>", recipe.steps)

        # Split steps into list of lines
        steps = recipe.steps.splitlines()
        context['step_lines'] = steps
        return context


# Recipe Detail
def highly_rec(request):
    # # Get all recipes with average rating >= 4.0
    # recipes = list(Recipe.objects.filter(average_rating__gte=4.0))
    #
    # # Select random recipe
    # random_recipe = random.choice(recipes)

    recipe = Recipe.objects.filter(average_rating__gte=4.0).first()

    # Get image
    temp = recipe.album.images.filter(default=True).first()
    if temp is None:
        recipe.image = None
    else:
        recipe.image = temp.image.url

    context = {'recipe': recipe,
               'recipe_image': recipe.image}
    return render(request, 'recipes/highly_rec.html', context)


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


# Subscribe page
def subscribe_view(request):
    form = SubscribeForm

    # Check if request was POST
    if request.method == 'POST':
        form = SubscribeForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
        else:
            email = request.POST.get('email-sub')

        try:
            EmailValidator()(email)
            valid = True
        except ValidationError:
            valid = False

        if valid:
            # Save subscription
            (sub, new) = Subscribed.objects.get_or_create(email=email)
            context = {
                'subscription': sub,
                'new': new,
                }

            # Search profiles for email and mark as subscribed
            profile = Profile.objects.filter(user__email=email).first()
            if profile is not None:
                profile.subscribed = True
                profile.save()

            return render(request, 'recipes/subscribe_results.html', context)

    # Render page with any bound data and error messages
    context = {'form': form}
    return render(request, 'recipes/subscribe.html', context)


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

            # Update recipe average rating
            update_avg_rating(recipe)

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


# Update average rating
def update_avg_rating(recipe: Recipe):
    recipe_rating = Rating.objects.filter(recipe=recipe)
    if recipe_rating:
        overall_rating = decimal.Decimal(recipe.get_avg_rating())
    else:
        overall_rating = decimal.Decimal(0)

    recipe.average_rating = overall_rating
    recipe.save()


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
