from django.db import models


class Person(models.Model):
    # CharField is for short strings; max_length is required
    name = models.CharField(max_length=100)
    
    # IntegerField stores whole numbers
    age = models.IntegerField()
    
    # Storing mobile as CharField is standard for basic needs
    # max_length=15 is generally enough for E.164 international format
    mobile = models.CharField(max_length=15)

    def __str__(self):
        return self.name