from django.db import models


class Model(models.Model):
    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f'{self._meta.model_name} - {self.id} - {self.name}'


class Parent(Model):
    name = models.CharField(max_length=10)


class Child(Model):
    parent = models.ForeignKey(
        Parent, on_delete=models.CASCADE, related_name='children',
    )
    name = models.CharField(max_length=10)


class Grandson(Model):
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name='grandchildren',
    )
    name = models.CharField(max_length=10)
