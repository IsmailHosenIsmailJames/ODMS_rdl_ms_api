from django.db import models

class ReportOneModel(models.Model):
    total_delivary = models.TextField(blank=True)
    total_delivary_done = models.TextField(blank=True)
    total_cash = models.TextField(blank=True)
    total_cash_done = models.TextField(blank=True)

    class Meta:
        managed = False
