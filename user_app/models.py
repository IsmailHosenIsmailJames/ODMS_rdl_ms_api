from django.db import models

class UserList(models.Model):
    id = models.IntegerField(null=False, default=0)
    sap_id = models.IntegerField(null=False,primary_key=True)
    full_name = models.CharField(max_length=255,null=False)
    mobile_number = models.CharField(max_length=255,null=False)
    class UserType(models.TextChoices):
        VALUE0 = 'Delivery Assistant', 'Delivery Assistant'
        VALUE1 = 'Driver', 'Driver'
    user_type = models.CharField(max_length=20,choices=UserType.choices,null=True, blank=True)
    password = models.CharField(max_length=255,null=False)
    class StatusType(models.IntegerChoices):
        V0 = 0, "Inactive"
        V1 = 1, "Active"
    status = models.PositiveSmallIntegerField(choices=StatusType.choices,default=StatusType.V1,null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = "rdl_user_list"
        verbose_name = "RDL User List"
        verbose_name_plural = "RDL User List"

class AdminUserList(models.Model):
    id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=255,null=False,unique=True)
    full_name = models.CharField(max_length=255,null=False)
    mobile_number = models.CharField(max_length=255,null=False)
    password = models.CharField(max_length=255,null=False)
    class StatusType(models.IntegerChoices):
        V0 = 0, "Inactive"
        V1 = 1, "Active"
    status = models.PositiveSmallIntegerField(choices=StatusType.choices,default=StatusType.V1,null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = "rdl_admin_user_list"
        verbose_name = "RDL Admin User List"
        verbose_name_plural = "RDL Admin User List"