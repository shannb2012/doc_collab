from django.urls import path
from . import views


app_name = "texteditor"
urlpatterns = [
    path('', views.index, name="index"),
    path('room/<id>', views.room, name="room"),
    path('documents/', views.Documents.as_view(), name="stuff"),
    path('cursors/', views.Cursors.as_view(), name="cursors"),
]
