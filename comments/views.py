from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import generic

from recipes.models import Recipe
from .forms import EditCommentForm
from .models import Comment

# Items per page
ipp = 10


# List all comments of current user
@method_decorator(login_required(login_url="users:login"), name='dispatch')
class MyCommentsView(generic.ListView):
    template_name = 'comments/my_comments.html'
    paginate_by = ipp
    context_object_name = 'comments_list'

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)


# Create a comment
@login_required(login_url="users:login")
def create_comment(request, recipe_id):
    if request.method == 'POST':
        Comment.objects.create(user=request.user,
                               recipe=Recipe.objects.get(pk=recipe_id),
                               body=request.POST['comment_body'],
                               active=True)
    return redirect('recipes:recipe', pk=recipe_id)


# Edit a comment
@login_required(login_url="users:login")
def edit_comment(request, comment_id):
    # Try to get the comment
    comment = get_object_or_404(Comment, pk=comment_id)

    # Check if current user created the comment
    if request.user == comment.user:
        # Create form with comment info
        form = EditCommentForm(instance=comment)

        # Check if request was POST and button was "Update"
        if request.method == 'POST' and 'Update' in request.POST:
            # Create the form using POST data
            form = EditCommentForm(request.POST, instance=comment)

            # Verify form data is valid
            if form.is_valid():
                # Mark the comment as edited and save the edit date
                comment = form.save(commit=False)
                comment.edited = True
                comment.edited_on = timezone.now()
                comment.save()
                messages.success(request, "Updated comment.")
                return redirect('recipes:recipe', pk=comment.recipe.pk)

        # If cancel was clicked, return to previous page
        elif request.method == 'POST' and 'Cancel' in request.POST:
            return redirect('recipes:recipe', pk=comment.recipe.pk)

        # Render the form with any bound data
        context = {'form': form, 'comment': comment}
        return render(request, 'comments/edit_comment.html', context)
    else:
        messages.error(request, f'You are not authorized to perform that action.')
        return redirect('comments:my_comments')


# Delete comment
@login_required(login_url="users:login")
def delete_comment(request, comment_id):
    redirect_url = request.META["HTTP_REFERER"]
    comment = get_object_or_404(Comment, pk=comment_id)

    # Check if current user created the comment
    if request.user == comment.user:
        # Delete comment
        comment.delete()
        return redirect(redirect_url)
    else:
        messages.error(request, f'You are not authorized to perform that action.')
        return redirect(redirect_url)
