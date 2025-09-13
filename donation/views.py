from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def initiate_payment(request):
    # Lazy import to avoid import-time errors during schema generation
    try:
        from sslcommerz_lib import SSLCOMMERZ
    except Exception:
        return Response({'error': 'Payment gateway unavailable'}, status=503)
    amount = request.data.get('amount')
    donor_name = request.data.get('name')
    donor_email = request.data.get('email')

    if not amount or not donor_name or not donor_email:
        return Response({'error': 'Amount, name, and email are required'}, status=400)

    settings = {
        'store_id': 'hemog68c429fc47f4e',
        'store_pass': 'hemog68c429fc47f4e@ssl',
        'issandbox': True
    }
    sslcz = SSLCOMMERZ(settings)

    post_body = {
        'total_amount': float(amount),
        'currency': "BDT",
        'tran_id': f"donation_{donor_email.replace('@','_')}_{int(float(amount)*100)}",
        'success_url': "https://yourdomain.com/donation/success/",
        'fail_url': "https://yourdomain.com/donation/fail/",
        'cancel_url': "https://yourdomain.com/donation/cancel/",
        'emi_option': 0,
        'cus_name': donor_name,
        'cus_email': donor_email,
        'cus_phone': request.data.get('phone', "01700000000"),
        'cus_add1': request.data.get('address', ""),
        'cus_city': request.data.get('city', "Dhaka"),
        'cus_country': request.data.get('country', "Bangladesh"),
        'shipping_method': "NO",
        'num_of_item': 1,
        'product_name': "Donation",
        'product_category': "Charity",
        'product_profile': "general"
    }

    response = sslcz.createSession(post_body)

    if response.get('GatewayPageURL'):
        return Response({'payment_url': response['GatewayPageURL']})
    else:
        return Response({'error': 'Failed to create payment session', 'details': response}, status=400)


