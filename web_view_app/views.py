from .utils import get_main_data
from django.shortcuts import render
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa

def summary(request, da_code):
    data_list = get_main_data(da_code)
    return render(request, "summary.html", {"data": data_list,"da_code":da_code})


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
    data = get_main_data(da_code) 
    return render_to_pdf('test.html', {'data': data,"da_code":da_code})

def test(request,da_code):
    data=get_main_data(da_code)
    return render(request,"test.html",{"data":data,"da_code":da_code})


