from django import forms


class BookingForm(forms.Form):
    check_in_date = forms.DateField()
    check_out_date = forms.DateField()
    guest_name = forms.CharField(max_length=100)
    

