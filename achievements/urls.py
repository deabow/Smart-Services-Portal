from __future__ import annotations

from django.urls import path

from .views import (
    achievements_list_view, 
    achievement_update_view, 
    achievement_create_view, 
    get_villages_for_area,
    add_achievement_image,
    delete_achievement_image,
    achievement_images_view
)


app_name = "achievements"

urlpatterns = [
	path("", achievements_list_view, name="list"),
	path("create/", achievement_create_view, name="create"),
	path("<int:pk>/update/", achievement_update_view, name="update"),
	path("<int:pk>/images/", achievement_images_view, name="images"),
	path("api/villages/", get_villages_for_area, name="villages_api"),
	path("api/images/add/<int:pk>/", add_achievement_image, name="add_image"),
	path("api/images/delete/<int:pk>/", delete_achievement_image, name="delete_image"),
]

