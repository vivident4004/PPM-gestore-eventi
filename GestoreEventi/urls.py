from django.urls import path
from . import views

urlpatterns = [
    # Event URLs
    path('', views.EventListView.as_view(), name='event-list'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('event/new/', views.EventCreateView.as_view(), name='event-create'),
    path('event/<int:pk>/update/', views.EventUpdateView.as_view(), name='event-update'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event-delete'),
    
    # Registration URLs
    path('event/<int:pk>/register/', views.register_for_event, name='event-register'),
    path('event/<int:pk>/unregister/', views.unregister_from_event, name='event-unregister'),
    path('my-registrations/', views.my_registrations, name='my-registrations'),
    path('event/<int:pk>/attendees/', views.event_attendees, name='event-attendees'),
]