from django.urls import path
from . import views

urlpatterns = [
    # Event URLs
    path('', views.EventListView.as_view(), name='event-list'),
    path('category/<slug:category_slug>/', views.EventListView.as_view(), name='event-list-by-category'),
    path('dashboard/', views.EventDashboardView.as_view(), name='event-dashboard'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event-detail'),
    path('event/new/', views.EventCreateView.as_view(), name='event-create'),
    path('event/<int:pk>/update/', views.EventUpdateView.as_view(), name='event-update'),
    path('event/<int:pk>/delete/', views.EventDeleteView.as_view(), name='event-delete'),

    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/new/', views.CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),

    # Registration URLs
    path('event/<int:pk>/register/', views.register_for_event, name='event-register'),
    path('event/<int:pk>/unregister/', views.unregister_from_event, name='event-unregister'),
    path('my-registrations/', views.my_registrations, name='my-registrations'),
    path('event/<int:pk>/attendees/', views.event_attendees, name='event-attendees'),
]
