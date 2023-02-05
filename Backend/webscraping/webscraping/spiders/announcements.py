import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst

from Backend.webscraping.webscraping.items import AnnouncementItem

from  Backend.models import Announcement, User, Photo

from datetime import datetime


import requests
import tempfile
from django.core import files

class AnnouncementSpider(CrawlSpider):
    name = "announcements"
    allowed_domains = ["annonce-algerie.com"]
    start_urls = []
    #specify n: the number of pages that you want to crawl (from 1 to 9)
    n = 2
    for i in range(n):
        url = "http://www.annonce-algerie.com/AnnoncesImmobilier.asp?rech_cod_cat=1&rech_cod_rub=&rech_cod_typ=&rech_cod_sou_typ=&rech_cod_pay=DZ&rech_cod_reg=&rech_cod_vil=&rech_cod_loc=&rech_prix_min=&rech_prix_max=&rech_surf_min=&rech_surf_max=&rech_age=&rech_photo=&rech_typ_cli=&rech_order_by=31&rech_page_num={page}".format(
        page = i+1
        )
        start_urls.append(url)
        
    rules = (
        Rule(
            LinkExtractor(allow=("DetailsAnnonceImmobilier.asp")),
            callback="parse_announcement",
            follow=True,
        ),
    )


    def parse_announcement(self, response):
        
        announcement_loader = ItemLoader(AnnouncementItem(), response=response)
        announcement_loader.default_output_processor = TakeFirst()
          
        #check if adresse exist
        if(response.css('td.da_label_field::text')[2].extract()=='Adresse'):
            adress = response.css('td.da_field_text::text')[6].extract()
            announcement_loader.add_value('Adress', adress)
        else:
            return
        
        #check if photo1 exists
        photo1_link = response.css('img#PhotoMin_0')
        if(photo1_link!=[]):
           photo1_link = photo1_link.attrib['src']
           photo1_link = 'http://www.annonce-algerie.com' + photo1_link
           res = requests.get(photo1_link, stream=True)
           if (res.status_code != requests.codes.ok):
                return
        else:
            return

        
        #title
        titre = response.css('b::text')[2].extract()
        announcement_loader.add_value('Title', titre)
        
        #category
        categ = response.css('td.da_field_text')[0].css('a::text')[1].extract()
        if(categ=='Vente'):
            category = 1
        elif(categ=='Location'):
            category = 3
        elif(categ=='Location vacances'):
            category = 4
        else:
            category=0
        announcement_loader.add_value('Category', category)
            
        #type
        typ = response.css('td.da_field_text')[0].css('a::text')[2].extract()
        announcement_loader.add_value('Type', typ)      
        
        #wilaya
        wilaya = response.css('td.da_field_text')[1].css('a::text')[2].extract()
        announcement_loader.add_value('Wilaya', wilaya)

        #commune
        commune = response.css('td.da_field_text')[1].css('a::text')[3].extract()
        announcement_loader.add_value('Commune', commune)
        
        #area
        area = response.css('td.da_field_text::text')[7].extract()
        area = area.replace('\xa0m²\xa0', '')
        area = area.replace(' ', '')
        area = int(area)
        announcement_loader.add_value('Area', area)
        
        #price
        price = response.css('td.da_field_text::text')[8].extract()
        price = price.replace('\xa0Dinar Algèrien (DA)\xa0\r\n\t\t     ', '')
        price = price.replace(' ', '')
        price = int(price)
        announcement_loader.add_value('Price', price)
        
        #date    
        fields = response.css('td.da_field_text::text')
        str_date = fields[len(fields)-1].extract()
        date = datetime.strptime(str_date, '%d/%m/%Y')
        announcement_loader.add_value('PubDate', date)

        #phone
        phone = response.css('span.da_contact_value::text')[0].extract() 
        phone = phone.replace(' ', '')
        phone = '0' + phone[len(phone)-9:]
        
        #text
        fields = response.css('td.da_field_text::text')
        text_field = fields[10:len(fields)-2].extract()
        text = '\n'.join(text_field)
        text += "\n\n" + "Numéro de téléphone de l'annonceur: " + phone 
        text += "\nLa source de l'annonce: www.annonce-algerie.com"
        announcement_loader.add_value('Description', text)

        
        #user
        user = User(FirstName='Annonce', LastName='Algerie', Email=' ',PfP='http://www.annonce-algerie.com/Images/Banners/logo_88x31_algerie.gif',PhoneNumber=' ')
        try:
            User.objects.get(pk=' ')
        except User.DoesNotExist:
            user.save()
        announcement_loader.add_value('Owner', user)
        
                
        #saving the item in DB
        annonce = announcement_loader.load_item().save()
        print('saved')
        #logging the item
        
        print('item:')
        print(announcement_loader.load_item())
        
        # List of images to download
        image_urls = []

        #photo1
        image_urls.append(photo1_link)
        
        #photo2
        photo2_link = response.css('img#PhotoMin_1')
        if(photo2_link!=[]):
           photo2_link = photo2_link.attrib['src']
           photo2_link = 'http://www.annonce-algerie.com' + photo2_link
           image_urls.append(photo2_link)
        
        #photo3
        photo3_link = response.css('img#PhotoMin_2')
        if(photo3_link!=[]):
           photo3_link = photo3_link.attrib['src']
           photo3_link = 'http://www.annonce-algerie.com' + photo3_link
           image_urls.append(photo3_link)
        
        #photo4
        photo4_link = response.css('img#PhotoMin_3')
        if(photo4_link!=[]):
           photo4_link = photo4_link.attrib['src']
           photo4_link = 'http://www.annonce-algerie.com' + photo4_link
           image_urls.append(photo4_link)
        
        print('saving photos:')
        print(image_urls)
        
        for image_url in image_urls:
            # Stream the image from the url
            response = requests.get(image_url, stream=True)

            # Was the request OK?
            if response.status_code != requests.codes.ok:
                # error handling, skip file
                continue
            
            # Get the filename from the url, used for saving later
            file_name = image_url.split('/')[-1]
            
            # Create a temporary file
            lf = tempfile.NamedTemporaryFile()
            # Read the streamed image in sections
            for block in response.iter_content(1024 * 8):
                
                # If no more file then stop
                if not block:
                    break

                # Write image block to temporary file
                lf.write(block)

            # Create the model to save the image to
            photo = Photo()
            photo.announcement = annonce            
            photo.image.save(file_name, files.File(lf))
            print('photo saved')
            print(photo)

        yield announcement_loader.load_item()
        