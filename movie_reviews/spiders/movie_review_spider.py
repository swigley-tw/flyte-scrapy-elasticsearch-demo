from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose
from scrapy.spiders import Spider
from scrapy.selector import Selector
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from movie_reviews.items import MovieReview, MoveReviewText


class MovieReviewSpider(CrawlSpider):
    name = "movie_reviews"
    allowed_domains = ["rogerebert.com"]
    start_page = 11
    end_page = 20
    start_urls = [
        "https://www.rogerebert.com/reviews/page/{}/".format(page) for page in range(start_page, end_page)
    ]
    rules = [
        Rule(LinkExtractor(allow=(), restrict_xpaths='//h5[@class="review-stack--title"]/a'),
             callback='parse_review', follow=True)
    ]
    def parse(self, response):
        """
        The lines below is a spider contract. For more info see:
        http://doc.scrapy.org/en/latest/topics/contracts.html

        @url http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/
        @scrapes name
        """

        reviews = response.xpath('//h5[@class="review-stack--title"]')

        items = []
        i = 0
        for review in reviews:
            item = MovieReview()
            item_url = review.xpath('a/@href').extract()
            item['title'] = review.xpath('a/text()').extract()
            item['url'] = review.xpath('a/@href').extract()
            item['text'] = scrapy.Request(response.urljoin(item_url))
            items.append(item)
        return items


    def parse_review(self, response):
        self.logger.info('----------SCRAPING------------')
        loader = ItemLoader(MovieReview(), response=response)
        loader.default_input_processor = MapCompose(str.strip)
        print(str(response.request.url))
        loader.add_value('text', response.xpath('//html/body/div/div/section/section/p').extract())
        loader.add_value('url', response.request.url)
        loader.add_value('title', response.xpath('//html/head/title[1]/text()').extract())

        yield loader.load_item()
