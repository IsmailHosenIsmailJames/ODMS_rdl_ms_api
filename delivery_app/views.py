from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

@api_view(['GET'])
def delivery_list(request,sap_id):
    if request.method == 'GET':
        d_type = request.query_params.get("type")
        return Response({"success": True, "result": [
            {
                'id': 1,
                'invoice_date': '2023-04-11',
                'customer_name': 'Hazi Liakot Ali Pharmacy',
                'customer_addreess': 'Khejurbag (Near Pargandiara Bazar)',
                'customer_mobile': '0171716732',
                'delevery_type': 'Car',
                'route_name': 'Shahbag',
                'latitude': 23.7985906000000000,
                'longitude': 90.4422262000000000,
                'status': 'Pending',
                'product_list':[
                    {
                        'product_code':'1011123',
                        'product_name':'Azicin Tablet 250gm',
                        'qty': 10,
                        'receive_qty': 0,
                        'per_price': 20.50,
                        'total_price': 205.00,
                    },
                    {
                        'product_code':'1011124',
                        'product_name':'Aristoplex Syrup 250ml',
                        'qty': 40,
                        'receive_qty': 0,
                        'per_price': 60.32,
                        'total_price': 2412.80,
                    }
                ]
            },
            {
                'id': 2,
                'invoice_date': '2023-04-11',
                'customer_name': 'Hayder Pharmacy',
                'customer_addreess': 'Khejurbag (Near Pargandiara Bazar)',
                'customer_mobile': '0171716732',
                'delevery_type': 'Car',
                'route_name': 'Shahbag',
                'latitude': 23.7985906000000000,
                'longitude': 90.4422262000000000,
                'status': 'Done',
                'product_list':[
                    {
                        'product_code':'1011123',
                        'product_name':'Azicin Tablet 250gm',
                        'qty': 10,
                        'receive_qty': 10,
                        'per_price': 20.50,
                        'total_price': 205.00,
                    },
                    {
                        'product_code':'1011124',
                        'product_name':'Aristoplex Syrup 250ml',
                        'qty': 40,
                        'receive_qty': 40,
                        'per_price': 60.32,
                        'total_price': 2412.80,
                    }
                ]
            }
            ]}, status=status.HTTP_200_OK)
