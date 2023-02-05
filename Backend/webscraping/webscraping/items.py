# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy_djangoitem import DjangoItem
from Backend.models import Announcement


class AnnouncementItem(DjangoItem):
    django_model = Announcement
    pass



"""class WebscrapingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass"""
