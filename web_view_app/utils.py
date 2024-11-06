from delivery_app.models import DeliveryInfoModel, DeliveryModel    
from collection_app.models import ReturnListModel
from collections import defaultdict
from django.db import connection

def get_sap_data(da_code):
    query = '''
        SELECT 
            dis.da_code,
            dis.da_name,
            dis.route,
            dis.billing_date,
            sis.gate_pass_no,
            COUNT(DISTINCT sis.billing_doc_no) AS total_billing_doc_no,
            SUM(sis.net_val+sis.vat) AS total_net_val,
            COUNT(DISTINCT sis.gate_pass_no) AS total_gate_pass,
            GROUP_CONCAT(DISTINCT sis.billing_doc_no) AS billing_doc_list,
            GROUP_CONCAT(DISTINCT sis.net_val) AS net_val_list
        FROM 
            rdl_delivery_info_sap AS dis
        JOIN 
            rpl_sales_info_sap AS sis ON dis.billing_doc_no = sis.billing_doc_no
        WHERE 
            dis.da_code = %s AND dis.billing_date = CURRENT_DATE
        GROUP BY 
            dis.da_code, dis.route, dis.billing_date, sis.gate_pass_no
    '''

    with connection.cursor() as cursor:
        cursor.execute(query, [da_code])
        columns = [col[0] for col in cursor.description]
        results = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    if not results:
        return {}  # Return empty if no results found
    # Prepare da_info 
    da_info = {
        "da_code": results[0]["da_code"],
        "da_name": results[0]["da_name"],
        "route": results[0]["route"],
        "billing_date": results[0]["billing_date"]
    }

    # Prepare total_data
    total_invoices = sum(result["total_billing_doc_no"] for result in results)
    total_amount = sum(result["total_net_val"] for result in results)
    total_gate_pass = len(results) 

    total_data = {
        "total_invoice": total_invoices,
        "total_amount": round(float(total_amount), 2),
        "total_gate_pass": total_gate_pass
    }

    # Prepare sap_data
    sap_data = {}
    for result in results:
        gate_pass_no = result["gate_pass_no"]
        sap_data[gate_pass_no] = {
            "total_amount": round(float(result["total_net_val"]), 2),
            "total_invoice": result["total_billing_doc_no"],
            # "billing_doc_list": result["billing_doc_list"].split(',') if result["billing_doc_list"] else [],
            # "net_val_list": result["net_val_list"].split(',') if result["net_val_list"] else []
        }
    
    return {
        "da_info": da_info,
        "total_data": total_data,
        "sap_data": sap_data
    }


def get_delivery_data(da_code):
    sql = """
        SELECT gate_pass_no,
               COUNT(CASE WHEN delivery_status = 'Done' THEN 1 END) AS total_delivery_done,
               SUM(net_val) AS total_net_val,
               COUNT(CASE WHEN cash_collection_status = 'Done' THEN 1 END) AS total_cash_collection,
               SUM(CASE WHEN cash_collection_status = 'Done' THEN cash_collection ELSE 0 END) AS total_cash_collection_amount,
               SUM(return_amount) AS total_return_amount,
               SUM(due_amount) AS total_due_amount
        FROM rdl_delivery 
        WHERE da_code = %s AND billing_date = CURRENT_DATE
        GROUP BY gate_pass_no;
    """
    
    with connection.cursor() as cursor:
        cursor.execute(sql, [da_code])
        results = cursor.fetchall()

    delivery_data = {}
    # Initialize total counters
    total_delivery = 0
    total_collection = 0
    total_delivered_amount = 0.00
    total_collection_amount = 0.00
    total_return_amount = 0.00
    total_due_amount = 0.00

    # Process results
    for row in results:
        gate_pass_no = row[0]
        total_delivery_done = row[1] or 0  # Ensure 0 if None
        net_val = round(float(row[2]), 2) if row[2] is not None else 0.00
        total_cash_collection = row[3] or 0
        total_cash_collection_amount = round(float(row[4]), 2) if row[4] is not None else 0.00
        total_return_amount_row = round(float(row[5]), 2) if row[5] is not None else 0.00
        total_due_amount_row = round(float(row[6]), 2) if row[6] is not None else 0.00

        # Populate delivery_data
        delivery_data[gate_pass_no] = {
            "total_delivery_done": total_delivery_done,
            "net_val": net_val,
            "total_cash_collection": total_cash_collection,
            "total_cash_collection_amount": total_cash_collection_amount,
            "total_return_amount": total_return_amount_row,
            "total_due_amount": total_due_amount_row,
        }

        # Aggregate totals in a single loop
        total_delivery += total_delivery_done
        total_collection += total_cash_collection
        total_delivered_amount += float(net_val)
        total_collection_amount += float(total_cash_collection_amount)
        total_return_amount += float(total_return_amount_row)
        total_due_amount += float(total_due_amount_row)

    # Calculate remaining amounts
    total_collection_remaining = total_delivery - total_collection
    total_collection_remaining_amount = round(float(total_delivered_amount) - float(total_collection_amount), 2)

    total_data = {
        "total_delivery": total_delivery,
        "total_collection": total_collection,
        "total_delivered_amount": round(total_delivered_amount, 2),
        "total_collection_amount": round(total_collection_amount, 2),
        "total_collection_remaining": total_collection_remaining,
        "total_collection_remaining_amount": total_collection_remaining_amount,
        "total_return_amount": round(total_return_amount, 2),
        "total_due_amount": round(total_due_amount, 2),
    }

    return [delivery_data, total_data]

def get_main_data(da_code):
    # Retrieve SAP data and delivery data
    sap = get_sap_data(da_code)
    delivery_data, total_delivery_data = get_delivery_data(da_code)

    sap_data = sap["sap_data"] 
    da_info = sap["da_info"] 
    total_sap_data = sap["total_data"] 

    main_data = {}

    for gate_pass_no, items in sap_data.items():
        # Extract delivery information for the current gate_pass_no
        delivery = delivery_data.get(gate_pass_no, {})

        # Calculate values while ensuring safe access with defaults
        total_invoice = items.get("total_invoice", 0)
        total_amount = round(float(items.get("total_amount", 0.00)), 2)
        total_delivery_done = delivery.get("total_delivery_done", 0)
        delivery_net_val = round(float(delivery.get("net_val", 0.00) or 0.00) - (float(delivery.get("total_return_amount", 0.00) or 0.00)), 2)
        remaining_delivery_amount = round(float(total_amount) - float(delivery.get("net_val", 0.00) or 0.00), 2)
        
        # Populate main_data for each gate_pass_no
        main_data[gate_pass_no] = {
            "gate_pass_no": gate_pass_no,
            "total_invoice": total_invoice,
            "total_amount": total_amount,
            "delivery_done": total_delivery_done,
            "delivery_net_val": delivery_net_val,
            "delivery_remaining": total_invoice - total_delivery_done,
            "remaining_delivery_amount": remaining_delivery_amount,
            "cash_collection": delivery.get("total_cash_collection", 0),
            "cash_collection_amount": round(float(delivery.get("total_cash_collection_amount", 0.00) or 0.00), 2),
            "cash_collection_remaining": total_delivery_done - delivery.get("total_cash_collection", 0),
            "cash_collection_remaining_amount": round(float(delivery_net_val) - float(delivery.get("total_cash_collection_amount", 0.00) or 0.00), 2),
            "return_amount": round(float(delivery.get("total_return_amount", 0.00) or 0.00), 2),
            "due_amount": round(float(delivery.get("total_due_amount", 0.00) or 0.00), 2)
        }

    # Prepare total data
    total_data = {
        "total_invoice": total_sap_data["total_invoice"],
        "total_amount": total_sap_data["total_amount"],
        "total_delivery": total_delivery_data["total_delivery"],
        "total_delivered_amount": round(total_delivery_data["total_delivered_amount"] - float(total_delivery_data["total_return_amount"]),2),
        "delivery_remaining": total_sap_data["total_invoice"] - total_delivery_data["total_delivery"],
        "remaining_delivery_amount": round(float(total_sap_data["total_amount"]) - float(total_delivery_data["total_delivered_amount"]), 2),
        "total_collection": total_delivery_data["total_collection"],
        "total_collection_amount": round(float(total_delivery_data["total_collection_amount"]), 2),
        "cash_collection_remaining": total_delivery_data["total_collection_remaining"],
        "cash_collection_remaining_amount": round(total_delivery_data["total_collection_remaining_amount"] - float(total_delivery_data["total_return_amount"]), 2),
        "total_return_amount": round(float(total_delivery_data["total_return_amount"]), 2),
        "total_due_amount": round(float(total_delivery_data["total_due_amount"]), 2),
        "total_gate_pass": total_sap_data["total_gate_pass"]
    }

    # Compile final results
    results = [list(main_data.values()), da_info, total_data]
    return results
    
def get_due_amount_list(da_code):
    sql = (
        "SELECT d.id, d.billing_doc_no, d.partner, d.gate_pass_no, d.route_code, d.due_amount, d.net_val, "
        " d.return_amount, d.cash_collection , c.name1, c.contact_person, c.mobile_no "
        "FROM rdl_delivery d "
        "INNER JOIN rpl_customer c ON d.partner=c.partner "
        "WHERE d.da_code=%s AND d.billing_date=CURRENT_DATE AND due_amount>0;"
    )
    db_results = DeliveryModel.objects.raw(sql,[da_code])

    due_list={}
    for item in db_results:
        key=item.partner
        
        if key in due_list:
            due_list[key]['invoice_list'].append({
                "due_amount":item.due_amount,
                "billing_doc_no":item.billing_doc_no    
            })
        else:
            data={
                "pid":item.partner,
                "name":item.name1,
                "customer":item.contact_person,
                "mobile":item.mobile_no,
                "invoice_list":[{
                    "due_amount":item.due_amount,
                    "billing_doc_no":item.billing_doc_no
                }]
            }
            due_list[key]=data
    results=list(due_list.values())
    return results


def get_product_return_list(da_code):
    sql = (
        "SELECT rl.id, rl.matnr, m.material_name, rl.batch, rl.return_quantity, "
        "rl.return_net_val, rl.partner, rl.billing_doc_no, rl.gate_pass_no, "
        "c.name1,c.contact_person,c.mobile_no "
        "FROM rdl_return_list rl "
        "INNER JOIN rpl_material m ON rl.matnr = m.matnr "
        "INNER JOIN rpl_customer c ON rl.partner=c.partner "
        "WHERE rl.da_code = %s AND rl.billing_date = CURRENT_DATE;"
    )
    query_results = ReturnListModel.objects.raw(sql, [da_code])
    product_list={}
    for item in query_results:
        key=item.partner
        
        if key in product_list:
            product_list[key]['return_list'].append({
                "matnr":item.matnr,
                "batch":item.batch,
                "material_name":item.material_name,
                "return_quantity":item.return_quantity,
                "return_net_val":item.return_net_val,
                "billing_doc_no":item.billing_doc_no,
            })
        else:
            data={
                "pid":item.partner,
                "name":item.name1,
                "customer":item.contact_person,
                "mobile":item.mobile_no,
                "return_list":[{
                    "matnr":item.matnr,
                    "batch":item.batch,
                    "material_name":item.material_name,
                    "return_quantity":item.return_quantity,
                    "return_net_val":item.return_net_val,
                    "billing_doc_no":item.billing_doc_no,
                }]
            }
            product_list[key]=data
    
    results=list(product_list.values())
    return results


# Get product Return List
def get_product_return_list2(da_code):
    sql = (
        "SELECT rl.id, rl.matnr, m.material_name, rl.batch, rl.return_quantity, "
        "rl.return_net_val, rl.partner, rl.billing_doc_no, rl.gate_pass_no "
        "FROM rdl_return_list rl "
        "INNER JOIN rpl_material m ON rl.matnr = m.matnr "
        "WHERE da_code = %s AND billing_date = CURRENT_DATE;"
    )
    db_results = ReturnListModel.objects.raw(sql, [da_code])
    grouped_materials=defaultdict(list)
    total_return_quantity=0
    for item in db_results:
        total_return_quantity+=item.return_quantity
        key=str(item.matnr)+str(item.batch)
        data={
            'matnr': item.matnr,
            'batch': item.batch,
            'material_name': item.material_name,
            'return_quantity': item.return_quantity,
            'return_net_val': item.return_net_val
            }
        if key in grouped_materials:
            grouped_materials[key]['return_quantity']+=item.return_quantity
            grouped_materials[key]['return_net_val']+=item.return_net_val 
        else:
            grouped_materials[key]=data
    results=[list(grouped_materials.values()),total_return_quantity]
    return results