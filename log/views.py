# -*- coding:utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404
from django.core.context_processors import csrf
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.decorators import login_required

# our own code
from log.models import Log
from log.models import log2Extend

@login_required
def index(request):
    logs = Log.objects.order_by("-id")
    paginator = Paginator(logs, 10)
    currentPage = request.POST.get('pageNum', 1)
    
    try:
        pager = paginator.page(currentPage)
    except InvalidPage:
        pager = paginator.page(1)
        
    pager.object_list = log2Extend(pager.object_list)
    return render_to_response("log/index.html",{"log_list":pager}, context_instance=RequestContext(request))
    
    
    
    