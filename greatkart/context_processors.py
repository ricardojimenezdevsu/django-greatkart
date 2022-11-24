from decouple import config

def paypal_client_id(request):
    client_id = config('PAYPAL_CLIENTID',default='sb')
    return dict(paypal_clientId = client_id)