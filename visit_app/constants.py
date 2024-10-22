from django.db import models

class VisitType(models.TextChoices):
    v0 = "Customer_Unavailable", "Customer_Unavailable"
    v1 = "Customer_Busy", "Customer_Busy"
    v2 = "Insufficient_Amount", "Insufficient_Amount"
