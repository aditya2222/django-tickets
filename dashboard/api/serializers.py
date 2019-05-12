import hashlib
import datetime
from rest_framework import serializers


from dashboard.models import Articles2, CategorizedEvents, StatusPromotionTicketing, Tickets, BankDetails



class Articles2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Articles2
        fields = ['event_name', 'sdate', 'start_time', 'edate', 'end_time',
		 'address_line1', 'address_line2', 'city', 'state', 
		'country', 'pincode','latitude','longitude' ]
        read_only_fields = ['date_added']
       # extra_kwargs = {'md5': {'write_only': True}}


    event_name = serializers.CharField(
                max_length=200,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_1/eventname.html',
                },
            )
    sdate =serializers.DateField(
                        input_formats=['%d/%m/%Y',],
                        style={
                          'template': 'dashboard/create-event/step_1/startdate.html'}                      
                        )

    start_time =serializers.TimeField(
                        input_formats=['%I:%M %p'],
                        style={
                          'template': 'dashboard/create-event/step_1/stime.html'}
                        )
    edate =serializers.DateField(
                        initial=datetime.date.today,
                        input_formats=['%d/%m/%Y',],
                        style={
                          'template': 'dashboard/create-event/step_1/enddate.html'}
                        )

   
    
    end_time =serializers.TimeField(
                        input_formats=['%I:%M %p'],
                        style={
                          'template': 'dashboard/create-event/step_1/etime.html'}
                        )
    
    address_line1 = serializers.CharField(
                      max_length=200,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/address1.html',
                      },
                    )
    
    address_line2 = serializers.CharField(
                      max_length=200,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/address2.html',
                      },
                    )
    
    city = serializers.CharField(
                      max_length=200,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/city.html',
                      },
                    )

    state = serializers.CharField(
                      max_length=200,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/state.html',
                      },
                    )

    country = serializers.CharField(
                      max_length=200,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/country.html',
                      },
                    )

    pincode = serializers.CharField(
                      max_length=200,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/pin.html',
                      },
                    )

    latitude = serializers.CharField(
                      max_length=15,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/latitude.html',
                      },
                    )

    longitude = serializers.CharField(
                      max_length=25,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/longitude.html',
                      },
                    )



    def validate(self, validated_data, *args, **kwargs):
        sDate = validated_data.get('sdate')
        eDate = validated_data.get('edate')
        if sDate > eDate:
            raise serializers.ValidationError({"End Date":"Start Date cannot be greater than End Date"})
        validated_data['md5'] = self.context['md5']
        return validated_data

class CategorizedEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorizedEvents
        fields = ['topic_id', 'category_id' ]

    def validate(self, validated_data, *args, **kwargs):
        if validated_data['topic_id']  == 0:
            validated_data['topic_id'] = None
        validated_data['event_id'] = self.context['event_id']
        return validated_data


class StatusPromotionTicketingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusPromotionTicketing
        fields = ['event_id','unique_id','mode','private','event_active','approval',
                  'network_share','ticketing', 'promotion', 'connected_user', 'complete_details']

#tickets serializer
class TicketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tickets
        fields = ['ticket_name','ticket_price','other_charges','other_charges_type',
                  'ticket_qty','min_qty','max_qty','start_date','start_time_step5',
                  'end_date','end_time_step5',
#'ticket_start_date','expiry_date','ticket_msg',
                  'ticket_msg','ticket_label',
        #  Note : ercessfee and transaction fee must be calculated and then passed to the serializer
        # 'event_id','qty_left','ercess_fee','transaction_fee','active',
         ]
        
    ticket_name = serializers.CharField(
                max_length=200,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/ticketname.html',
                },
            )
    ticket_price = serializers.CharField(
                max_length=8,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/ticketprice.html',
                },
            )
    other_charges = serializers.CharField(required = False,
                max_length=6,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/extracharges.html',
                },
            )
    #othercharges type will come here        
    other_charges_type = serializers.IntegerField(required = False,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/extrachargestype.html',
                },
            )            
    ticket_qty = serializers.IntegerField(
                
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/ticketqty.html',
                },
            )
    min_qty = serializers.IntegerField(
                
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/ticketmin.html',
                },
            )                 
    max_qty = serializers.IntegerField(
                
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/ticketmax.html',
                },
            )                                
    start_date =serializers.DateField(
                         input_formats=['%d/%m/%Y',],
                         style={
                           'template': 'dashboard/create-event/step_5/startdate.html'}                      
                         )

    start_time_step5 =serializers.TimeField(
                         input_formats=['%I:%M %p'],
                         style={
                           'template': 'dashboard/create-event/step_5/stime.html'}
                         )
    end_date =serializers.DateField(
                         input_formats=['%d/%m/%Y',],
                         style={
                           'template': 'dashboard/create-event/step_5/enddate.html'}
                         )

   
    
    end_time_step5 =serializers.TimeField(
                         input_formats=['%I:%M %p'],
                         style={
                           'template': 'dashboard/create-event/step_5/etime.html'}
                         )
    
    ticket_msg = serializers.CharField(required=False,
                max_length=200,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/anymessage.html',
                },
            )
    #ticket label will come here
    ticket_label = serializers.CharField(
                max_length=200,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/ticketlabel.html',
                },
            )


    def validate(self, validated_data, *args, **kwargs):
        print("this is date validation")
        sDate = validated_data.get('start_date')
        eDate = validated_data.get('end_date')
        print(sDate)
        print(eDate)
        if sDate > eDate:
            raise serializers.ValidationError({"End Date":"Start Date cannot be greater than End Date"})
        del validated_data['start_date']
        del validated_data['start_time_step5']
        del validated_data['end_date']
        del validated_data['end_time_step5']
        validated_data['event_id'] = self.context['event_id']
        validated_data['ticket_start_date'] = self.context['ticket_start_date']
        validated_data['expiry_date'] = self.context['expiry_date']
        validated_data['qty_left'] = self.context['qty_left']
        validated_data['ercess_fee'] = self.context['ercess_fee']
        validated_data['transaction_fee'] = self.context['transaction_fee']
        validated_data['active'] = 1
        return validated_data

    def ticketqtyidate(self, validated_data, *args, **kwargs):
        print("this is ticket qty validation")
        minticket = validated_data.get('min_qty')
        maxticket = validated_data.get('max_qty')
        if minticket > maxticket:
            raise serializers.ValidationError({"Ticket":"Min ticket cannot be greater than Max ticket"})
        return validated_ticketdata


class BankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetails
        fields = ['user_id','bank_name','ac_holder_name','ac_type','ac_number','ifsc_code','branch','gst_number' ]
        
    bank_name = serializers.CharField(
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/bankname.html',
                },
            )
    
    
    ac_holder_name = serializers.CharField(
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/accholdername.html',
                },
            )
    ac_type = serializers.CharField(
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/acctype.html',
                },
            )

    ac_number = serializers.CharField(
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/accno.html',
                },
    )
    
    ifsc_code = serializers.CharField(
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/ifsc.html',
                },
            )       


    branch = serializers.CharField(
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/branch.html',
                },
            ) 
    gst_number = serializers.CharField(
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/gst.html',
                },
            )
