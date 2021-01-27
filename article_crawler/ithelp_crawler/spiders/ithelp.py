import scrapy
import re

class IthelpSpider(scrapy.Spider):
    name = 'ithelp'
    allowed_domains = ['ithome.com.tw']
    #start_urls = ['https://ithelp.ithome.com.tw/users/20107875/ironman/2209']

    def start_requests(self):
        for page in range(1, 2):
            yield scrapy.Request(url=f'https://ithelp.ithome.com.tw/articles?tab=tech&page={page}', callback=self.parse)

    def parse(self, response):
        article_tags = response.css('div.qa-list')
        if len(article_tags) > 0:
            for article_tag in article_tags:
                # tag: a, class: list__title
                article_title = article_tag.css('a.qa-list__title-link')
                # ::attr(href) : get all href data under this tag
                # strip(): remove the space
                # get() : get text
                article_url = article_title.css('::attr(href)').get().strip()
                # response.follow support relative path 
                yield response.follow(article_url, callback=self.parse_article)

    def parse_article(self, response):
        block_main = response.css('div.leftside')
        block_inter = block_main.css('div.qa-panel.clearfix')
        block_content = block_inter.css('div.qa-panel__content')

        block_header = block_content.css('div.qa-header')
        block_header_info = block_header.css('div.qa-header__info')

        # ::text : locate text under the tag
        title = block_header.css('h2.qa-header__title::text').get().strip()
        author = block_header_info.css('a.qa-header__info-person::text').get().strip()
        
        publish_time = block_header_info.css('a.qa-header__info-time::text').get().strip()
        
        tag_group = block_header.css('div.qa-header__tagGroup')
        tag_elements = tag_group.css('a.tag qa-header__tagList')
        tags = [tag_element.css('::text').get().strip() for tag_element in tag_elements]
        
        content = '.'.join(block_content.css('div.markdown__style').css('::text').getall())
        content = content.replace('\r','').replace('\n','') # content include many \r \n, which influence csv reading

        view_count_str = block_header_info.css('span.qa-header__info-view').css('::text').get().strip()
        view_count = int(re.search('(\d+).*', view_count_str).group(1)) #1st group is the number \d: [0-9]

        article = {
            'url': response.url,
            'title': title,
            'author': author,
            'publish_time': publish_time,
            'tags': '_'.join(tags),
            'content': content,
            'view_count': view_count
        }

        yield article