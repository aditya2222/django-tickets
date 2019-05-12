from rest_framework import serializers
from .models import Articles2,Tickets


class EditViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Articles2
        fields = '__all__'

class EditTicketSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tickets
        fields = '__all__'
