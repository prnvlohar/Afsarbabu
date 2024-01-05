
from django.db import models

from users.models import CustomUser
from django.core.exceptions import ValidationError
# Create your models here.


class Assessment(models.Model):

    title = models.CharField(max_length=100)
    duration = models.DurationField()

    def __str__(self):
        return self.title


class Question(models.Model):

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    question = models.CharField(max_length=255, null=True)
    option1 = models.CharField(max_length=255, null=True)
    option2 = models.CharField(max_length=255, null=True)
    option3 = models.CharField(max_length=255, null=True)
    option4 = models.CharField(max_length=255, null=True)
    answer = models.CharField(max_length=255, null=True)
    def save(self, *args, **kwargs):
        if Question.objects.count() >= 50:
            raise ValidationError("Cannot add more than 50 instances")
        super(Question, self).save(*args, **kwargs)


class Rating(models.Model):

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    rating = models.IntegerField()

    def __str__(self):
        return f'{self.user} rated {self.rating} star for {self.assessment}'


class PassFailStatus(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    status = models.BooleanField()