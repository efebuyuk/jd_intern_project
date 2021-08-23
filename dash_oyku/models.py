from django.db import models
from django.db.models import IntegerField, Model, JSONField



class notebook(models.Model):
    name            = models.CharField(max_length=500)
    cell_count      = models.IntegerField(default=0)
    code_cell_count = models.IntegerField(default=0)
    language        = models.CharField(max_length=6)
    dataset         = JSONField()
    function        = JSONField()
    library         = JSONField()
