from itertools import groupby
from delivery_app.models import DeliveryInfoModel, DeliveryModel    
from collection_app.models import ReturnListModel
from collections import defaultdict


# Get SAP Assigned Data
def get_sap_data(da_code):
    sql = f"SELECT dis.da_name,dis.route,dis.billing_doc_no, dis.billing_date, sis.vat, sis.net_val, (sis.vat+sis.net_val) total_amount, sis.gate_pass_no FROM rdl_delivery_info_sap dis INNER JOIN rpl_sales_info_sap sis ON dis.billing_doc_no=sis.billing_doc_no  WHERE dis.da_code=%s AND dis.billing_date=CURRENT_DATE;"
    results = DeliveryInfoModel.objects.raw(sql, [da_code])
    sorted_results = sorted(results, key=lambda x: x.gate_pass_no)
    grouped_results = groupby(sorted_results, key=lambda x: x.gate_pass_no)

    da_info={
        "da_code":da_code,
        "da_name":results[0].da_name,
        "route":results[0].route,
        "billing_date":results[0].billing_date
    }
    # Total Data
    amount=0.00
    invoices=set()
    gate_pass=set()
    for item in results:
        invoices.add(item.billing_doc_no)
        amount+=float(item.total_amount)
        gate_pass.add(item.gate_pass_no)
    total_data={
        "total_invoice":len(invoices),
        "total_amount":round(amount,2),
        "total_gate_pass":len(gate_pass)
    }
    # Gate PASS wise grouped data
    sap_data = {}
    for gate_pass_no, group in grouped_results:
        total_amount = 0.0
        total_invoice = set()
        for item in group:
            total_amount += float(item.total_amount)
            total_invoice.add(item.billing_doc_no)
        sap_data[gate_pass_no] = {
            "total_amount": round(total_amount, 2),
            "total_invoice": len(total_invoice),
        }
    for gate_pass_no, group in grouped_results:
        print(gate_pass_no)
        print(group)
    data=[sap_data,da_info,total_data]
    return data

# Get delivery data for specific DA
def get_delivery_data(da_code):
    sql = f"SELECT * FROM rdl_delivery WHERE da_code=%s AND billing_date=CURRENT_DATE;"
    results = DeliveryModel.objects.raw(sql, [da_code])
    sorted_results = sorted(results, key=lambda x: x.gate_pass_no)
    grouped_results = groupby(sorted_results, key=lambda x: x.gate_pass_no)
    # Gate pass wise grouped data
    delivery_data = {}
    for gate_pass_no, group in grouped_results:
        total_delivery_done , total_cash_collection = 0,0
        total_net_val , total_return_amount = 0.00,0.00
        total_cash_collection_amount , total_due_amount = 0.00,0.00
        for item in group:
            total_net_val += float(item.net_val)
            if item.delivery_status == "Done":
                total_delivery_done += 1
                total_return_amount += float(item.return_amount)
                total_due_amount += float(item.due_amount)
                if item.cash_collection_status == "Done":
                    total_cash_collection += 1
                    total_cash_collection_amount += float(item.cash_collection)
                    
        delivery_data[gate_pass_no] = {
            "total_delivery_done": total_delivery_done,
            "net_val": round(total_net_val, 2),
            "total_cash_collection": total_cash_collection,
            "total_cash_collection_amount": round(total_cash_collection_amount, 2),
            "total_return_amount": round(total_return_amount, 2),
            "total_due_amount": round(total_due_amount, 2),
        }
    # Total Data
    total_delivery=0
    total_collection=0
    total_delivered_amount=0.00
    total_collection_amount=0.00
    return_amount=0.00
    due_amount=0.00
    for gate_pass_no, item in delivery_data.items():
        total_delivery+=item["total_delivery_done"]
        total_collection+=item["total_cash_collection"]
        total_delivered_amount+=item["net_val"]
        total_collection_amount+=item["total_cash_collection_amount"]
        return_amount+=item["total_return_amount"]
        due_amount+=item["total_due_amount"]
    total_data={
        "total_delivery":total_delivery,
        "total_collection":total_collection,
        "total_delivered_amount":round(total_delivered_amount,2),
        "total_collection_amount":round(total_collection_amount,2),
        "total_collection_remaining":total_delivery-total_collection,
        "total_collection_remaining_amount":round(total_delivered_amount-total_collection_amount,2),
        "total_return_amount":round(return_amount,2),
        "total_due_amount":round(due_amount,2),
    }
    
    return [delivery_data,total_data]

# Merge sap and delivery data
def get_main_data(da_code):
    sap=get_sap_data(da_code)
    dv=get_delivery_data(da_code)
    sap_data = sap[0]
    da_info = sap[1]
    total_sap_data = sap[2]
    delivery_data =dv[0]
    total_delivery_data = dv[1]
    main_data = {}
    for gate_pass_no, items in sap_data.items():
        delivery = delivery_data.get(gate_pass_no, {})
        main_data[gate_pass_no] = {
            "gate_pass_no": gate_pass_no,
            "total_invoice": items.get("total_invoice", 0),
            "total_amount": round(items.get("total_amount", 0.00),2),
            "delivery_done": delivery.get("total_delivery_done", 0),
            "delivery_net_val": round(delivery.get("net_val", 0.00)-(delivery.get("total_return_amount", 0.00) or 0.00),2),
            "delivery_remaining": items.get("total_invoice", 0) - (delivery.get("total_delivery_done", 0) or 0),
            "remaining_delivery_amount": round(items.get("total_amount", 0.00) - round(delivery.get("net_val", 0.00)-(delivery.get("total_return_amount", 0.00) or 0.00),2)),
            "cash_collection": delivery.get("total_cash_collection", 0),
            "cash_collection_amount": round(delivery.get("total_cash_collection_amount", 0.00),2),
            "cash_collection_remaining": delivery.get("total_delivery_done", 0) - (delivery.get("total_cash_collection", 0) or 0),
            "cash_collection_remaining_amount": round(delivery.get("net_val", 0.00)-(delivery.get("total_return_amount", 0.00) or 0.00) - delivery.get("total_cash_collection_amount", 0.00),2),
            "return_amount": round(delivery.get("total_return_amount", 0.00),2),
            "due_amount": round(delivery.get("total_due_amount", 0.00),2)
        }
    total_data={
        "total_invoice":total_sap_data["total_invoice"],
        "total_amount":total_sap_data["total_amount"],
        "total_delivery":total_delivery_data["total_delivery"],
        "total_delivered_amount":total_delivery_data["total_delivered_amount"],
        "delivery_remaining":total_sap_data["total_invoice"]-total_delivery_data["total_delivery"],
        "remaining_delivery_amount":round(total_sap_data["total_amount"]-total_delivery_data["total_delivered_amount"],2),
        "total_collection":total_delivery_data["total_collection"],
        "total_collection_amount":total_delivery_data["total_collection_amount"],
        "cash_collection_remaining":total_delivery_data["total_collection_remaining"],
        "cash_collection_remaining_amount":total_delivery_data["total_collection_remaining_amount"],
        "total_return_amount":total_delivery_data["total_return_amount"],
        "total_due_amount":total_delivery_data["total_due_amount"],
        "total_gate_pass":total_sap_data["total_gate_pass"]
    }
    results=[list(main_data.values()),da_info,total_data]
    return results
    

# Get product Return List
def get_product_return_list(da_code):
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


def get_product_return_list2(da_code):
    sql = (
        "SELECT rl.id, rl.matnr, m.material_name, rl.batch, rl.return_quantity, "
        "rl.return_net_val, rl.partner, rl.billing_doc_no, rl.gate_pass_no, "
        "c.name1,c.contact_person,c.mobile_no "
        "FROM rdl_return_list rl "
        "INNER JOIN rpl_material m ON rl.matnr = m.matnr "
        "INNER JOIN rpl_customer c ON rl.partner=c.partner "
        "WHERE da_code = %s AND billing_date = CURRENT_DATE;"
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

























def old_get_main_data(da_code):
    # SAP data query
    sql = f"SELECT dis.da_name,dis.route,dis.billing_doc_no, dis.billing_date, sis.vat, sis.net_val, (sis.vat+sis.net_val) total_amount, sis.gate_pass_no FROM rdl_delivery_info_sap dis INNER JOIN rpl_sales_info_sap sis ON dis.billing_doc_no=sis.billing_doc_no WHERE dis.da_code='{da_code}' AND dis.billing_date=CURRENT_DATE;"
    sap_results = DeliveryInfoModel.objects.raw(sql)
    sap_sorted_results = sorted(sap_results, key=lambda x: x.gate_pass_no)
    sap_delivery_data = groupby(sap_sorted_results, key=lambda x: x.gate_pass_no)
    
    da_name=sap_results[0].da_name
    route=sap_results[0].route
    billing_date=sap_results[0].billing_date
    print(da_code,da_name,route,billing_date)
    # Calculate SAP Delivery Data
    calculated_sap_delivery_data = {}
    for gate_pass_no, group in sap_delivery_data:
        total_amount = 0.0
        total_invoice = set()
        for item in group:
            total_amount += float(item.total_amount)
            total_invoice.add(item.billing_doc_no)
        calculated_sap_delivery_data[gate_pass_no] = {
            "total_amount": round(total_amount, 2),
            "total_invoice": len(total_invoice),
        }
    
    # Delivery data query
    sql2 = f"SELECT * FROM rdl_delivery WHERE da_code='{da_code}' AND billing_date=CURRENT_DATE;"
    results = DeliveryModel.objects.raw(sql2)
    sorted_results = sorted(results, key=lambda x: x.gate_pass_no)
    delivery_data = groupby(sorted_results, key=lambda x: x.gate_pass_no)
    
    # Calculate Delivery Data
    calculated_delivery_data = {}
    for gate_pass_no, group in delivery_data:
        total_delivery_done = total_cash_collection = 0
        total_net_val = total_return_amount = total_cash_collection_amount = total_due_amount = 0.00
        for item in group:
            total_net_val += float(item.net_val)
            if item.delivery_status == "Done":
                total_delivery_done += 1
                total_return_amount += float(item.return_amount)
                total_due_amount += float(item.due_amount)
                if item.cash_collection_status == "Done":
                    total_cash_collection += 1
                    total_cash_collection_amount += float(item.cash_collection)

        calculated_delivery_data[gate_pass_no] = {
            "total_delivery_done": total_delivery_done,
            "net_val": round(total_net_val, 2),
            "total_cash_collection": total_cash_collection,
            "total_cash_collection_amount": round(total_cash_collection_amount, 2),
            "total_return_amount": round(total_return_amount, 2),
            "total_due_amount": round(total_due_amount, 2),
        }
    
    # Merge SAP and Delivery Data
    main_data = {}
    for gate_pass_no, items in calculated_sap_delivery_data.items():
        delivery = calculated_delivery_data.get(gate_pass_no, {})
        main_data[gate_pass_no] = {
            "gate_pass_no": gate_pass_no,
            "total_invoice": items.get("total_invoice", 0),
            "total_amount": items.get("total_amount", 0.00),
            "delivery_done": delivery.get("total_delivery_done", 0),
            "delivery_net_val": delivery.get("net_val", 0.00)-(delivery.get("total_return_amount", 0.00) or 0.00),
            "delivery_remaining": items.get("total_invoice", 0) - (delivery.get("total_delivery_done", 0) or 0),
            "remaining_delivery_amount": items.get("total_amount", 0.00) - (delivery.get("delivery_net_val", 0.00) or 0.00),
            "cash_collection": delivery.get("total_cash_collection", 0),
            "cash_collection_amount": delivery.get("total_cash_collection_amount", 0.00),
            "cash_collection_remaining": delivery.get("total_delivery_done", 0) - (delivery.get("total_cash_collection", 0) or 0),
            "cash_collection_remaining_amount": delivery.get("net_val", 0.00)-(delivery.get("total_return_amount", 0.00) or 0.00) - delivery.get("total_cash_collection_amount", 0.00),
            "return_amount": delivery.get("total_return_amount", 0.00),
            "due_amount": delivery.get("total_due_amount", 0.00),
        }
    data=list(main_data.values())
    # data.append({'da_code':da_code,'da_name':da_name,'route':route,'billing_date':billing_date})
    # get da info
    def return_da_info():
        return ({
            "da_name": da_name,
            "route": route,
            "billing_date": billing_date})
    print(data)
    return data

