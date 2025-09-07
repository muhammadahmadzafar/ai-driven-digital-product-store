from django.urls import path # type: ignore
from .views import chatbot_response

urlpatterns = [
    path("chatbot/", chatbot_response, name="chatbot"),
]
