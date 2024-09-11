from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

@api_view(['GET'])
def customer_details(request, partner):
    if request.method == 'GET':
        try:
            with connection.cursor() as cursor:
                # Raw SQL query with LIMIT 1
                cursor.execute("""
                    SELECT c.*, cl.latitude, cl.longitude 
                    FROM rpl_customer c 
                    LEFT JOIN exf_customer_location cl 
                    ON cl.customer_id = c.partner 
                    WHERE c.partner = %s 
                    LIMIT 1
                """, [partner])
                
                # Fetch a single row from the executed query
                row = cursor.fetchone()
                
                if row:
                    # Get column names
                    columns = [col[0] for col in cursor.description]
                    
                    # Convert the row into a dictionary
                    result = dict(zip(columns, row))
                else:
                    result = None

            return Response({
                "success": True,
                "result": result
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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

        # Get pagination parameters (page and limit)
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        offset = (page - 1) * limit

        # Append LIMIT and OFFSET to the query for pagination
        sql_query += f" LIMIT {limit} OFFSET {offset}"

        # Execute the raw query to fetch the customers with pagination
        with connection.cursor() as cursor:
            cursor.execute(sql_query)
            customers = cursor.fetchall()

        # Fetch total number of customers for pagination purposes
        total_query = "SELECT COUNT(*) FROM rpl_customer WHERE 1=1"
        if search_name:
            total_query += f" AND name1 LIKE '%%{search_name}%%'"
        if search_partner:
            total_query += f" AND partner LIKE '%%{search_partner}%%'"

        with connection.cursor() as cursor:
            cursor.execute(total_query)
            total_customers = cursor.fetchone()[0]

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

        # Calculate the total number of pages
        total_pages = (total_customers + limit - 1) // limit

        # Prepare response data
        return Response({
            "success": True,
            "total_customers": total_customers,
            "total_pages": total_pages,
            "current_page": page,
            "results": customer_list
        }, status=status.HTTP_200_OK)
