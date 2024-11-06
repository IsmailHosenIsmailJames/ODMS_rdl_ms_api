from .utils import get_main_data,get_product_return_list,get_due_amount_list,get_product_return_list2
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa


def reports(request,da_code):
    return render(request, "reports.html",{"da_code":da_code})

def summary(request, da_code):
    data_list=get_main_data(da_code)
    data = data_list[0]
    da_info = data_list[1]
    total=data_list[2]
    return render(request, "summary.html", {"data": data,"da_info":da_info,"total":total,"status":"view"})


def render_to_pdf(template_src, context_dict):
    template = render_to_string(template_src, context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="da_summary.pdf"'
    
    # Create PDF from HTML
    pisa_status = pisa.CreatePDF(template, dest=response)
    
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + template + '</pre>')
    return response

def da_summary_pdf(request,da_code):
    data_list=get_main_data(da_code)
    data = data_list[0]
    da_info = data_list[1]
    total=data_list[2]
    return render_to_pdf('summary.html', {'data': data,"da_info":da_info,"total":total,"status":"print"})

def test(request,da_code):
    # data=get_main_data(da_code)
    da_info={
        "da_code":da_code
    }
    return render(request,"test.html",{"da_info":da_info,"status":"view"})

def product_return_list_v2(request,da_code):
    data_list=get_product_return_list2(da_code)
    return_list=data_list[0]
    total_return=data_list[1]
    da_info={
        "da_code":da_code
    }
    return render(request,"return_list_v2.html",{"return_list":return_list,"total_return":total_return,"da_info":da_info,"status":"view"})

def due_amount_list(request,da_code):
    data_list=get_due_amount_list(da_code)
    da_info={
        "da_code":da_code,
    }
    return render(request,"due_amount_list.html",{"data":data_list,"da_info":da_info})

def product_return_list_v1(request,da_code):
    data_list=get_product_return_list(da_code)
    da_info={
        "da_code":da_code
    }
    return render(request,"return_list_v1.html",{"data":data_list,"da_info":da_info})


def admin_dashboard_manual(request):
    return render(request, "admin_dashboard_manual.html")

def dashboard_manual(request):
    return render(request, "dashboard_manual.html")