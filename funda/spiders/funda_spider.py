import re
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from funda.items import FundaItem

class FundaSpider(CrawlSpider):

    name = "funda_spider"
    allowed_domains = ["funda.nl"]

    def __init__(self, place='amsterdam'):
        self.start_urls = ["http://www.funda.nl/koop/%s/p%s/" % (place, page_number) for page_number in range(1,10)]
        self.base_url = "http://www.funda.nl/koop/%s/" % place
        self.le1 = LinkExtractor(allow=r'%s+(huis|appartement)-\d{8}' % self.base_url)

    def extract_text(self, response, xpath):
        results = response.xpath(xpath).extract()
        return results[0].strip() if results else ''

    def parse(self, response):
        links = self.le1.extract_links(response)
        for link in links:
            if link.url.count('/') == 6 and link.url.endswith('/'):
                item = FundaItem()
                item['url'] = link.url
                if re.search(r'/appartement-',link.url):
                    item['woningtype'] = "appartement"
                elif re.search(r'/huis-',link.url):
                    item['woningtype'] = "huis"
                yield scrapy.Request(link.url, callback=self.parse_dir_contents, meta={'item': item})

    def parse_dir_contents(self, response):
        new_item = response.request.meta['item']

        title = response.xpath('//title/text()').extract()[0]
        postal_code = re.search(r'\d{4} [A-Z]{2}', title).group(0)
        city = re.search(r'\d{4} [A-Z]{2} \w+',title).group(0).split()[2]
        address = re.findall(r'te koop: (.*) \d{4}',title)[0]
        new_item['gemeente'] = city
        new_item['postcode'] = postal_code
        new_item['address'] = address

        price_dd = response.xpath("//dt[contains(.,'Vraagprijs')]/following-sibling::dd[1]/text()").extract()[0]
        price = re.findall(r' \d+.\d+', price_dd)[0].strip().replace('.','')
        new_item['vraagprijs'] = price


        year_built_dd = self.extract_text(response, "//dt[contains(.,'Bouwjaar')]/following-sibling::dd[1]/text()")
        year_built = re.findall(r'\d+', year_built_dd)[0] if year_built_dd else ''
        new_item['bouwjaar'] = year_built

        area_dd = self.extract_text(response, "//dt[contains(.,'Woonoppervlakte')]/following-sibling::dd[1]/text()")
        area = re.findall(r'\d+', area_dd)[0] if area_dd else ''
        new_item['woonoppervlakte'] = area

        rooms_dd = self.extract_text(response, "//dt[contains(.,'Aantal kamers')]/following-sibling::dd[1]/text()")
        rooms = re.findall('\d+ kamer',rooms_dd)
        rooms = rooms[0].replace(' kamer','') if rooms else ''
        new_item['kamers'] = rooms

        bedrooms = re.findall('\d+ slaapkamer',rooms_dd)
        bedrooms = bedrooms[0].replace(' slaapkamer','') if bedrooms else ''
        new_item['slaapkamers'] = bedrooms

        

        #additional info


        new_item['status'] =  self.extract_text(response, "//dt[contains(.,'Status')]/following-sibling::dd[1]/text()")

        new_item['aanvaarding'] =  self.extract_text(response, "//dt[contains(.,'Aanvaarding')]/following-sibling::dd[1]/text()")

        
        periodic_contribution_vve = response.xpath("//dt[contains(.,'Bijdrage VvE')]/following-sibling::dd[1]/text()").extract()
        periodic_contribution_periodic = response.xpath("//dt[contains(.,'Periodieke bijdrage')]/following-sibling::dd[1]/text()").extract()
        periodic_contribution_service = response.xpath("//dt[contains(.,'Servicekosten')]/following-sibling::dd[1]/text()").extract()
        periodic_contribution = periodic_contribution_vve + periodic_contribution_service + periodic_contribution_periodic
        periodic_contribution = ', '.join(periodic_contribution).strip()
        #periodic_contribution = re.findall(r'\d+', periodic_contribution)[0] if periodic_contribution else ''
        new_item['periodieke_bijdrage'] = periodic_contribution


        house_type_detail = response.xpath("//dt[contains(.,'Soort woonhuis')]/following-sibling::dd[1]/text()").extract()
        appartment_type_detail = response.xpath("//dt[contains(.,'Soort appartement')]/following-sibling::dd[1]/text()").extract()
        property_type_detail = (house_type_detail + appartment_type_detail)
        new_item['soort_woning'] = ' '.join(property_type_detail).strip()


        new_item['soort_bouw'] =  self.extract_text(response, "//dt[contains(.,'Soort bouw')]/following-sibling::dd[1]/text()")

        new_item['soort_dak'] =  self.extract_text(response, "//dt[contains(.,'Soort dak')]/following-sibling::dd[1]/text()")

        new_item['specifiek'] =  self.extract_text(response, "//dt[contains(.,'Specifiek')]/following-sibling::dd[1]/text()")

        new_item['perceel_oppervlakte'] =  self.extract_text(response, "//dt[contains(.,'Perceeloppervlakte')]/following-sibling::dd[1]/text()")

        new_item['inpandige_ruimte'] =  self.extract_text(response, "//dt[contains(.,'Overige inpandige ruimte')]/following-sibling::dd[1]/text()")

        new_item['buitenruimte'] =  self.extract_text(response, "//dt[contains(.,'Gebouwgebonden buitenruimte')]/following-sibling::dd[1]/text()")


        yield new_item
        



# Gebouwgebonden buitenruimte
# Inhoud
# Aantal woonlagen
# Aantal badkamers
# Gelegen op
# Badkamervoorzieningen
# Externe bergruimte
# Voorzieningen


# Energielabel | Voorlopig energielabel
# Isolatie, Verwarming, Warm water, Cv-ketel

# Eigendomssituatie
# Lasten

# Ligging
# Tuin, Achtertuin, Voortuin, Ligging tuin
# Balkon/dakterras

# Schuur, berging

# Soort garage
# Capaciteit

# Soort parkeergelegenheid


# Omschrijving
# Image url

