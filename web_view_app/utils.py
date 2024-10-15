from itertools import groupby
from delivery_app.models import DeliveryInfoModel, DeliveryModel

def get_main_data(da_code):
    # SAP data query
    sql = f"SELECT dis.billing_doc_no, dis.billing_date, sis.vat, sis.net_val, (sis.vat+sis.net_val) total_amount, sis.gate_pass_no FROM rdl_delivery_info_sap dis INNER JOIN rpl_sales_info_sap sis ON dis.billing_doc_no=sis.billing_doc_no WHERE dis.da_code='{da_code}' AND dis.billing_date=CURRENT_DATE;"
    sap_results = DeliveryInfoModel.objects.raw(sql)
    sap_sorted_results = sorted(sap_results, key=lambda x: x.gate_pass_no)
    sap_delivery_data = groupby(sap_sorted_results, key=lambda x: x.gate_pass_no)
    
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
    
    return list(main_data.values())
