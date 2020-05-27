"""guest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path
from sign import views # 导入sign应用的views文件

urlpatterns = [
    path('admin/', admin.site.urls),
    #添加index/路径配置,r表示字符串是非转义的原始字符，^用来匹配文本的开头，$用来匹配文本的结束
    path('index/',views.index),
    url('login_action/$',views.login_action),
    url(r'^event_manage/$',views.event_manage),
    url(r'^$',views.index),
    url(r'^accounts/login/$',views.index),
    url(r'^search_name/$',views.search_name),
    url(r'^guest_manage/$',views.guest_manage),
    url(r'^sign_index/(?P<eid>[0-9]+)/$',views.sign_index),
    url(r'^sign_index_action/(?P<eid>[0-9]+)/$',views.sign_index_action),
    url(r'^logout/$',views.logout),
]
