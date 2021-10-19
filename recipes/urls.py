from django.urls import path

from .views import RecipeDetailView, CategoryDetailView, RecipeListView, CategoryListView, liked_recipes_view, \
    like_button, rating_button, SearchResultsView, highly_rec

app_name = 'recipes'
urlpatterns = [
    # Search
    path('search/', SearchResultsView.as_view(), name='search_results'),

    # Category list
    path('', CategoryListView.as_view(), name='category_list'),

    # Category details
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='category'),

    # Recipe list
    path('list', RecipeListView.as_view(), name='recipe_list'),

    # Recipe details
    path('<int:pk>/', RecipeDetailView.as_view(), name='recipe'),

    # Rating
    path('rating/', rating_button, name='rate'),

    # Likes
    path('like/', like_button, name='like'),
    path('liked_recipes/', liked_recipes_view, name='liked_recipes'),

    # Highly Recommended Recipe
    path('highly_rec', highly_rec, name='highly_rec'),

    # Add and Delete Recipe
    # path('add_recipes/', add_recipe_view, name='add_recipes'),
    # path('edit_recipes/', edit_recipe_view, name='edit_recipes'),
    ]
