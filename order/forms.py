from django import forms

from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name','last_name','phone','email','address_line_1', 'address_line_2', 'country', 'state','city', 'notes']

    def __init__(self, *args, **kargs):
        super(OrderForm, self).__init__(*args, **kargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'