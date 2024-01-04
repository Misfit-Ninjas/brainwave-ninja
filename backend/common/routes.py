from .views import BrainViewSet, RestViewSet


routes = [
    {"regex": r"rest", "viewset": RestViewSet, "basename": "Rest"},
    {"regex": r"brain/(?P<guid>[0-9a-f-]{36})", "viewset": BrainViewSet, "basename": "Brain"},
]
