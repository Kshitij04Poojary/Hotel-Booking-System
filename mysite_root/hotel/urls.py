from django.urls import path
#from . import views
from .views import *

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('view-rooms/', ViewRoomsView.as_view(), name='view-rooms'),
    path('book-room/<int:room_id>/', book_room, name='book_room'),
    path('payment/success/', payment_success_view, name='payment_success'),
    #path('book-room/<int:room_id>/', BookRoomView.as_view(), name='book-room'),
    path('signup/', SignupUser.as_view(), name='user_signup'),
    #path('login/', LoginUser.as_view(), name='user_login'),
    #path('receptionist/register/', ReceptionistRegistrationView.as_view(), name='receptionist-register'),
    #path('receptionist/login/', ReceptionistLoginView.as_view(), name='receptionist-login'),
    path('verification/<str:token>', email_verification, name='email_verification')
]