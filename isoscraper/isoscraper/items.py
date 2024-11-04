from scrapy import Field, Item
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from dataclasses import dataclass, field
from typing import Optional, TypedDict
from datetime import datetime

import pymupdf4llm
import os
import requests

@dataclass
class IsoItem:
    name: Optional[str] = field(default=None)
    section: Optional[str] = field(default=None)
    date: Optional[str] = field(default=None)
    url: Optional[str] = field(default=None)
    content_type: Optional[str] = field(default=None)
    content: Optional[str] = field(default=None)

class IsoItemLoader(ItemLoader):
    item = IsoItem()
    default_output_processor = TakeFirst()

class HTMLItemLoader(IsoItemLoader):
    pass
        
