from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import User as AuthUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Room,CustomUser,Booking
from django.views import View
from django.shortcuts import render,redirect
from .serializers import RoomSerializer, CustomUserSerializer
from rest_framework.authtoken.models import Token
from .forms import BookingForm
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.http import JsonResponse,HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
import razorpay
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.urls import reverse
class HomePageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home.html')

class ViewRoomsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        rooms = Room.objects.all()
        serializer = RoomSerializer(rooms, many=True)
        return render(request, 'view_rooms.html', {'rooms': serializer.data})
        #return Response(serializer.data, status=status.HTTP_200_OK)

def book_room(request, room_id):
    template_name = 'book_room.html'
    room = get_object_or_404(Room, pk=room_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in_date = form.cleaned_data['check_in_date']
            check_out_date = form.cleaned_data['check_out_date']
            guest_name = form.cleaned_data['guest_name']
            user = get_object_or_404(CustomUser, name=guest_name)
            total_amount = room.price * (check_out_date - check_in_date).days
           
            client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
            razorpay_order = client.order.create({
                'amount': int(total_amount * 100),  # Amount in paise
                'currency': 'INR',
                'payment_capture': '1'  # Auto capture payment
            })
            booking = Booking.objects.create(
                room=room,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                guest_name=guest_name,
                user=user,
                total_amount=total_amount,
                razorpay_order_id=razorpay_order['id']  # Store Razorpay order ID
            )
            room.is_available = False
            room.save()
            return render(request,"payment.html",
            {
                #"callback_url": "http://" + "127.0.0.1:8000" + "/razorpay/callback/",
                "razorpay_key": settings.RAZOR_KEY_ID,
                "booking": booking,
            },)
    else:
        form = BookingForm()
    
    return render(request, template_name, {'room': room, 'form': form})

@csrf_exempt
def payment_success_view(request):
   order_id = request.POST.get('order_id')
   payment_id = request.POST.get('razorpay_payment_id')
   signature = request.POST.get('razorpay_signature')
   params_dict = {
       'razorpay_order_id': order_id,
       'razorpay_payment_id': payment_id,
       'razorpay_signature': signature
   }
   try:
       client.utility.verify_payment_signature(params_dict)
       # Payment signature verification successful
       # Perform any required actions (e.g., update the order status)
       return HttpResponse("Your Payment Was Successful")
   except razorpay.errors.SignatureVerificationError as e:
       # Payment signature verification failed
       # Handle the error accordingly
       return render(request, 'payment_failure.html')

#if request.user.is_authenticated:
#else:return redirect('login')
class LoginUser(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            token = Token.objects.get(user=user)

            return Response({
                'token': token.key,
                'email': email,
                'verified' : user.is_verified,
                'message': 'User logged in successfully'
            })
        else:
            return Response({'message': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# Registering new user
class SignupUser(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.objects.get(user=user)
            email_send(user.email, token)
            return Response({'message': 'User Registered Successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def email_send(email, token):
    subject = 'Your account needs to be verified'
    message = f'Click on the link to verify your account http://127.0.0.1:8000/verification/{token}'
    email_from = 'jason2004bourne@gmail.com'
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)


# Verifying the email
def email_verification(request, token):
    user_token = get_object_or_404(Token, key=token)
    user = user_token.user
    if not user.is_verified:
        user.is_verified = True
        user.save()
        return JsonResponse({'message': 'verified'})
    return JsonResponse({'message': 'User already verified'})


            