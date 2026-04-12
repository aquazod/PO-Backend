import scrapy


class PropertyItem(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()        # int or None
    date = scrapy.Field()         # ISO date string or None
    location = scrapy.Field()      # str or None
    link = scrapy.Field()         # clean URL, no ?pg= param