import os
import re
import unicodedata
from datetime import datetime
from urllib.parse import urlparse

import scrapy
from scrapy.http import Request, HtmlResponse
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.pipelines.files import FilesPipeline
from scrapy.utils.spider import iterate_spider_output


class DocFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None):
        parsed = urlparse(request.url)
        return request.url.replace(parsed.scheme + "://" + parsed.netloc, "", 1).replace("/", "_-_")

class DocSpider(CrawlSpider):
    name = 'docspider'
    allowed_domains = ['schiermonnikoog.nl']
    start_urls = ['https://www.schiermonnikoog.nl']
    DIR = f'scans/{allowed_domains[0]}_{datetime.now().isoformat()[:19]}'

    if not os.path.exists('scans'):
        os.mkdir('scans')

    custom_settings = {
        'ITEM_PIPELINES': {'spider.DocFilesPipeline': 1},
        'FILES_STORE': f'./{DIR}/files',
    }

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    # Override _requests_to_follow and comment out the first two lines to also process files
    def _requests_to_follow(self, response):
        #if not isinstance(response, HtmlResponse):
        #    return
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [l for l in rule.link_extractor.extract_links(response) if l not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            seen = seen.union(links)
            for link in links:
                r = Request(url=link.url, callback=self._response_downloaded)
                r.meta.update(rule=n, link_text=link.text)
                yield rule.process_request(r, response)

    def _response_downloaded(self, response):
        rule = self._rules[response.meta['rule']]
        return self._parse_response(response, rule.callback, rule.cb_kwargs, rule.follow)

    def _parse_response(self, response, callback, cb_kwargs, follow=True):
        if callback:
            cb_res = callback(response, **cb_kwargs) or ()
            cb_res = self.process_results(response, cb_res)
            for requests_or_item in iterate_spider_output(cb_res):
                yield requests_or_item

        if follow and self._follow_links:
            for request_or_item in self._requests_to_follow(response):
                yield request_or_item

    def parse_item(self, response):
        if not isinstance(response, HtmlResponse):
            with open(f'{self.DIR}/files.txt', 'a') as OUT:
                yield {
                    'file_urls': [response.url],
                }

                if 'referer' in response.request.headers:
                    OUT.write(f'{response.request.headers["referer"]}    {response.url}\n')
                else:
                    OUT.write(f'NO REFERER    {response.url}\n')
        else:
            with open(f'{self.DIR}/urls.txt', 'a') as OUT:
                if 'referer' in response.request.headers:
                    OUT.write(f'{response.request.headers["referer"]}    {response.url}\n')
                else:
                    OUT.write(f'NO REFERER    {response.url}\n')
