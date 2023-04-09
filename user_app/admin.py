from django.contrib import admin
from .models import UserList

# Register your models here.


class UserListModel (admin.ModelAdmin):
    list_display=('sap_id','full_name','mobile_number','user_type')
    readonly_fields=('created_at','updated_at')
    search_fields = ('sap_id','full_name')
admin.site.register(UserList,UserListModel)