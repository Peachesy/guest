from django.contrib import admin
from sign.models import Event, Guest

# Register your models here.


class EventAdmin(admin.ModelAdmin):  # 没生效？？因为把admin.site.register(Event,EventAdmin)写成了admin.site.register(Event)
    list_display = ['id', 'name', 'status', 'address', 'start_time']
    search_fields = ['name']  # 增加搜索栏
    list_filter = ['status']  # 增加过滤器


class GuestAdmin(admin.ModelAdmin):     # 没生效？？因为把admin.site.register(Guest,GuestAdmin)写成了admin.site.register(Guest)
    list_display = ['realname', 'phone', 'email', 'sign', 'create_time', 'event']
    search_fields = ['realname','phone']  # 搜索栏
    list_filter = ['sign']  # 过滤器


# 通知admin管理工具为Event和Guest模块提供界面
admin.site.register(Event,EventAdmin)
admin.site.register(Guest,GuestAdmin)

