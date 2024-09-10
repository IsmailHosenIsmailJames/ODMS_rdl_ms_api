from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.db import connection

@api_view(['GET'])
def customer_list(request):
    if request.method == 'GET':
        # Base SQL query
        sql_query = "SELECT * FROM rpl_customer WHERE 1=1"

        # Apply search filters for `name1` and `partner`
        search_name = request.GET.get('name1', '')
        search_partner = request.GET.get('partner', '')
        if search_name:
            sql_query += f" AND name1 LIKE '%%{search_name}%%'"
        if search_partner:
            sql_query += f" AND partner LIKE '%%{search_partner}%%'"

        # Execute the raw query
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            customers = cursor.fetchall()

        # Convert raw SQL data to a list of dictionaries
        columns = [
            'partner', 'name1', 'name2', 'contact_person', 'street', 
            'street1', 'street2', 'street3', 'post_code', 'upazilla', 
            'district', 'mobile_no', 'email', 'drug_reg_no', 
            'customer_grp', 'trans_p_zone'
        ]
        customer_list = [
            dict(zip(columns, customer)) for customer in customers
        ]

        # Apply pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(customer_list, 10)  # Show 10 customers per page
        try:
            customers_page = paginator.page(page)
        except:
            return Response({"success": False, "error": "Invalid page number"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare response data
        return Response({
            "success": True,
            "total_customers": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": customers_page.number,
            "results": customers_page.object_list
        }, status=status.HTTP_200_OK)
