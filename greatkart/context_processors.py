import environ
env = environ.Env()
environ.Env.read_env()

def paypal_client_id(request):
    client_id = env('PAYPAL_CLIENTID') if env('PAYPAL_CLIENTID') else 'sb'
    return dict(paypal_clientId = client_id)