from django.db import models


class Microdata(models.Model):
    id = models.IntegerField(primary_key=True)
    fanm = models.CharField(max_length=255, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    locl = models.CharField(max_length=255, blank=True, null=True)
    wrkr = models.CharField(max_length=255, blank=True, null=True)
    ennm = models.CharField(max_length=255, blank=True, null=True)
    endv = models.CharField(max_length=255, blank=True, null=True)
    kscd = models.IntegerField(blank=True, null=True)
    ksnm = models.CharField(max_length=255, blank=True, null=True)
    use = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "microdata"
