import  os
import json
from django.shortcuts import render , redirect
from .forms import HowForm, ChangePasswordForm
from Ercesscorp.models import RegistrationData, Users
#from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import  Articles2, Tickets  # , Photo
# from .models import Photo
#from .forms import PhotoForm

from django.views.decorators.csrf import csrf_exempt
from PIL import Image
from io import  StringIO
from django.core.files.base import ContentFile
import  os
from django.conf import settings
from hashlib import md5
from django.http import  JsonResponse, HttpResponse, HttpResponseRedirect

from .forms import HowForm, ChangePasswordForm
from Ercesscorp.third_party_security import smartlogin
from .models import Articles2, StatusPromotionTicketing, rsvp#, Photo
from Ercesscorp.models import RegistrationData, Users
# from .models import Photo
#from .forms import PhotoForm



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status

#this is new
from .serializers import EditViewSerializer,EditTicketSerializer
from rest_framework import viewsets


email_sent_from = settings.EMAIL_HOST_USER



def getHow(request):
    # print('inside get how')
    sub = request.session.get('sub')
    # print(sub)
    if sub == 0:
        sub = False
    elif sub == 1:
        sub = True
    uname = request.session.get('username')
    # print('in views of dash')
    # print(uname)
    if request.method == 'POST':
        form = HowForm(request.POST)
        if form :
            how = request.POST.get('choices', '')
            other = request.POST.get('other', '')
            x = User.objects.get(username=uname)
            # print('in dash views')
            # print(x.pk)
            if x :
                r = RegistrationData.objects.get(user_id = x.pk)
                print(r)
                r.submitted = 1
                if how != 'others' :
                    r.how_u_know = how
                else :
                    r.how_u_know = other
                r.save()
                # return  redirect('dashboard:home')
                sub = True
        form = HowForm()
        return render(request, 'gethow.html', {'sub': sub, 'form': form})
    else :
        form = HowForm()
        # print('sub'+str(sub))
        return render(request , 'gethow.html' ,{'sub':sub ,'form':form})
'''

def third_step(request , eventid):
    pic1 = pic2 = None
    x = ''
    ft = fe = fi = 0
    didnt_recognize = False
    error_upload = False
    upload_size_error = False
    user = None
    try:
        user = Articles2.objects.get(id=eventid)
    except:
        user = None
        print('inside except third step ')
    else :
        pic1 = user.company_logo
        pic2 = user.event_banner
    if request.method == 'POST' :
        if user is not None:
            try :
                i = float(request.POST.get('x'))
                j = float(request.POST.get('y'))
                height = float(request.POST.get('height'))
                width = float(request.POST.get('width'))
                print(type(i), type(j), type(width), type(height))
            except:pass

            try:
                iname = image = request.FILES['thumbnail']
                print(image.size)
                user.company_logo = thumbnail(image ,iname ,i,j, width,height)
                print('saved')
            except Exception as e:
                ft = 1
                print('thumbnail')
                print(e)
            else :x = user.save()
            try :
                iname = image = request.FILES['eventbanner']
                if image.size >5242880 :
                    return redirect('/live/dashboard/create-event/step-three/'+ eventid +'?upload_size_error=True')
                else:
                    user.event_banner = passer(image, iname, i,j, width,height)
                    print('saved')
                # user.event_banner = passer(user.event_banner.file, i, j, width, height)
            except :
                fe = 1
                print('eventbanner')
            else : x = user.save()

            try:
                user.editable_image = request.FILES['editableimage']
                #have to send mail to ercess
            except :
                fi  = 1
                print('editableimage')
            else :x = user.save()
            if x is None :
                print('inside else if ')
                return redirect('/live/dashboard/create-event/step-three/'+ eventid)
            else :
                return redirect('/live/dashboard/create-event/step-three/'+ eventid +'?error_upload=True')
        else :
            return redirect('/live/dashboard/create-event/step-three/'+ eventid +'?didnt_recognize=True')
    else :
        pic1 = user.company_logo
        pic2 = user.event_banner
        if 'error_upload' in request.GET:
            error_upload = True
        if 'didnt_recognize' in request.GET:
            didnt_recognize = True
        if 'upload_size_error' in request.GET:
            upload_size_error = True
        return render(request , 'step_three.html',{'error_upload':error_upload,
                                                   'didnt_recognize':didnt_recognize,
                                                   'pic1':pic1 ,'pic2':pic2 , 'upload_size_error':upload_size_error})
'''
'''
def photo_list(request):
    photos = Photo.objects.all()
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            print(form.save())
            return redirect('/live/dashboard/test')
    else:
        form = PhotoForm()
    return render(request, 'photo_list.html', {'form': form, 'photos': photos})
'''

def passer(image,iname, x , y , w , h):
    image = Image.open(image)
    print(image)
    box = (x, y, w + x, h + y)
    cropped_image = image.crop(box)
    print(cropped_image)
    resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
    print(resized_image)
    resized_image.save(r'media\third_step_images\e' + str(iname))
    return  str(r'third_step_images\e')+str(iname)


def thumbnail(image,iname, x , y , w , h):
    image = Image.open(image)
    print(image)
    box = (x, y, w + x, h + y)
    cropped_image = image.crop(box)
    print(cropped_image)
    resized_image = cropped_image.resize((100, 100), Image.ANTIALIAS)
    print(resized_image)
    # resized_image.save(r'media\third_step_images\e' + str(iname))
    # x = str(iname).split('.')
    resized_image.save(r'media\third_step_images\e'+str(iname), "JPEG",quality=100)
    return  str(r'third_step_images\e')+str(iname)


@csrf_exempt
def change_password(request):
    print('inside view')
    if request.method == 'POST':
        print('post')
        requestData = request.body
        requestDataDecode = requestData.decode('utf8').replace("'", '"')
        requestDataJson = json.loads(requestDataDecode)
        print(requestDataJson)
        userpassword = requestDataJson['oldpass']
        newpassword = requestDataJson['newpass']

        #form = ChangePasswordForm(request.POST)
        #if form.is_valid():
        flag=False
        success=False
        exe = False
        #newpassword = form.cleaned_data['newpassword1']
         #   userpassword = form.cleaned_data['oldpassword']
        username = request.session.get('username')
        print(username)
        x = Users.objects.get(user=username)
        print(x)
        email = x.user
        password = x.password
        pswd_encoded = md5(userpassword.encode('utf-8')).hexdigest()
        print(Users.objects.filter(user=email, password=pswd_encoded).exists())
        if Users.objects.filter(user=email, password=pswd_encoded).exists():
                user = Users.objects.get(user=email, password=pswd_encoded)
                new_pswd_encoded = md5(newpassword.encode('utf-8')).hexdigest()
                user.password = new_pswd_encoded
                user.save()
                try:
                    send_mail('Password Changed','You have successfully changed your password.',email_sent_from,[email,])
                    print('in try')
                    #clear_list()
                except Exception as e:
                    print(e)
                    messageData = {'message':'Unexpected Error occured. Try again later !','responseType':'success', 'messageType':'error'}
                    return HttpResponse(json.dumps(messageData))
                    #return render(request, 'settings.html',{'error':e,'exe':exe,'form': form})
                print('done')
                messageData = {'message':'Password changed successfully !','responseType':'success', 'messageType':'success'}
                return HttpResponse(json.dumps(messageData))
                #return render(request, 'settings.html',{'success':success,'form': form})

        else:
            print('wrong')
            messageData = {'message':'Incorrect Old Password','responseType':'success', 'messageType':'error'}
            return HttpResponse(json.dumps(messageData))
            #return render(request, 'settings.html',{'error':'You have entered wrong old password','flag':flag,'form': form})


    else:
        form = ChangePasswordForm()
    return render(request, 'settings.html',{'form': form})

# class EditView(viewsets.ModelViewSet):
#     queryset = Articles2.objects.all()
#     serializer_class = EditViewSerializer


def RSVPlist(request):
    user_id = request.session.get('userid')
    print(user_id)
    q1=StatusPromotionTicketing.objects.get(connected_user=user_id)
    print(q1)
    q2=Articles2.objects.filter(id=36663)#q1.event_id)
    print(q2)
    rsvp_count={}
    for i in q2:
        rsvp_count[q2.id]=rsvp.objects.filter(event_id=q2.event_id).count()
    return render(request,'RSVP.html',{'entries1':q2},{'rsvp_count':rsvp_count})




class EditView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'edit_list.html'
    def get(self, request):
        queryset = Articles2.objects.all()

        return Response({'Articles': queryset})

class EditDetailView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'edit_detail.html'

    def get_object(self, event_id):
        try:
            return Articles2.objects.get(pk=event_id)
        except Articles2.DoesNotExist:
            raise Http404

    def get(self, request,event_id):
        article = self.get_object(event_id)
        serializer = EditViewSerializer(article)
        tickets = Tickets.objects.all().filter(event_id = event_id)
        print(tickets)




        for x in tickets:
             # y.append(x.values('ticket_name')[0]['ticket_name'])
             # z.append(x.values('ticket_price')[0]['ticket_price'])
             print(x)


        # print(x.values('ticket_name'))

        return Response({'article': article, 'tickets':x})


    # def put(self, request, pk, format=None):
    #     article = self.get_object(pk)
    #     serializer = EditViewSerializer(article, data=request.data)
    #     if not serializer.is_valid():
    #         return Response({'serializer': serializer, 'article': article})
    #     serializer.save()
    #     return redirect('article-list')

    # def delete(self, request, pk, format=None):
    #     article = self.get_object(pk)
    #     article.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
