# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Articles2(models.Model):
#    id = models.IntegerField(primary_key=True)
    country = models.CharField(max_length=45)
    event_name = models.CharField(max_length=200 , unique= True ,default='nothing yet')
    md5 = models.CharField(max_length=35)
    date_added = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    profile_image = models.ImageField(upload_to='events' , default='')
    sdate = models.DateTimeField(db_column='sDate', blank=True, null=True , unique= True)  # Field name made lowercase.
    edate = models.DateTimeField(db_column='eDate', blank=True, null=True , unique = True)  # Field name made lowercase.
    address_line1 = models.TextField(blank=True, null=True)
    address_line2 = models.TextField(blank=True, null=True)
    pincode = models.IntegerField(default=000000)
    state = models.CharField(max_length=30)
    city = models.TextField()
    locality = models.CharField(max_length=50)
    full_address = models.CharField(max_length=255 , unique= True , default='nothing yet') # 255 is max allowed by mysql for unique constraints
    latitude = models.CharField(max_length=105)
    longitude = models.CharField(max_length=105)
    start_time = models.TimeField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)
    description = models.TextField(default='nothing yet')
    website = models.CharField(max_length=50, blank=True, null=True)
    fb_page = models.CharField(max_length=200, blank=True, null=True)
    fb_event_page = models.CharField(max_length=200, blank=True, null=True)
    event_hashtag = models.CharField(max_length=30, blank=True, null=True)
    source_name = models.CharField(max_length=30)
    source_url = models.CharField(max_length=350)
    email_id_organizer = models.CharField(max_length=100)
    ticket_url = models.TextField(default='nothing yet')
    banner = models.ImageField(upload_to='events' , default='')
    editable_image = models.FileField(upload_to='editables' , default='')
   
    class Meta:
        managed = False
        db_table = 'articles2'
        unique_together = (('event_name', 'sdate', 'edate', 'full_address'),)
    
    def __str__(self):
        return self.event_name




class Categories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category = models.CharField(max_length=38)
    page_name = models.CharField(max_length=30)
    short_lived = models.IntegerField()
    status = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'categories'
    


class CategorizedEvents(models.Model):
    table_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    category_id = models.IntegerField()
    topic_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categorized_events'


class Topics(models.Model):
    topics_id = models.AutoField(primary_key=True)
    topic = models.CharField(max_length=50)
    category = models.CharField(max_length=37)

    class Meta:
        managed = False
        db_table = 'topics'

class StatusPromotionTicketing(models.Model):
    status_promotion_ticketing_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    unique_id = models.CharField(max_length=10)
    mode = models.CharField(max_length=20)
    private = models.IntegerField()
    event_active = models.IntegerField()
    approval = models.IntegerField()
    network_share = models.IntegerField()
    ticketing = models.IntegerField()
    promotion = models.IntegerField()
    connected_user = models.IntegerField()
    complete_details = models.IntegerField()
    validation_status_sent = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'status_promotion_ticketing'

class AttendeeFormTypes(models.Model):
    type_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'attendee_form_types'

class AttendeeFormOptions(models.Model):
    option_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    ques_id = models.IntegerField()
    option_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'attendee_form_options'

class AttendeeFormBuilder(models.Model):
    ques_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    ques_title = models.TextField()
    ques_type = models.IntegerField()
    ques_accessibility = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'attendee_form_builder'

class Tickets(models.Model):
    tickets_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    ticket_name = models.CharField(max_length=100)
    ticket_price = models.CharField(max_length=8)
    other_charges = models.CharField(max_length=3, blank=True, null=True,default='0')
    other_charges_type = models.IntegerField(blank=True, null=True,default='1')
    ticket_qty = models.IntegerField()
    min_qty = models.IntegerField()
    max_qty = models.IntegerField()
    qty_left = models.IntegerField()
    ticket_msg = models.CharField(max_length=200,blank=True, null=True)
    ticket_start_date = models.DateTimeField(blank=True, null=True)
    expiry_date = models.DateTimeField()
    ercess_fee = models.IntegerField()
    transaction_fee = models.IntegerField()
    ticket_label = models.CharField(max_length=20)
    active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tickets'


class Tickets_Sale(models.Model):
    table_id = models.AutoField(primary_key=True)
    event_id = models.IntegerField()
    ticket_id = models.IntegerField()
    booking_id = models.IntegerField()
    oragnizer = models.IntegerField()
    ticket_type = models.CharField(max_length=100)
    purchase_date = models.DateTimeField()
    #amount_paid = models.CharField(max_length=8)
    ampunt_paid = models.CharField(max_length=8)
    qty = models.IntegerField()
    attendee_name = models.CharField(max_length=30)
    attendee_contact = models.CharField(max_length=12)
    attendee_email = models.CharField(max_length=80)
    seller_site = models.CharField(max_length=80)
    receival_status = models.IntegerField(blank=True, null=True)
    forward_status = models.IntegerField(blank=True, null=True)
    ticket_handover = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tickets_sale'


class AboutCountries(models.Model):
    table_id = models.AutoField(primary_key=True)
    country = models.CharField(max_length=50)
    country_code = models.CharField(max_length=2)
    currency = models.CharField(max_length=10)
    pincode_size = models.IntegerField()
    event_advertising = models.CharField(max_length=11)
    event_stall_spaces = models.CharField(max_length=11)
    event_mcp = models.CharField(max_length=11)
    timezone = models.CharField(max_length=255, blank=True, null=True)
    currency_code = models.CharField(max_length=255, blank=True, null=True)
    bank_regex1 = models.CharField(max_length=100, blank=True, null=True)
    bank_regex2 = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'about_countries'

class rsvp(models.Model):
    table_id = models.AutoField(primary_key=True)
    date_added = models.DateTimeField()
    event_id = models.IntegerField()
    uniq_id = models.CharField(max_length=10)
    supplied_by = models.CharField(max_length=30)
    attendee_name = models.CharField(max_length=30)
    attendee_email = models.CharField(max_length=80)
    attendee_contact = models.CharField(max_length=12)

    class Meta:
        managed = False
        db_table = 'rsvp'

    def __str__(self):
        return self.uniq_id

class BankDetails(models.Model):
    user_id = models.IntegerField()
    bank_name = models.CharField(max_length=20)
    ac_holder_name = models.CharField(max_length=70)
    ac_type = models.CharField(max_length=15)
    ac_number = models.CharField(max_length=26)
    ifsc_code = models.CharField(max_length=14)
    branch = models.CharField(max_length=30)
    gst_number = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'bank_details'

class Admin(models.Model):
    table_id = models.IntegerField(primary_key=True)
    fname = models.CharField(max_length=20)
    lname = models.CharField(max_length=20)
    email_id = models.CharField(max_length=20)
    password = models.CharField(max_length=300, blank=True, null=True)
    admin_type = models.IntegerField()
    admin_active = models.IntegerField()
    team = models.IntegerField()
    mobile = models.CharField(max_length=11)

    class Meta:
        managed = False
        db_table = 'admin'

class Admin_Event_Assignment(models.Model):
    table_id = models.IntegerField(primary_key=True)
    admin_id = models.IntegerField()
    super_admin_id = models.IntegerField()
    event_id = models.IntegerField()
    assignment_timestamp = models.DateTimeField()
    deadline = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'admin_event_assignment'

class StatusOnChannel(models.Model):
    table_id = models.IntegerField(primary_key=True)
    event_id = models.IntegerField()
    last_updated = models.DateTimeField()
    site_id = models.IntegerField()
    admin_id = models.IntegerField()
    link = models.CharField(max_length=350)
    promotion_status = models.CharField(max_length=30)
    partner_status = models.CharField(max_length=30)
    validation_status_sent = models.CharField(max_length=30,blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'event_status_on_channel'

class PartnerSites(models.Model):

    table_id = models.IntegerField(primary_key=True)
    site_name = models.CharField(max_length=30)
    site_url = models.CharField(max_length=350)
    country = models.CharField(max_length=30)
    
    website = models.IntegerField()
    app = models.CharField(max_length=30)
    coverage = models.CharField(max_length=30)
    method = models.CharField(max_length=30)
    doc_name = models.CharField(max_length=30)
    email1 = models.CharField(max_length=30)
    email2 = models.CharField(max_length=30)
    cc = models.CharField(max_length=30)
    restriction = models.CharField(max_length=100)
    support_name = models.CharField(max_length=30)
    support_email = models.CharField(max_length=30)
    support_mobile = models.CharField(max_length=15)
    payment_policy = models.CharField(max_length=200)
    payment_within_days = models.IntegerField()
    merchant_name = models.CharField(max_length=30)
    official_convenience_fee = models.DecimalField(max_digits=6, decimal_places=2)
    official_transaction_fee = models.DecimalField(max_digits=6, decimal_places=2)
    official_flat_charges = models.DecimalField(max_digits=6, decimal_places=2)
    official_tax_charges = models.DecimalField(max_digits=6, decimal_places=2)
    negotiated_convenience_fee = models.DecimalField(max_digits=6, decimal_places=2)
    negotiated_transaction_fee = models.DecimalField(max_digits=6, decimal_places=2)
    negotiated_flat_charges = models.DecimalField(max_digits=6, decimal_places=2)
    negotiated_tax_charges = models.DecimalField(max_digits=6, decimal_places=2)
    convenience_fee_organizer = models.DecimalField(max_digits=6, decimal_places=2)
    transaction_fee_organizer = models.DecimalField(max_digits=6, decimal_places=2)
    flat_fee_organizer = models.DecimalField(max_digits=6, decimal_places=2)
    tax_fee_organizer = models.DecimalField(max_digits=6, decimal_places=2)
    additional_msg = models.CharField(max_length=200)
    active_state = models.IntegerField()
    
    class Meta:
        managed = False
        db_table = 'partner_sites'
