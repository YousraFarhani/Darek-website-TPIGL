from .models import *
from rest_framework import serializers 


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['FirstName','LastName','PfP','PhoneNumber','Email']
        

class AnnouncementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id','PubDate','Title','Description','Area', 'Price','Type','Category', 'Wilaya', 'Commune', 'Adress','Owner_id']
        

class FavouriteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Favourite
        fields = ['user','announcement']
       
       
class OfferSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Offer
        fields = ['id','sender_id','receiver_id','announcement_id','content']
        
        
class ResponseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Response
        fields = ['id','owner_id','offer_id','content']