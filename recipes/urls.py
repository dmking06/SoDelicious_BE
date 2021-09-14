from django.urls import path

from .views import RecipeDetailView, RecipeListView, liked_recipes_view, like_button

app_name = 'recipes'
urlpatterns = [
    # Recipe list
    path('', RecipeListView.as_view(), name='recipe_list'),

    # Recipe details & modal
    path('<int:pk>/', RecipeDetailView.as_view(), name='recipe'),

    # Likes
    path('like/', like_button, name='like'),
    path('liked_recipes/', liked_recipes_view, name='liked_recipes'),

    # Add and Delete Recipe
    # path('add_recipes/', add_recipe_view, name='add_recipes'),
    # path('edit_recipes/', edit_recipe_view, name='edit_recipes'),
    ]
