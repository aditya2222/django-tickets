from django.shortcuts import render, redirect , get_object_or_404, render_to_response
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import authenticate , login , logout
from django.core.mail import send_mail
from django.http import  JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.template import RequestContext, Context, loader
from hashlib import md5
import secrets
import time
import os
import re
from django.core.files.storage import FileSystemStorage
from datetime import datetime
import itertools

from dashboard.models import rsvp,StatusPromotionTicketing,PartnerSites,StatusOnChannel
from django.shortcuts import render_to_response

from .forms import RegistrationForm , UserForm , LoginForm,ForgotPasswordForm , ContactForm ,ResetPassword
from .models import RegistrationData , BlogData , ContactData, Users
from dashboard.models import rsvp,StatusPromotionTicketing, Articles2,Tickets,Tickets_Sale, Admin_Event_Assignment, Admin, StatusOnChannel

from django.utils import timezone

from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.hashers import make_password, check_password
import hashlib 
from .models import UserRegistrationToken
import uuid
from datetime import datetime as dt

email_sent_from = settings.EMAIL_HOST_USER

flag = 0
l = []
email_verify_dict = {}


def send_verification_email(host_url_param,user_id_param, user_email_param, firstname_param, lastname_param):
    try:
        email_token = str(uuid.uuid4()) + str(user_id_param)
        # save token into db
        currentTime = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # UserRegistrationToken.objects.filter(user_email=emailVal)
        user_registration_token_filter_data = UserRegistrationToken.objects.filter(user_email=user_email_param)
        if len(user_registration_token_filter_data) == 0:
            UserRegistrationToken.objects.create(user_email_token=email_token, user_email=user_email_param, user_email_token_created_on=currentTime)
        else:
            UserRegistrationToken.objects.filter(user_email=user_email_param).update(user_email_token=email_token, user_email_token_created_on=currentTime)
        # ends here ~ save token into db

        verify_url = 'http://'+host_url_param+'/live/verify_email/'+email_token+'/'
        # send email
        html_message = loader.render_to_string('static/common/signup_verification.html',
            {
            'firstname': firstname_param,
            'lastname': lastname_param,
            'verify_url':verify_url
            })
        send_mail('Verify Email','message',email_sent_from,[user_email_param],fail_silently=False,html_message=html_message)
        # ends here ~ send email

    except Exception as e:
        print('error is ',e)

@csrf_exempt
def registration(request):
    regerr =False
    pass_no_match = False
    mail_no_match = False
    auth_email_failed = False
    submitted = False
    sec_code = None
    errormail = False
    x =0
    if request.method == 'POST':
        try:
            # read request data
            requestData = request.body
            requestDataDecode = requestData.decode('utf8').replace("'", '"')
            requestDataJson = json.loads(requestDataDecode)
            # ends here ~ read request data

            # set value into variable
            fnameVal = requestDataJson['fnameVal']
            lnameVal = requestDataJson['lnameVal']
            locVal = requestDataJson['locVal']
            emailVal = requestDataJson['emalVal']
            passVal = requestDataJson['passVal']
            print(fnameVal, lnameVal, locVal, emailVal, passVal)
            # ends here ~ set value into variable

            # test code
            # Users.objects.filter().exclude(id=1).delete()
            # UserRegistrationToken.objects.filter(user_email=emailVal).delete()
            # ends here ~ test code

            filterData = Users.objects.filter(user=emailVal)
            if len(filterData) == 0:
                # save values into db
                pswd_encoded = hashlib.md5(passVal.encode('utf-8')).hexdigest()
                email_encoded = hashlib.md5(emailVal.encode('utf-8')).hexdigest()
                new_user = Users(user=emailVal, firstname = fnameVal, lastname = lnameVal, location= locVal,password=pswd_encoded,md5=email_encoded)
                new_user.save()
                # ends here ~ save values into db


                # email_token = str(uuid.uuid4()) + str(new_user.id)

                send_verification_email(request.get_host(), new_user.id, emailVal, fnameVal, lnameVal)
                '''
                html_message = loader.render_to_string('static/common/signup_verification.html',
                     {
                     'firstname': 'firstname_param',
                     'lastname': 'lastname_param',
                     'verify_url':'verify_url'
                     })
                '''
             #   send_mail('subject','message',email_sent_from,['mybooks0101@gmail.com'],fail_silently=False) #,html_message=html_message)
                # # ends here ~ send email

               
                messageData = {'message':'Congratulations! your account is successfully created. Please check your email and follow the instructions.','responseType':'success', 'messageType':'success'}
               

            else:
                
                messageData = {'message':'This account already exists in our record. Try to login.','responseType':'success', 'messageType':'error'}
                

#            messageData = {'as':'as'}
            return HttpResponse(json.dumps(messageData))
        except Exception as e:
            print('error is',e)
            ############### new code ~ Date: 21 april 2019 #############
            # @author Shubham
            # return message 
            messageData = {'message':e,'responseType':'error', 'messageType':'error'}
            return HttpResponse(json.dumps(messageData))
            ################ ends here ~  new code ~ Date: 21 april 2019 #############

    else :
        form1 = UserForm()
        form2 = RegistrationForm()
        if 'regerr' in request.GET:
            regerr = True
        if 'pass_no_match' in request.GET:
            pass_no_match = True
        if 'mail_no_match' in request.GET:
            mail_no_match = True
        if 'submitted' in request.GET:
            submitted = True
        if 'errormail' in request.GET:
            errormail = True
        if 'auth_email_failed' in request.GET:
            auth_email_failed = True
        return render(request , 'registration.html',{'form1':form1 ,
                                                     'form2':form2 ,
                                                     'regerr':regerr,
                                                     'pass_no_match':pass_no_match,
                                                     'mail_no_match':mail_no_match ,
                                                     'errormail':errormail,
                                                     'submitted':submitted ,
                                                     'auth_email_failed':auth_email_failed})



def verify_mail(request, slug):
    try:
        try:
            filterData = UserRegistrationToken.objects.get(user_email_token=slug)
            filterTime = filterData.user_email_token_created_on
        except Exception as e:
            print('verify_email error',e)
            messageData = {'message':'Token is invalid. Please get a new confirmation mail from your dashboard.','responseType':'success', 'token_type':'email'}
            # return HttpResponse(json.dumps(messageData))
            context = {}
            context['messageData']=messageData
            return render(request, 'email_password_template.html', context)

        if (filterTime == ''):
            messageData = {'message':'Token is invalid. Please get a new confirmation mail from your dashboard.','responseType':'success', 'token_type':'email'}
        else:
            tokenCreateTime = filterTime.strftime("%Y-%m-%d %H:%M:%S")
            currentTime = dt.now().strftime("%Y-%m-%d %H:%M:%S")

            fmt = '%Y-%m-%d %H:%M:%S'
            tokenCreateTimeNew = dt.strptime(tokenCreateTime, fmt)
            currentTimeNew = dt.strptime(currentTime, fmt)
            print(tokenCreateTimeNew)
            print(currentTimeNew)
            minutesDifference = currentTimeNew - tokenCreateTimeNew
            diff_minutes = (minutesDifference.days * 24 * 60) + (minutesDifference.seconds/60)
            
            if diff_minutes >= 5:
                messageData = {'message':'Token is invalid. Please get a new confirmation mail from your dashboard.','responseType':'success', 'token_type':'email'}
                # if (filterData.user_password_token == ''):
                #     UserRegistrationToken.objects.filter(user_email=filterData.user_email).delete()
                # else:
                #     UserRegistrationToken.objects.filter(user_email=filterData.user_email).update(user_email_token='',user_email_token_created_on='')
            else:
                Users.objects.filter(user=filterData.user_email).update(status='active')
                filterUserTable = Users.objects.get(user=filterData.user_email)
                if (filterData.user_password_token == ''):
                    UserRegistrationToken.objects.filter(user_email=filterData.user_email).delete()
                else:
                    UserRegistrationToken.objects.filter(user_email=filterData.user_email).update(user_email_token='',user_email_token_created_on='')
                html_message = loader.render_to_string('static/common/welcome_email_template.html', {
                    'firstname': filterUserTable.firstname,
                    'lastname': filterUserTable.lastname,
                })

                # send welcome template
                send_mail('Welcome to Ercess','message',email_sent_from,[filterData.user_email],fail_silently=False,html_message=html_message)
                messageData = {'message':'We were successful to verify your email address. You can proceed with login now.','responseType':'success', 'token_type':'email'}
                # ends here ~ send welcome template
        
        # return HttpResponse(json.dumps(messageData))
        context = {}
        context['messageData']=messageData
        return render(request, 'email_password_template.html', context)
    except Exception as e:
        print('error is ',e)
        messageData = {'message':'Something went wrong. Please try again.','responseType':'error', 'token_type':'email'}
        context = {}
        context['messageData']=messageData
        return render(request, 'email_password_template.html', context)
'''
def registration(request):
    print('in view')
    regerr =False
    pass_no_match = False
    mail_no_match = False
    auth_email_failed = False
    submitted = False
    sec_code = None
    errormail = False
    x =0
    if request.method == 'POST':
        form1  = UserForm(request.POST)
        form2 = RegistrationForm(request.POST)
        if form1.is_valid() and form2.is_valid() :
            print('after validation')
            firstname = request.POST.get('firstname','')
            lastname = request.POST.get('lastname','')
            email = request.POST.get('email','')
            cemail = request.POST.get('confirmmail','')
            password = request.POST.get('password','')
            re_enter_password = request.POST.get('reenter_password','')

            # print(firstname, lastname , email ,cemail ,password , re_enter_password)
            if email != cemail :
                return redirect('/live/signup?mail_no_match=True')
            if password!= re_enter_password :
                return redirect('/live/signup?pass_no_match=True')

            data = User.objects.filter(email=email)
            print(data)
            if not data :
                try:
                    user = User.objects.create_user(username=email ,
                                                    first_name = firstname ,
                                                    last_name = lastname ,
                                                    email=email ,
                                                    password=password)
                    user.save()
                    u = authenticate(username=email, password=password , email=email)

                    # print('before auth save')
                    print(u.save())
                    # print('after auth save')
                    # mobile = request.POST.get('mobile','')
                    gender = request.POST.get('gender', '')
                    location = request.POST.get('location', '')
                    reg = RegistrationData(
                        user=user,
                        gender= gender,
                        location= location
                    )
                    x = reg.save()
                    pswd_encoded = md5(password.encode('utf-8')).hexdigest()
                    new_user = Users(user=email, firstname = firstname,
                                     lastname = lastname, password=pswd_encoded,
                                     gender= gender, location= location)

                    new_user.save()
                except Exception as e:
                    print('exception in register')
                    print(e)
                    return redirect('/live/signup?regerr=True')
            else:
                return redirect('/live/signup?regerr=True')
            if x is not None:
                return redirect('/live/signup?regerr=True')
            else :
                try:
                    sec_code = get_sec_code()
                    print('-------------')
                    print(sec_code)
                    res = send_mail('Verify email', 'http://127.0.0.1:8000/live/verify_email/?email='+email+'&token='+sec_code + '\n\n\n' + 'verify your email !!!',
                                    'no-reply@ercess.com', [email, ])
                except Exception as e:
                    #print(res)
                    print(e)
                    return redirect('/live/signup?errormail=True')
                else:
                    # add email and seccode to dict
                    set_key_email(email, sec_code)
                    return redirect('/live/signup?submitted=True')
        form1 = UserForm()
        form2 = RegistrationForm()
        return render(request, 'registration.html', {'form1': form1, 'form2': form2})
    else :
        form1 = UserForm()
        form2 = RegistrationForm()
        if 'regerr' in request.GET:
            regerr = True
        if 'pass_no_match' in request.GET:
            pass_no_match = True
        if 'mail_no_match' in request.GET:
            mail_no_match = True
        if 'submitted' in request.GET:
            submitted = True
        if 'errormail' in request.GET:
            errormail = True
        if 'auth_email_failed' in request.GET:
            auth_email_failed = True
        return render(request , 'registration.html',{'form1':form1 ,
                                                     'form2':form2 ,
                                                     'regerr':regerr,
                                                     'pass_no_match':pass_no_match,
                                                     'mail_no_match':mail_no_match ,
                                                     'errormail':errormail,
                                                     'submitted':submitted ,
                                                     'auth_email_failed':auth_email_failed})

'''
def set_key_email(email, sec_code):
    key1 = str(email)
    key2 = key1+'sc'
    email_verify_dict[key1] = email
    email_verify_dict[key2] = sec_code
'''
def verify_mail(request):
    if request.method == 'GET':
        if 'token' in request.GET:
            token = request.GET.get('token', '')
        if 'email' in request.GET:
            email = request.GET.get('email', '')

        key1 = str(email)
        key2 = key1 + 'sc'

        if key1 in email_verify_dict and key2 in email_verify_dict:
            print('exist')
            #set value 1 in db and redirect to login
            u = User.objects.get(email=email)
            print(u)
            r = RegistrationData.objects.get(user_id=u.pk)
            r.verify = 1
            r.save()

            print('pop out keys')

            print(email_verify_dict.pop(key1))
            print(email_verify_dict.pop(key2))

            return  redirect('/live/login?verified=True')
        else:
            print('no')
            #show error that authentication failed
            return redirect('/live/signup?auth_email_failed=True')

'''

@csrf_exempt
def loginview(request):
    loginerror = False
    error = False
    verify_error = False
    verified = False
    mail = False
    contact =False
    submitted = False
    passchange = False
    if request.method == 'POST':
        requestData = request.body
        requestDataDecode = requestData.decode('utf8').replace("'", '"')
        requestDataJson = json.loads(requestDataDecode)

        email = requestDataJson['emalVal']
        password = requestDataJson['passVal']
   
        
        
        print('after login form validation')
            
        pswd_encoded = md5(password.encode('utf-8')).hexdigest()
            
        if Users.objects.filter(user=email).exists():
               
            if Users.objects.filter(user=email, password=pswd_encoded).exists():

                    u = Users.objects.get(user=email)
                
                    #status = u.status
                    #if status=='active':
                    request.session['username'] = email
                    request.session['userid'] = u.id
                    request.session['firstname'] = u.firstname
                    request.session['lastname'] = u.lastname
                       
                    request.session.modified = True
                       # us = authenticate(username=email, password=password)
                        #if us:
                         #   next_url = request.GET.get('next')
                          #  print(next_url)
                           # if next_url:
                    print(request)
                    print(request.session.keys())
                    messageData = {'url':'/live/dashboard/add-event','responseType':'success', 'messageType':'success'}
                    return HttpResponse(json.dumps(messageData))
                        #return HttpResponseRedirect('/live/dashboard/add-event')
                        #return redirect('dashboard:step_one')
                            #else:
                             #   return redirect('dashboard:how')
                    #else :
                     #   messageData = {'message':'Verify your email','responseType':'success', 'messageType':'success'}
                      #  return HttpResponse(json.dumps(messageData))
                        #return redirect('/live/login?verify_error=True')
            else :
                messageData = {'message':'Invalid details provided','responseType':'success', 'messageType':'error'}
                return HttpResponse(json.dumps(messageData))
                    #return redirect('/live/login?error=True')
        else:
            messageData = {'message':'Oops! this user does not exist in our record.','responseType':'success', 'messageType':'error'}
            return HttpResponse(json.dumps(messageData))
       # print('checkkkkkk----------------------------------------------')
       # print(form.errors)
        #form = LoginForm()
        #return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
        if 'loginerror' in request.GET:
            loginerror = True
        if 'error' in request.GET:
            error = True
        if 'mail' in request.GET:
            mail = True
        if 'contact' in request.GET:
            contact = True
        if 'submitted' in request.GET:
            submitted = True
        if 'passchange' in request.GET:
            passchange = True
        if 'verify_error' in request.GET:
            verify_error = True
        if 'verified' in request.GET:
            verified = True
        return render(request, 'login.html', {'form': form ,'loginerror':loginerror,'error':error ,
                                              'mail':mail ,'contact':contact ,
                                              'submitted':submitted ,'passchange':passchange,
                                              'verify_error':verify_error,
                                              'verified':verified})
'''
def loginview(request):
    error = False
    verify_error = False
    verified = False
    mail = False
    contact =False
    submitted = False
    passchange = False
    if request.method == 'POST':
        form = LoginForm(request.POST)
        print('before validation')
        if form.is_valid():
            print('after validation')
            email = request.POST.get('email' ,'')
            password = request.POST.get('password', '')
            # print(username)
            # print(password)
            user = authenticate(username = email , password = password)
            # print('user in login view')
            print('user')
            print(user)
            if user :

                u = User.objects.get(email=email)
                print(u)
                r = RegistrationData.objects.get(user_id= u.pk )
                print('in views of ercess corp')
                verify = r.verify
                if verify:
                    print(r.submitted)
                    request.session['sub'] = r.submitted
                    print(request.session['sub'])
                    request.session['username'] = email
                    login(request, user)
                    return redirect('dashboard:how')
                else :
                    return redirect('/live/login?verify_error=True')
            else :
                return redirect('/live/login?error=True')
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
        if 'error' in request.GET:
            error = True
        if 'mail' in request.GET:
            mail = True
        if 'contact' in request.GET:
            contact = True
        if 'submitted' in request.GET:
            submitted = True
        if 'passchange' in request.GET:
            passchange = True
        if 'verify_error' in request.GET:
            verify_error = True
        if 'verified' in request.GET:
            verified = True
        return render(request, 'login.html', {'form': form ,'error':error ,
                                              'mail':mail ,'contact':contact ,
                                              'submitted':submitted ,'passchange':passchange,
                                              'verify_error':verify_error,
                                              'verified':verified})
'''
@csrf_exempt
def forgotPassword(request):
    try:
        errormail = False
        usernotexist = False
        res = 0
        if request.method == 'POST':
            try:
                # read request data
                requestData = request.body
                print('requestData',requestData)
                requestDataDecode = requestData.decode('utf8').replace("'", '"')
                requestDataJson = json.loads(requestDataDecode)
                # ends here ~ read request data

                # set value into variable
                emailVal = requestDataJson['emalVal']
                # ends here ~ set value into variable

                filterData = Users.objects.filter(user=emailVal)
                if len(filterData) == 0:
                    messageData = {'message':'Oops! this user does not exist in our record.','responseType':'success', 'messageType':'error'}
                else:
                    filterUserData = Users.objects.get(user=emailVal)
                    password_token = str(uuid.uuid4()) + str(filterUserData.id)
                    
                    # save token into db
                    currentTime = dt.now().strftime("%Y-%m-%d %H:%M:%S")
                    user_registration_token_filter_data = UserRegistrationToken.objects.filter(user_email=emailVal)
                    if len(user_registration_token_filter_data) == 0:
                        UserRegistrationToken.objects.create(user_password_token=password_token, user_email=emailVal, user_password_token_created_on=currentTime)
                    else:
                        UserRegistrationToken.objects.filter(user_email=emailVal).update(user_password_token=password_token, user_password_token_created_on=currentTime)
                    # ends here ~ save token into db

                    verify_url = 'http://'+request.get_host()+'/live/reset_password/'+password_token+'/'
                    # send email
                    html_message = loader.render_to_string('static/common/forget_password_template.html',
                        {
                        'verify_url':verify_url
                        })
                    print('emailVal',emailVal)
                    print('email_sent_from',email_sent_from)
                    send_mail('Reset Password - Ercess','message',email_sent_from,[emailVal],fail_silently=False,html_message=html_message)
                    # ends here ~ send email

                    messageData = {'message':'Please check your email to reset password.','responseType':'success', 'messageType':'success'}

                return HttpResponse(json.dumps(messageData))

            except Exception as e:
                print('error is', e)
        else:
            form = ForgotPasswordForm()
            if 'errormail' in request.GET:
                errormail = True
            if 'usernotexist' in request.GET:
                usernotexist = True
            return render(request, 'fogotpassword.html', {'form': form ,'errormail':errormail ,'usernotexist':usernotexist})
    except Exception as e:
        print('error is ', e)


@csrf_exempt
def setNewPassword(request):
    try:
        # read request data
        requestData = request.body
        requestDataDecode = requestData.decode('utf8').replace("'", '"')
        requestDataJson = json.loads(requestDataDecode)
        # ends here ~ read request data

        print(requestDataJson)
        # get all required values
        slugValue = requestDataJson['slugVal']
        passwordValue = requestDataJson['passVal']
        # ends here ~ get all required values

        # code for changed password
        try:
            filterData = UserRegistrationToken.objects.get(user_password_token=slugValue)
            pswd_encoded = hashlib.md5(passwordValue.encode('utf-8')).hexdigest()
            Users.objects.filter(user=filterData.user_email).update(password=pswd_encoded)
            # ends here ~ code for changed password

            if (filterData.user_email_token == ''):
                UserRegistrationToken.objects.filter(user_email=filterData.user_email).delete()
            else:
                UserRegistrationToken.objects.filter(user_email=filterData.user_email).update(user_password_token='',user_password_token_created_on='')
            messageData = {'url': '/live/login/','message':'Your password was reset successfully.','responseType':'success', 'token_type':'password','messageType':'success'}
            return HttpResponse(json.dumps(messageData))
        except Exception as e:
            messageData = {'message':'Token is already used to reset your password.','responseType':'success', 'token_type':'password','messageType':'error'}
            return HttpResponse(json.dumps(messageData))


    except Exception as e:
        raise


def resetPassword(request, slug):
    try:
        usernotexist = False
        passnotmatch = False
        if request.method == 'POST':
            pass
            # # read request data
            # requestData = request.body
            # requestDataDecode = requestData.decode('utf8').replace("'", '"')
            # requestDataJson = json.loads(requestDataDecode)
            # # ends here ~ read request data

            # print(requestDataJson)

        else:
            try:
                filterData = UserRegistrationToken.objects.get(user_password_token=slug)
                filterTime = filterData.user_password_token_created_on
            except Exception as e:
                messageData = {'message':'Your token is expired. Please try again.','responseType':'success', 'token_type':'password', 'messageType':'error'}
                context = {}
                context['messageData']=messageData
                return render(request, 'resetpassword.html', context)

            if (filterTime == ''):
                messageData = {'message':'Your token is expired. Please try again.','responseType':'success', 'token_type':'password','messageType':'error'}
            else:
                tokenCreateTime = filterTime.strftime("%Y-%m-%d %H:%M:%S")
                currentTime = dt.now().strftime("%Y-%m-%d %H:%M:%S")

                fmt = '%Y-%m-%d %H:%M:%S'
                tokenCreateTimeNew = dt.strptime(tokenCreateTime, fmt)
                currentTimeNew = dt.strptime(currentTime, fmt)

                minutesDifference = currentTimeNew - tokenCreateTimeNew
                diff_minutes = (minutesDifference.days * 24 * 60) + (minutesDifference.seconds/60)
                
                if diff_minutes >= 2880:
                    messageData = {'message':'Your token is expired. Please try again.','responseType':'success', 'token_type':'password','messageType':'error'}
                else:
                    messageData = {'message':'Your toke to reset password is valid.','responseType':'success', 'token_type':'password','messageType':'success','email':filterData.user_email}
                # return HttpResponse(json.dumps(messageData))
                context = {}
                context['messageData']=messageData
                return render(request, 'resetpassword.html', context)
                # form = ResetPassword()
                # return render(request, 'resetpassword.html',
                #                   {'form': form})
    except Exception as e:
        print('error is ',e)


'''
def forgotPassword(request):
    errormail = False
    usernotexist = False
    res = 0
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email','')
            # print(email)
            try :
                u = User.objects.get(email=email)
            except :
                return redirect('/live/forgot_password?usernotexist=True')
            if  u :
                try:
                    res = send_mail('Change your password', 'http://127.0.0.1:8000/live/reset_password/?token='+get_sec_code() + '\n\n\n' + 'change your password within 5 minutes !!!', 'no-reply@ercess.com', [email,])
                    clear_list()
                except Exception as e:
                    print(res)
                    print(e)
                    pass
                if res  == 1:
                    # give submission message to user
                    return redirect('/live/login?mail=True')
                else :
                    # give error to user
                    return redirect('/live/forgot_password?errormail=True')

            else :
                #raise user doesnot exist
                return redirect('/live/forgot_password?usernotexist=True')
        form = ForgotPasswordForm()
        return render(request, 'fogotpassword.html', {'form': form})
    else:
        form = ForgotPasswordForm()
        if 'errormail' in request.GET:
            errormail = True
        if 'usernotexist' in request.GET:
            usernotexist = True
        return render(request, 'fogotpassword.html', {'form': form ,'errormail':errormail ,'usernotexist':usernotexist})

def resetPassword(request):
    usernotexist = False
    passnotmatch = False
    if request.method == 'POST':
        form = ResetPassword(request.POST)
        if form.is_valid():
            email = request.POST.get('email', '')
            password = request.POST.get('password','')
            rpassword = request.POST.get('rpassword', '')
            try:
                u = User.objects.get(email=email)
            except :
                return redirect('/live/reset_password?usernotexist=True')
            if  u :
                if password == rpassword :
                    u.set_password(password)
                    u.save()
                    return redirect('/live/login?passchange=True')
                else :
                    #raiseerror password not matching
                    return redirect('/live/reset_password?passnotmatch=True')
            else :
                #raise user does not exist
                return redirect('/live/reset_password?usernotexist=True')
        form = ResetPassword()
        return render(request, 'resetpassword.html', {'form': form})
    else:
        form = ResetPassword()

        if 'usernotexist' in request.GET:
            usernotexist = True
        if 'passnotmatch' in request.GET:
            passnotmatch = True
        if 'token' in request.GET:
            token = request.GET.get('token', '')
            res = check_token(token)
            print(res)
            if res == 1 :
                return render(request, 'resetpassword.html',
                              {'form': form, 'usernotexist': usernotexist, 'passnotmatch': passnotmatch})
            elif res == 0 :
                return render(request , 'request_timeout.html')
        else :
            return render(request, '403.html')
        return render(request, 'resetpassword.html',
                      {'form': form, 'usernotexist': usernotexist, 'passnotmatch': passnotmatch})
'''
def home(request):
    try:

        try:
            print('trying to delete session data', request.session.get('username'))
            del request.session['username']
            request.session.modified = True
        except Exception as e:
            print(e)
        try :
            print('trying to delete session  sub data', request.session.get('sub'))
            del request.session['sub']
            request.session.modified = True
        except Exception as e:
            print(e)
        try:
            logout(request)
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
    return render(request, 'index.html')

def multichannelpromotion(request):
    # print('multichannel promotion')
    return  render(request , 'multichannel_promotion.html')

def sellstallspaces(request):
    return  render(request , 'stall_spaces.html')

def advertisement(request):
    return  render(request , 'paid-advertisement.html')

def howitworks(request):
    # print('inside how it works')
    return render(request , 'how-it-works.html')
#
# def createevent(request):
#     pass
#
#
# def manageevents(request):
#     pass
#
#
# def salesreport(request):
#     pass
def aboutus(request):
    return  render(request, 'about-us.html')

def contactus(request):
    res = 0
    x = 0
    send_to = 'no-reply@ercess.com'
    contactregerror = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name  = form.cleaned_data.get('name','')
            email = form.cleaned_data.get('email', '')
            mobile= form.cleaned_data.get('mobile', '')
            purpose =form.cleaned_data.get('purpose','')
            comment = form.cleaned_data.get('comment','')
            try:
                res = send_mail('Customer Query', 'contact details of customer' + 'name : ' + name + 'email : '+ email + 'phone no :' + str(mobile)
                                + 'purpose :'+purpose + 'comments :'+comment, email, [email, ])


                con = ContactData(
                    username=name,
                    email=email,
                    mobile=mobile,
                    purpose=purpose,
                    comment=comment
                )

                x = con.save()



            except Exception as e:
                print(e)

            if res == 1 and x is None:
                # give submission message to user
                return redirect('/live/login?contact=True')
            else:
                # give error to user
                return redirect('/live/contact?contactregerror=True')
        form = ForgotPasswordForm()
        return render(request, 'contact-us.html', {'form': form})
    else:
        form = ContactForm()
        if 'contactregerror' in request.GET:
            contactregerror = True
        return render(request, 'contact-us.html', {'form': form, 'contactregerror': contactregerror})

def blog(request):
    data = BlogData.objects.all()
    return  render(request, 'blog.html' ,{'data':data[0] ,'desc':data[0].description[0:300]})

def blogpost(request,pk):

    data = BlogData.objects.get(pk=pk)
    return  render(request, 'blog-post.html' ,{'data':data })

def career(request):
    return  render(request,'careers.html')


def pricing(request):
    return  render(request, 'pricing.html')


def partners(request):
    return  render(request, 'partners.html')


def marketing(request):
    pass


def privacypolicy(request):
    return  render(request, 'privacy-policy.html')


def logoutview(request):

    try :
        #logout(request)
        print('trying to delete session data' ,request.session.get('username'))
        for key in list(request.session.keys()):
            del request.session[key]
        #del request.session['username']
        #del request.session['sub']
        #print('data deleted')
        #print('auth logging out')


    except :
        print('unable to delete')

    if not request.session.get('username'):

        return  redirect('/live/')


def blogdetails(request):
    blogs =  BlogData.objects.all()
    data  = {"results":list(blogs.values('blog_id','title','author' ,'date' ,'description' ))}
    return  JsonResponse(data)


def blogspecific(request, pk):
    blog = get_object_or_404(BlogData , pk=pk)
    data = {
        "results":{
            'blog_id':blog.blog_id,
            'title':blog.title,
            'author':blog.author,
            'date':blog.date,
            'description':blog.description
        }
    }
    return  JsonResponse(data)


def bad_request(request):
    response = render_to_response( '400.html')
    response.status_code = 400
    return response

def permission_denied(request):
    response = render_to_response('403.html')
    response.status_code = 403
    return response


def page_not_found(request):
    response = render_to_response('404.html')
    response.status_code = 404
    return response

def server_error(request):
    response = render_to_response('500.html')
    response.status_code = 500
    return response

def get_sec_code():
    sc = secrets.token_hex(16)
    l.append(sc)
    print(l)
    return sc


def check_token(token):
    flag = 0
    print('token'+token)
    print('list'+str(l))
    for scc in l:
        print(scc)
        if scc == token:
            flag = 1
    if flag == 1 :
        return 1
    else :
        return 0


def clear_list():
    timeout = time.time() + 60*5
    while True :
        if time.time() > timeout:
            l.clear()
            break

def manageevents(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    e=[]
    r =request.session.get('userid')
    print(r)
    l=StatusPromotionTicketing.objects.all().filter(connected_user=r,complete_details=1).values('event_id').order_by('-event_id')
    d=StatusPromotionTicketing.objects.all().filter(connected_user=r,complete_details=0).values('event_id').order_by('-event_id')
    now = datetime.now(tz=timezone.utc)
    print(l,d)
    tot_count =[ len(l) + len(d)]
    print(tot_count)
    pr=[]
    up=[]
    pn=[]
    un=[]
    psd=[]
    usd=[]
    u_src=[]
    p_src=[]
    d_src=[]
    pc=0
    uc=0
    for i in range(0,(len(l))):
        print(i)
        p = Articles2.objects.all().filter(edate__lt=now,id=l[i]['event_id'])
        u = Articles2.objects.all().filter(edate__gt=now,id=l[i]['event_id'])
        if len(p)!=0:
            pr.append(p.values('id')[0]['id'])
            pn.append(p.values('event_name')[0]['event_name'])
            psd.append(p.values('sdate')[0]['sdate'])
            p_src.append(p.values('banner')[0]['banner'])
            
        elif len(u)!=0:
            up.append(u.values('id')[0]['id'])
            un.append(u.values('event_name')[0]['event_name'])
            usd.append(u.values('sdate')[0]['sdate'])
            u_src.append(u.values('banner')[0]['banner'])
    stat=[]
    for i in up:
        #print(i)
        st =  StatusPromotionTicketing.objects.all().filter(event_id=i)    
        #print(st) 
        if len(st)!=0:  
            stat.append(st.values('event_active')[0]['event_active'])

    print(stat)

    #admin_mobile
    admin_mobile=[]
    
    for i in range(0,len(up)):
        # print("---------")
        # print(stat)
        # print(up[i])
        if stat[i]==5:
            a_m=Admin_Event_Assignment.objects.all().filter(event_id=up[i])
            # print(a_m)
            if len(a_m)!=0:
                t_id = (a_m.values('table_id')[0]['table_id'])
                # print(t_id)
                ad_m=Admin.objects.all().filter(table_id=t_id)
                if len(ad_m)!=0:
                    admin_mobile.append(ad_m.values('mobile')[0]['mobile'])
                else:
                    admin_mobile.append('9886188705')
                    # print('nested else')
            else:
                admin_mobile.append('9886188705')
                # print("in this")

    
    
    # for i in t_id:
    #     ad_m=Admin.objects.all().filter(table_id=i)
    #     if len(ad_m)!=0:
    #         admin_mobile.append(ad_m.values('mobile')[0]['mobile'])
    #     else:
    #         admin_mobile.append('9886188705')
    print(admin_mobile)
    print("-------------")
    print(up)
    print(un)
    print(usd)
    print(stat)
    print(u_src)
    upcm = itertools.zip_longest(up,un,usd,stat,admin_mobile,u_src)
#    upcm = zip(up,un,usd,stat,admin_mobile,u_src) 
#    print("UPCNM",list(upcm))
    upcm_count=[len(up)]
    # for previous meetings
    qy=[]
    qk=[]
    
    for k in pr:
        q = Tickets_Sale.objects.all().filter(event_id=k).values('table_id')
        for h in q:
            qy
            qk.append(h['table_id'])
        qy.append(qk)
    qty = [] 
    qt =[]       
    for i in qy:
        for t in i:
            qty_l = Tickets_Sale.objects.all().filter(table_id=t).values('qty')
            qt.append(qty_l[0]['qty'])
        qty.append(qt)
    
    val=0
    value = []
    for i in qty:
        for t in i:
            val=val+t
        value.append(val)

    int_c=[]
    for k in pr:
        ct = rsvp.objects.all().filter(event_id=k).values('table_id').count()
        int_c.append(ct)

    prev = zip(pr,pn,psd,value,int_c,p_src)
    prev_count=[len(pr)]

    #draft
    d_id=[]
    d_n=[]
    d_sd=[]
    draft_count=[len(d)]
    #print(d)
    for i in d:
        #print(i)
        dr = Articles2.objects.all().filter(id=i['event_id'])
        #print(dr)
        if len(dr)!=0:
            d_id.append(dr.values('id')[0]['id'])
            d_n.append(dr.values('event_name')[0]['event_name'])
            d_sd.append(dr.values('sdate')[0]['sdate'])
            d_src.append(dr.values('banner')[0]['banner'])

    #print(d_id)
    draft=zip(d_id,d_n,d_sd,d_src)
    print(tot_count,upcm_count,prev_count,draft_count)
    count=zip(tot_count,upcm_count,prev_count,draft_count)


    


    return render(request, 'dashboard/organizer_dashboard.html',{'prev': prev,'upcm': upcm,'draft': draft,'count':count})

def RSVP(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    entries = rsvp.objects.all()[:7]
    entries1 = Articles2.objects.all()
    entries2 = StatusPromotionTicketing.objects.all()
    #print(entries)
    count = 0
    a=rsvp.objects.values('event_id')
    b=Articles2.objects.values('id')
    for i in range(len(b)):
        if a == b:
            count=count+1
    print(count)
    
    return render_to_response('dashboard/RSVP.html',{'entries': entries,'entries1': entries1,'entries2': entries2,}, RequestContext(request))


def getInquiries(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    return render(request, 'dashboard/inquiries.html')


def getSales(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    user = request.session.get('userid')

    ticketing = StatusPromotionTicketing.objects.all().filter(connected_user= 104,complete_details=0).exclude().values('event_id')
    print(ticketing)
    count_t = len(ticketing)
    now = datetime.now()

    # upcoming tab
    up_id = []
    up_sdate = []
    up_name = []
    up_ban = []
    up_city = []

    # past_tab
    pa_id = []
    pa_sdate = []
    pa_name = []
    pa_ban = []
    pa_city = []

    for i in range(0, count_t):
        up_eve = Articles2.objects.filter(sdate__gt=now, id=ticketing[i]['event_id']).all() | Articles2.objects.filter(
            edate__gt=now, id=ticketing[i]['event_id']).all()

        pa_eve = Articles2.objects.filter(edate__lt=now, id=ticketing[i]['event_id']).all()

        if len(up_eve) != 0:
            up_id.append(up_eve.values('id')[0]['id'])
            up_sdate.append(up_eve.values('sdate')[0]['sdate'])
            up_name.append(up_eve.values('event_name')[0]['event_name'])
            up_ban.append(up_eve.values('banner')[0]['banner'])
            up_city.append(up_eve.values('city')[0]['city'])


        elif len(pa_eve) != 0:
            pa_id.append(pa_eve.values('id')[0]['id'])
            pa_sdate.append(pa_eve.values('sdate')[0]['sdate'])
            pa_name.append(pa_eve.values('event_name')[0]['event_name'])
            pa_ban.append(pa_eve.values('banner')[0]['banner'])
            pa_city.append(pa_eve.values('city')[0]['city'])

    # count of ticket sale upcoming events
    up_sale = []

    print(up_id)
    for i in up_id:
        sale = Tickets_Sale.objects.all().filter(event_id=i).values('qty')

        u_s = 0
        print(sale)

        if len(sale) != 0:
            for i in sale:
                print(i)
                qty=i['qty']
                u_s += qty
            up_sale.append(u_s)
        elif len(sale) == 0:
            up_sale.append(0)
    print(up_sale)

    # count of ticket sale past events
    pa_sale = []

    for i in pa_id:
        sale = Tickets_Sale.objects.all().filter(event_id=i).values('qty')
        p_s = 0

        if len(sale) != 0:
            for i in sale:
                qty = i['qty']
                p_s += qty
            pa_sale.append(p_s)
        elif len(sale) == 0:
            pa_sale.append(0)
    print(pa_sale)

    upcoming = zip(up_id, up_name, up_sdate, up_ban, up_city, up_sale)
    up_count = len(up_id)

    past = zip(pa_id, pa_name, pa_sdate, pa_ban, pa_city, pa_sale)
    pa_count = len(pa_id)

    total_count = up_count + pa_count

    return render(request, 'dashboard/sales.html', {'upcoming': upcoming, 'up_count': up_count,
                                                    'past': past, 'pa_count': pa_count ,
                                                    't_count':total_count})





def getHelp(request):
    return render(request, 'dashboard/help.html')

def profile(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    user = Users.objects.get(pk= request.session['userid'])
    print(user)
    # print(id)
    # user = Users.objects.all().filter(id = id)
    # print(user)
    # , {'user_info': user}
    return render(request, 'dashboard/profile.html', {'user': user})



def settings(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    return render(request, 'dashboard/settings.html')

def rsvp_event(request, event_id):
    return render(request, 'dashboard/rsvp_event.html')

def event_details(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    print(event_id)
    data=[]
    e =Articles2.objects.all().filter(id=event_id)
    eve_id= e.values('id')[0]['id']
    name = [e.values('event_name')[0]['event_name']]
    
    img = [e.values('banner')[0]['banner']]

    #for complete details check
    print(e.values('id')[0]['id'])
    status_check = StatusPromotionTicketing.objects.filter(event_id=e.values('id')[0]['id']).values('complete_details')
    print(status_check)
    print(status_check[0]['complete_details'])
    status = False
    if status_check[0]['complete_details']==1:
        status=True

    
    #for sale
    name_s=[]
    amt=[]
    qty=[]
    e_s = Tickets_Sale.objects.all().filter(event_id=event_id).order_by('-purchase_date').values('table_id')
    c_s = [len(e_s)]

    for i in range(0,len(e_s)):
        
        if i < 3:
            d = Tickets_Sale.objects.all().filter(table_id=e_s[i]['table_id'])
            name.append(d.values('attendee_name')[0]['attendee_name'])
            amt.append(d.values('ampunt_paid')[0]['ampunt_paid'])
            qty.append(d.values('qty')[0]['qty'])
        
    sale=zip(name,amt,qty)


    #for rsvp
    name_r=[]
    cont=[]
    email=[]
    e_r = rsvp.objects.all().filter(event_id=event_id).order_by('-date_added').values('table_id')
    for i in range(0,len(e_r)):
        if i < 3:
            d = rsvp.objects.all().filter(table_id=e_r[i]['table_id'])
            name_r.append(d.values('attendee_name')[0]['attendee_name'])
            cont.append(d.values('attendee_contact')[0]['attendee_contact'])
            email.append(d.values('attendee_email')[0]['attendee_email'])
        
    rsvp_d=zip(name_r,cont,email)
    c_r = [len(e_r)]
    
    
    data=zip(name,img,c_s,c_r)

    #for site
    s_n=[]
    c_l=[]
    c_ps=[]
    c_p=[]


    s = StatusOnChannel.objects.all().filter(event_id=event_id).values('table_id')
    s_len= len(s)
    print(s)
    for i in s:
        d = StatusOnChannel.objects.all().filter(table_id=i['table_id'])
        s_i = PartnerSites.objects.all().filter(table_id=(d.values('site_id')[0]['site_id']))
        s_n.append(s_i.values('site_name')[0]['site_name'])
        c_l.append(d.values('link')[0]['link'])
        c_ps.append(d.values('promotion_status')[0]['promotion_status'])
        c_p.append(d.values('partner_status')[0]['partner_status'])

    print(c_l)
    site=zip(s_n,c_l,c_ps,c_p)

    return render(request, 'dashboard/event_details.html',{'data': data,'sale':sale,
                                                           'rsvp':rsvp_d,'site':site,
                                                           'status':status,'s_len':s_len,
                                                           'eve_id':eve_id})

def legal(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')


    return render(request, 'dashboard/legal.html')

	
def edit_event(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    
    s=[]
    d = Articles2.objects.all().filter(id=event_id)
    s.append(d.values('event_name')[0]['event_name'])
    s.append(d.values('sdate')[0]['sdate'])
    s.append(d.values('start_time')[0]['start_time'])
    s.append(d.values('edate')[0]['edate'])
    s.append(d.values('end_time')[0]['end_time'])
    s.append(d.values('address_line1')[0]['address_line1'])
    s.append(d.values('address_line2')[0]['address_line2'])
    s.append(d.values('city')[0]['city'])
    s.append(d.values('state')[0]['state'])
    s.append(d.values('country')[0]['country'])
    s.append(d.values('pincode')[0]['pincode'])
    



    return render(request, 'dashboard/edit_event.html',{'event_id':event_id,'s':s,})

def edit_action_one(request, event_id):
    
    print(event_id)
    event_name=request.POST.get('event_name','')
    sdate=request.POST.get('sdate','')
    start_time=request.POST.get('start_time','')
    edate=request.POST.get('edate','')
    end_time=request.POST.get('end_time','')
    address_line1=request.POST.get('address_line1','')
    address_line2=request.POST.get('address_line2','')
    city=request.POST.get('city','')
    state=request.POST.get('state','')
    country=request.POST.get('country','')
    pincode=request.POST.get('pincode','')
    
    s_u=Articles2(id=event_id,event_name=event_name,address_line1=address_line1,address_line2=address_line2,city=city,state=state,country=country)
    print(s_u)
    s_u.save()

    #sdate=sdate,start_time=start_time,edate=edate,end_time=end_time,
    # s=[]
    # d = Articles2.objects.all().filter(id=event_id)
    # s.append(d.values('event_name')[0]['event_name'])
    # s.append(d.values('sdate')[0]['sdate'])
    # s.append(d.values('start_time')[0]['start_time'])
    # s.append(d.values('edate')[0]['edate'])
    # s.append(d.values('end_time')[0]['end_time'])
    # s.append(d.values('address_line1')[0]['address_line1'])
    # s.append(d.values('address_line2')[0]['address_line2'])
    # s.append(d.values('city')[0]['city'])
    # s.append(d.values('state')[0]['state'])
    # s.append(d.values('country')[0]['country'])
    # s.append(d.values('pincode')[0]['pincode'])


    return HttpResponseRedirect(reverse('dashboard:edit-event-two', args=(event_id,)))

def edit_event_two(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    
    
    return render(request, 'dashboard/edit_event_two.html',{'event_id':event_id,})


def edit_action_two(request, event_id):
    
    print(event_id)

    return HttpResponseRedirect(reverse('dashboard:edit-event-four', args=(event_id,)))

def edit_event_four(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    
    
    return render(request, 'dashboard/edit_event_four.html',{'event_id':event_id,})

def edit_action_four(request, event_id):
    
    print(event_id)

    return HttpResponseRedirect(reverse('dashboard:edit-event-four', args=(event_id,)))


def step_three(request, md5, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    
    return render(request, 'dashboard/create-event/step_3/step_three_temp.html',{'event_id':event_id, 'md5':md5}) 


def step_three_action(request, md5, event_id):
    
    print('request includes'+str(request.FILES.get('myfile')))
    myfile=request.POST.get('myfile', None)
    articles2 = Articles2.objects.get(id = event_id)
    # event_name = re.sub('[^A-Za-z0-9 ]+', '',articles2.event_name)
    event_name = articles2.event_name
    event_name = event_name.replace(' ','-')
    image_name = event_name +'-'+str(event_id)
    print('event id is '+ str(event_id))
    uploadedfileurl=''

    if request.method=='POST' and request.FILES.get('myfile', None):
        myfile=request.FILES['myfile']
        print(myfile.name.split('.'))
        image_name_banner = image_name +'-' + 'banner' + '.' + myfile.name.split('.')[-1]
        print(image_name_banner)
        myfile.name = image_name_banner
        fs=FileSystemStorage(location='media/events')
        print('myfile. name is '+ str(myfile.name)+' and myfile is '+ str(myfile))
        filename=fs.save(myfile.name,myfile)
        print('filename is '+ str(filename))
        uploadedfileurl=fs.url(filename)
        u_banner=uploadedfileurl
    print(u_banner)

    myfile1=request.POST.get('myfile1', None)
    
    print(myfile1)
    uploadedfileurl_1=''
    u_p=''
    if request.method=='POST' and request.FILES.get('myfile1', None):
        myfile1=request.FILES['myfile1']
        image_name_thumb = image_name +'-' + 'thumbnail' + '.' + myfile1.name.split('.')[-1]
        print(image_name_thumb)
        myfile1.name = image_name_thumb
        fs_1=FileSystemStorage(location='media/events')
        filename_1=fs_1.save(myfile1.name,myfile1)
        uploadedfileurl_1=fs_1.url(filename_1)
        # Articles2.objects.filter(id=event_id).create(profile_image=myfile1)
        u_p =uploadedfileurl_1
    
    myfile2=request.POST.get('myfile2', None)
    
    print(myfile2)
    uploadedfileurl_2=''
    u_editables=''
    if request.method=='POST' and request.FILES.get('myfile2', None):
        myfile2=request.FILES['myfile2']
        editable_name = image_name +'-' + 'editable' + '.' + myfile2.name.split('.')[-1]
        print(editable_name)
        myfile2.name = editable_name
        fs_2=FileSystemStorage(location='media/events/editables')
        filename2=fs_2.save(myfile2.name,myfile2)
        uploadedfileurl_2=fs_2.url(filename2)
        u_editables=uploadedfileurl_2
    
    articles2.banner = u_banner
    articles2.profile_image = u_p
    articles2.editable_image = u_editables
    #s=Articles2(id=event_id,banner=u_banner,profile_image=u_p,editable_image=u_editables)
    
    #print(s)
    articles2.save()
    

    #return render(request, 'dashboard/create-event/step_3/step_three_temp.html',{'event_id':event_id, 'md5':md5,})
    #return redirect('/live/dashboard/add-event-description/67a6687ee9ff3f3d54eb361752c9fcd1/36679')
    #base_url = reverse('dashboard:step_four', kwargs={'md5':md5, 'event_id':event_id})
    #print(base_url)
    
    #return redirect(base_url)
    return HttpResponseRedirect(reverse_lazy('dashboard:step_four', args=(md5,event_id,)))

def create_stall(request):
    
    

    return render(request, 'dashboard/create-stalls.html')



def getSalesDetails(request, event_id):
    event = Articles2.objects.all().filter(id=event_id).first()
    print(event)
    eve_name = event.event_name
    print(eve_name)
    sales = Tickets_Sale.objects.all().filter(event_id=event_id)
    print(sales)
    t_count = len(sales)
    print(t_count)

    tkt_type=[]
    tkt_qty=[]
    tkt_amt=[]
    tkt_p_date=[]
    tkt_s_site=[]
    tkt_atendee=[]
    tkt_book_id=[]

    if t_count != 0:
        for i in sales:
            print(i)
            tkt_book_id.append(i.booking_id)
            tkt_type.append(i.ticket_type)
            tkt_amt.append(i.ampunt_paid)
            tkt_qty.append(i.qty)
            tkt_p_date.append(i.purchase_date)
            tkt_s_site.append(i.seller_site)
            tkt_atendee.append(i.attendee_name)

    details = zip(tkt_type,tkt_book_id,tkt_amt,tkt_qty,tkt_p_date,tkt_s_site,tkt_atendee)

    return render(request,'sale_details.html',{'details':details,'count':t_count,'eve_name':eve_name})

