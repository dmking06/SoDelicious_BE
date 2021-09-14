from django.contrib.auth import get_user_model
from django.db import models
from recipes.models import Recipe

User = get_user_model()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comment')
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return 'Comment by {} on {}'.format(self.user, self.created_on)
