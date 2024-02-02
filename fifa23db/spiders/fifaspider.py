import scrapy
from scrapy.settings.default_settings import DEFAULT_REQUEST_HEADERS

class FifaspiderSpider(scrapy.Spider):
    name = "fifaspider"
    allowed_domains = ["futwiz.com"]
    start_urls = ["https://www.futwiz.com/en/fifa23/career-mode/players?page=0"]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers=DEFAULT_REQUEST_HEADERS, callback=self.parse)

    def parse(self, response):
        players = response.css('tr.table-row')
        for player in players:
            url = player.css('p.name a::attr(href)').get()
            full_url = "https://www.futwiz.com" + url
            yield scrapy.Request(full_url, callback=self.parse_player_page)

        # Next page logic
        next_page = response.css('div.col-2.next a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_player_page(self, response):
        real_face_button = response.xpath('//div[contains(@class, "realfacebutton")]')
        if real_face_button:  # Check if any elements were found
            wage_xpath = '//*[@id="panel"]/div[3]/div/div[2]/div[1]/div[3]/div/div[14]/text()'
        else:
            wage_xpath = '/html/body/main/div[3]/div/div[2]/div[1]/div[3]/div/div[13]/text()'

        yield {
            'Name': response.xpath('//*[@id="panel"]/div[3]/div/div[1]/div/div[1]/h1/text()').get(),
            'Nation': response.xpath('//*[@id="panel"]/div[3]/div/div[1]/div/div[1]/div/text()').get(),
            'OVR': response.xpath('//*[@id="panel"]/div[3]/div/div[2]/div[1]/div[2]/div[1]/div[1]/p[1]/text()').get(),
            'POT': response.xpath('//*[@id="panel"]/div[3]/div/div[2]/div[1]/div[2]/div[1]/div[2]/p[1]/text()').get(),
            'Age': response.xpath('//*[@id="panel"]/div[3]/div/div[2]/div[1]/div[2]/div[1]/div[4]/p[1]/text()').get(),
            'Height': response.xpath('//*[@id="panel"]/div[3]/div/div[2]/div[1]/div[2]/div[1]/div[5]/p[2]/text()').get(),
            'Weight': response.xpath('//*[@id="panel"]/div[3]/div/div[2]/div[1]/div[2]/div[1]/div[6]/p[1]/text()').get(),
            'Position': response.xpath('//*[@id="panel"]/div[3]/div/div[2]/div[1]/div[3]/div/div[1]/text()').get(),
            'Reputation': response.xpath('//*[@id="panel"]/div[3]/div/div[2]/div[1]/div[3]/div/div[7]/text()').get(),
            'Value': response.css('div.cprofile-inforbar-stat.career-value::text').get(),
            'Wage': response.xpath(wage_xpath).get()
        }
