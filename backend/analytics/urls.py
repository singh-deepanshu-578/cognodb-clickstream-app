from django.urls import path
from . import views

urlpatterns = [
    path("visitors/", views.list_visitors),
    path("visitors/<str:visitor_id>/", views.visitor_overview),
    path("visitors/<str:visitor_id>/journey/", views.visitor_journey),
    path("visitors/<str:visitor_id>/returning-chains/", views.returning_chains),
    path("insights/common-paths/", views.common_paths),
    path("insights/abandonment-points/", views.abandonment_points),
    path("insights/also-viewed/<str:product_id>/", views.also_viewed),
    path("insights/referrer-conversion/", views.referrer_conversion),
    path("insights/top-pages/", views.top_pages),
]