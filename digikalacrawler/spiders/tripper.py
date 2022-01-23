from curses import meta
from markupsafe import string
import scrapy, json

ids = []

class Tripper(scrapy.Spider):
    name = 'Tripper'

    start_urls = ['https://www.digikala.com/']

    def parse(self, response):
        main_categories = response.css('.c-navi-new-list__sublist-option--item a.c-navi-new__big-display-title::attr(href)').getall()
        for href in main_categories:
            yield response.follow(href,self.parse_categories, meta = {'href': href} )

    def parse_categories(self, response):
        last_page = int(response.css('a.c-pager__next::attr(data-page)').get())

        for i in range (1, last_page+1):
            href = response.meta.get('href')
            yield response.follow(f'{href}/pageno={i}', self.responsible)

    def responsible(self, response):
        for i in range(1,37):
            json_item = json.loads(response.css(f'.c-listing__items > li:nth-child({i}) > div:nth-child(1)::attr(data-enhanced-ecommerce)').extract()[0])
            image = response.css(f'.c-listing__items > li:nth-child({i}) > div:nth-child(1)').css('a.c-product-box__img').css('img::attr(src)').get()

            comments_url = f'https://www.digikala.com/ajax/product/comments/{json_item["id"]}'
            
            comments = response.follow(comments_url, self.comments, meta={'product-id': json_item["id"], 'product-name': json_item["name"], 'image': image, 'price': json_item["price"]})

            yield comments
            
    def comments(self, response):

        comments = response.css('div.c-comments__item')
        rate = response.css('.c-comments__side-rating-main::text').get()
        total_no = response.css('.c-comments__side-rating-all::text').get().strip().split(" ")[-2]

        for comment in comments:
            yield {
                'product-id': response.meta.get('product-id'),
                'product-name': response.meta.get('product-name', None),
                'image': response.meta.get('image', None),
                'Rate': rate + ' out of 5',
                'Number of Rates': total_no,
                'Price': response.meta.get('price'),
                'Date': comment.css('span.c-comments__detail::text').getall()[0],
                'Owner': comment.css('span.c-comments__detail::text').getall()[-1],
                'text': comment.css('div.c-comments__content::text').get()
            }
            