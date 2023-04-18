from django.contrib import admin
from .models import UserList, AdminUserList

class UserListModel (admin.ModelAdmin):
    list_display=('sap_id','full_name','mobile_number','user_type','status')
    readonly_fields=('created_at','updated_at')
    search_fields = ('sap_id','full_name')
admin.site.register(UserList,UserListModel)

class AdminUserListModel (admin.ModelAdmin):
    list_display=('user_name','full_name','mobile_number','status')
    readonly_fields=('created_at','updated_at')
    search_fields = ('user_name','full_name')
admin.site.register(AdminUserList,AdminUserListModel)