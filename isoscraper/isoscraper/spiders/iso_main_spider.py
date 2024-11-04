import scrapy
from scrapy import Request
from isoscraper.items import IsoItemLoader
from urllib.parse import urlparse, urljoin, urlencode, quote
from markdownify import markdownify as md
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os 
import pymupdf4llm
import pymupdf.pro
pymupdf.pro.unlock()

def html_to_md(html_text, base_url):
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # Convert href attributes in <a> tags
    for tag in soup.find_all('a', href=True):
        tag['href'] = urljoin(base_url, tag['href'])
    
    # Convert src attributes in <img> and other tags that use src
    for tag in soup.find_all(['img', 'script', 'link'], src=True):
        tag['src'] = urljoin(base_url, tag['src'])
    
    # Return the modified HTML as a string
    return md(str(soup))

class IsoMainSpider(scrapy.Spider):
    name = "iso_main_spider"
    allowed_domains = ["iso-ne.com"]
    start_urls = ["https://www.iso-ne.com/participate/rules-procedures"]
    pdf_dir = "data2/pdfs"
    markdown_dir = "data2/markdown"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.markdown_dir, exist_ok=True)

    def parse(self, response):
        yield self.parse_introductory_text(response)

        links = response.css("div.introductory-text a::attr(href)").getall()
        block_link_list = response.css(".introductory-text .block-link-list")
        if block_link_list:
            for link in links:
                full_link = response.urljoin(link)
                self.log(f"HTML link found: {full_link}")
                yield scrapy.Request(url=full_link, callback=self.parse)
            
        documents_table = response.css("#documents-table, .document-widget-container")
        section = response.css('title::text').get()
        if documents_table:
            current_time = datetime.utcnow()
            publish_date_dt_end = current_time.isoformat(timespec='seconds') + "Z"
            pre_document_type_value = section
            match section:
                case "Master and Local Control Center Procedures":
                    pre_document_type_value = "Master Local Control Center Operating Procedures"
                case "Generator and Non-Generator VAR Capability":
                    pre_document_type_value = "Generator and Non-Generator VAR Capability Operating Procedures"
            
            params = {
                "type":["doc","ceii"],
                "crafterSite":"iso-ne",
                "searchable":"true",
                "includeVersions":"false",
                "publish_date_dt_start":self.settings['PUBLISH_DATE_START'],
                "publish_date_dt_end":publish_date_dt_end,
                "q":"*",
                "source":"docLibraryWidget",
                "pre_document_type_value":pre_document_type_value,
                "pre_file_type":["DOC","DOCX","doc","docx","PPT","PPTX","ppt","pptx","PDF","pdf","XLS","XLSX","CSV","xls","xlsx","csv"], #"ZIP","zip","ZIPX","zipx","x-zip-compressed","X-ZIP-COMPRESSED"
                "start":"0",
                "rows":"99",
                "sort":"normalized_document_title_s asc",
                "facets":["key_issue_value","open_projects_value","closed_projects_value","document_committee_value","events_key","document_type_value","file_type"],
                "file_type.sort":"index",
                "document_type_value.sort":"index",
                "key_issue_value.sort":"index",
                "document_committee_value.sort":"index",
                "open_projects_value.sort":"index",
                "closed_projects_value.sort":"index"
            }
            
            # Construct full URL with parameters
            api_url = f"{self.settings['API_BASE_URL']}?{urlencode(params, safe=':',doseq=True, quote_via=quote)}"
            
            # Make a request to the API
            yield scrapy.Request(api_url, callback=self.parse_api_response,  meta={'section': section})
        
        for link in links:
            if link.endswith('.pdf'):
                yield response.follow(
                    link, 
                    callback=self.parse_file, 
                    meta={
                        'section': response.css('title::text').get(),
                        'content_type' : 'pdf'
                    })

        for link in links:
            if not link.endswith('.pdf'):
                yield response.follow(url=link, callback=self.parse)
    
    def parse_introductory_text(self, response):
        loader = IsoItemLoader(response=response)
        loader.add_value("name", "Introductory Text")
        loader.add_css("section", "h1::text")
        loader.add_value("url", response.url)
        loader.add_value("content_type", "html")
    
        html_text = response.css("div.introductory-text").get()
        md_text = html_to_md(html_text, response.url)
        loader.add_value("content", md_text)
        
        htmlitem = loader.load_item()
        
        return htmlitem

    
    def parse_api_response(self,response):
        data = json.loads(response.text)
        
        # Extract the documents from the response
        documents = data.get('documents', [])
        
        # Process each document
        for document in documents:
            if document.get('file_type') in ["PDF", "pdf", "DOC","DOCX","doc","docx","PPT","PPTX","ppt","pptx","XLS","XLSX","xls","xlsx"]:
                full_link = response.urljoin(document.get('path'))
                yield scrapy.Request(
                    url=full_link, 
                    callback=self.parse_file, 
                    meta={
                        'section': response.meta.get('section'),
                        'date': datetime.utcfromtimestamp(document.get('publish_date') // 1000).strftime('%Y-%m-%d'),
                        'content_type' : document.get('file_type').lower()
                    }
                )
                
    def parse_file(self, response):
        loader = IsoItemLoader(response=response)
        parsed_url = urlparse(response.url)
        file_name = parsed_url.path.split('/')[-1]
        loader.add_value("name", file_name)
        loader.add_value("section", response.meta.get('section'))
        loader.add_value("date", response.meta.get('date'))
        loader.add_value("url", response.url)
        loader.add_value("content_type", response.meta.get('content_type'))
        #loader.add_value("content", response.url)
        
        file_path = os.path.join(self.pdf_dir, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.body)

        markdown_text = pymupdf4llm.to_markdown(file_path)
        loader.add_value("content", markdown_text)

        markdown_file = os.path.splitext(file_name)[0] + ".md"
        markdown_path = os.path.join(self.markdown_dir, markdown_file)
        with open(markdown_path, 'w') as md_file:
            md_file.write(markdown_text)

        yield loader.load_item()
        