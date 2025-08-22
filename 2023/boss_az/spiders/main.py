import scrapy

class MainSpider(scrapy.Spider):
    name            = "main"
    allowed_domains = ["boss.az"]
    start_urls      = ["https://boss.az/vacancies.html?action=index&controller=vacancies&format=html&only_path=true&page=6&search%5Bcategory_id%5D=&search%5Bcompany_id%5D=&search%5Beducation_id%5D=&search%5Bexperience_id%5D=&search%5Bkeyword%5D=&search%5Bregion_id%5D=&search%5Bsalary%5D=&type=vacancies"]

    def parse(self, response):
        links = response.css('.results-i-link::attr(href)').getall()

        for link in links:
            yield response.follow(link, self.parse_product, meta={'link': link})

        prev_page = response.css('nav.pagination span.prev a[rel="prev"]::attr(href)').extract_first()
        next_page = response.css('nav.pagination span.next a[rel="next"]::attr(href)').extract_first()

        if next_page:
            yield response.follow(next_page, self.parse)
        elif prev_page:
            yield response.follow(prev_page, self.parse)

    def parse_product(self, response):
        href = response.request.meta['link']
        yield {
            'href'  : href,
            'phone' : response.css('a.phone::attr(href)').extract_first(),
        }
