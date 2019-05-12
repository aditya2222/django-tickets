from hashlib import md5
from django.shortcuts import redirect, get_object_or_404, render_to_response, render
from django.http import HttpResponse
from django.contrib import messages
from django.core import serializers
from django.urls import reverse
from urllib.parse import urlencode
from rest_framework.renderers import TemplateHTMLRenderer, StaticHTMLRenderer
from rest_framework.generics import ListCreateAPIView, ListAPIView 
from rest_framework.response import Response
from datetime import datetime



from dashboard.models import (Articles2, Categories, Topics, StatusPromotionTicketing, 
                             AttendeeFormTypes, AttendeeFormOptions, AttendeeFormBuilder,
                             Tickets, AboutCountries, BankDetails)
from dashboard.forms import Articles2Form
from .serializers import (Articles2Serializer, CategorizedEventsSerializer, 
                         StatusPromotionTicketingSerializer, TicketsSerializer,
                          BankDetailsSerializer)


class ArticlesCreateAPIView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    queryset = Articles2.objects.all()
    serializer_class= Articles2Serializer
    template_name = 'dashboard/create-event/step_1/step_one.html'

    def get(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        return Response({'dashboard': self.queryset, 'serializer':self.serializer_class})


    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        event_md5 = md5(request.data.get('event_name').encode('utf-8')).hexdigest()[:34]
        print(event_md5)
        context = {'md5' : event_md5}
        serializer = Articles2Serializer(data=request.data, context=context)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        obj = serializer.save()
        event_id = obj.id
        #user_id = request.user.id
        user_id = request.session.get('userid')
        unique_id = f'EL{event_id}'
        data = {'event_id':event_id, 'unique_id':unique_id,'mode':'created',
                'private':0,'event_active':1,'approval':0, 'network_share':1,
                'ticketing':0, 'promotion':0, 'connected_user':user_id, 'complete_details':0}
        
        serializer = StatusPromotionTicketingSerializer(data=data)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        messages.success(request, f'Thank you. Event has been registered. your event id is {event_id}')
        base_url = reverse('dashboard:step_two', kwargs={'md5':event_md5, 'event_id':event_id})
        return redirect(base_url)

class CategoryCreateAPIView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, event_id, md5, *args, **kwargs):
        #if 'userid' not in request.session.keys():
         #   return redirect('/live/login')
        request.session['event_id'] = event_id
        request.session['md5'] = md5

        qs_categories = Categories.objects.values_list('category_id', 'category')      
        return Response({'context':qs_categories}, template_name = 'dashboard/create-event/step_2/step_two.html')

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5']
        event_id = request.session['event_id']
        context = {'event_id' : event_id}
        print(request.data)
        serializer = CategorizedEventsSerializer(data=request.data, context=context)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        print("----updated event tables")
        user_id = request.user.id
        if not user_id:
            user_id = 1
        unique_id = f'EL{event_id}'

        if request.POST.get('type1') == 'public':
            type_event = 0
        else:
            type_event = 1
        if request.POST.get('type2') == 'paid':
            ticketing = 1
        else:
            ticketing = 0
        data = {'private':type_event, 'ticketing':ticketing,}
        inst = get_object_or_404(StatusPromotionTicketing, event_id=event_id)
        print(inst)
        serializer = StatusPromotionTicketingSerializer(inst, data=data, partial=True)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        base_url = reverse('dashboard:step_three', kwargs={'md5':md5, 'event_id':event_id})
        return redirect(base_url)


class TopicsListAPIView(ListAPIView):
    def get(self, request):
        cat_id = request.GET.get('id')
        queryset = Topics.objects.filter(category=cat_id).order_by('topic')
        data = serializers.serialize('json', list(queryset))
        return HttpResponse(data)

class ThirdStepTemp(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, event_id, md5, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        request.session['event_id'] = event_id
        request.session['md5'] = md5
        return Response({}, template_name = 'dashboard/create-event/step_3/step_three_temp.html')

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5']
        event_id = request.session['event_id']
        base_url = reverse('dashboard:step_four', kwargs={'md5':md5, 'event_id':event_id})
        return redirect(base_url)
    
class DescriptionCreateAPIView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, event_id, md5, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        request.session['event_id'] = event_id
        request.session['md5'] = md5
        inst = get_object_or_404(Articles2, id=event_id)
        print(inst.country)
        qs_india=get_object_or_404( AboutCountries, country=inst.country)
        print(qs_india.bank_regex1)
        print(qs_india.bank_regex2)
        bank_regex1 = qs_india.bank_regex1
        bank_regex2 = qs_india.bank_regex2
        descform = Articles2Form()
        return Response({'descform':descform, 'bank_regex1':bank_regex1,'bank_regex2':bank_regex2},
                        template_name = 'dashboard/create-event/step_4/step_four.html')

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5']
        event_id = request.session['event_id']
        print(event_id)
        descform = Articles2Form(request.POST, instance = get_object_or_404(Articles2, id=event_id))
        if not descform.is_valid():
            return Response({'descform': descform,'flag':True})
        descform.save()
        base_url = reverse('dashboard:step_five', kwargs={'md5':md5, 'event_id':event_id})
        return redirect(base_url)

class QuestionCreateAPIView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, event_id, md5, *args, **kwargs):
        print('--')
        print(request.session.keys())
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        request.session['event_id'] = event_id
        request.session['md5'] = md5
        inst = get_object_or_404(StatusPromotionTicketing, event_id=event_id)
        print(inst)
        data={'complete_details':1}
        serializer = StatusPromotionTicketingSerializer(inst, data=data, partial=True)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        qs_types = AttendeeFormTypes.objects.values_list('type_id', 'name')      
        return Response({'context':qs_types}, template_name = 'dashboard/create-event/step_6/step_six.html')

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5']
        event_id = request.session['event_id']
        for i,j in request.POST.items():
            if i not in ['csrfmiddlewaretoken']:
                ques = request.POST.getlist(i)
                print(ques)
                type_inst = AttendeeFormTypes.objects.get(name=ques[2])
                type_id=type_inst.type_id
                add_que = AttendeeFormBuilder(event_id=event_id, ques_title=ques[1],
                                          ques_accessibility=int(ques[0]), ques_type=type_id)
                add_que.save()
                que_id = add_que.ques_id
                if type_id == 5:
                    options = ques[-1].split(',')
                    print(options)
                    for op in options:
                        add_op = AttendeeFormOptions(event_id=event_id, ques_id=que_id, option_name=op)
                        add_op.save()
        base_url = reverse('dashboard:event_added')
        return HttpResponse(base_url)

class CreateTicketsView(ListCreateAPIView):

    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'dashboard/create-event/step_5/step_five.html'
    tickets = Tickets.objects.all()
    aboutcountries = AboutCountries.objects.all()

    #event_id = 20

    serializer_class= TicketsSerializer(context=tickets)
    
    def get(self, request,event_id, md5, *args, **kwargs):    # must be included
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        request.session['event_id'] = event_id
        request.session['md5'] = md5
        

        inst = get_object_or_404(Articles2, id=event_id)
        date = inst.sdate.strftime('%m/%d/%Y')
        print(date)

        ticketvalues= Tickets.objects.values()
        listdictticket = [entry for entry in ticketvalues]
        listticket=[d['event_id'] for d in listdictticket]
        flag=False
        if event_id in listticket:
            flag=True

        print(listticket)
        print(request.session.values())

        return Response({'ticket': ticketvalues,'serializer':self.serializer_class,'event_start_date':date, 
                'a':self.aboutcountries,'cureventid':event_id,'flag':flag,}, 
                 template_name = 'dashboard/create-event/step_5/step_five.html'  )

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5'] 
        event_id = request.session['event_id']
        #context = {'event_id' : event_id}
        print(request.data)   
        tsd = request.data.get('start_date')
        exd = request.data.get('start_time_step5')
        sd = request.data.get('end_date')
        xd = request.data.get('end_time_step5')
        print(tsd + exd )
        print(exd)
        ticket_start_date = tsd +" "+ exd 
        ticket_start_date = datetime.strptime(ticket_start_date, '%d/%m/%Y %H:%M %p')
        expiry_date= sd +" "+ xd 
        expiry_date= datetime.strptime(expiry_date, '%d/%m/%Y %H:%M %p')
        context = {'ticket_start_date' : ticket_start_date,'expiry_date' :  expiry_date, 'event_id' : event_id, 'qty_left' : 110, 'ercess_fee': 1, 'transaction_fee':1}
        serializer = TicketsSerializer(data=request.data,  context = context)
        print("hi is this code running")
        print(serializer)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        print("data stored in table")
        base_url = reverse('dashboard:step_six', kwargs={'md5':md5, 'event_id':event_id})
        return redirect(base_url)

'''
class CreateTicketsView(ListCreateAPIView):

    renderer_classes = [TemplateHTMLRenderer]
#    template_name = 'dashboard/step_one.html'#templates-snippets/base.html'
    queryset = Tickets.objects.all()
    aboutcountries = AboutCountries.objects.all()
    serializer_class= TicketsSerializer(context=queryset)
    
    def get(self, request, event_id, md5, *args, **kwargs):#event_id, md5, must be included
        request.session['event_id'] = event_id
        request.session['md5'] = md5
        return Response({'dashboard': self.queryset, 'serializer':self.serializer_class, 'a':self.aboutcountries}, template_name = 'dashboard/create-event/step_5/step_five.html')

    def post(self, request, *args, **kwargs):
        md5 = request.session['md5'] #commented for now
        event_id = request.session['event_id']#commented fro now
        #context = {'event_id' : event_id}   
        tsd = request.data.get('ticket_start_date')
        exd = request.data.get('expiry_date')

        context = {'ticket_start_date' : tsd,'expiry_date' : exd,}
        serializer = TicketsSerializer(data=request.data,context = context)
        print("hi is this code running")
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        print("is this code running")
        base_url = reverse('dashboard:step_six', kwargs={'md5':md5, 'event_id':event_id})
        return redirect(base_url)
        return HttpResponse("Finally")
'''
class BankDetailsView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    serializer_class= BankDetailsSerializer
    template_name = 'dashboard/bankdetails.html'

    bankdetailscontents = BankDetails.objects.all()
    #print(bankdetailscontents[0])

    def get(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        user_id = self.request.user.id
        #if user_id in bankdetailscontents.user_id:
         #   pass
        return Response({'serializer':self.serializer_class,'i':self.bankdetailscontents}, template_name = 'dashboard/bankdetails.html')

    def post(self, request, *args, **kwargs):
        serializer = BankDetailsSerializer(data=request.data)
        print(request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        return HttpResponse("Finally")
        
