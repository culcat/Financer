
from django.db import models
from django.contrib.auth.models import User





class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now=True)
    description = models.CharField(max_length=100,blank=True)



class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now=True)
    category = models.CharField(max_length=150)
    description = models.CharField(max_length=100 ,blank=True)


