# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from supabase import create_client, Client
import logging

# Define your Supabase credentials
SUPABASE_URL = "https://your-project-url.supabase.co"
SUPABASE_API_KEY = "your-anon-key"

class IsoscraperPipeline:
    def __init__(self):
        # Initialize Supabase client
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_API_KEY)
        logging.info("Supabase client initialized")

    def process_item(self, item, spider):
        # Insert the scraped item into the Supabase table
        try:
            response = self.supabase.table("your_table_name").insert(item).execute()
            logging.info(f"Successfully inserted item into Supabase: {response.data}")
        except Exception as e:
            logging.error(f"Error inserting item into Supabase: {str(e)}")
        return item
