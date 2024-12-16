# Project Thor Backend Utilities

This repository contains scripts that aided in the development of Project Thor. In particular the repository contains three features
1. **Web Scraping** - We have created a web scraper using Scrapy to scrape content from the ISO New England website and store in a JSON file.
2. **Embedding** - We have created a script to convert the JSON file returned by Scrapy into vector embeddings using Open AI's embedding model and then populate our Supabase Postgres database.
3. **Testing** - We have created a testing script using RAGAS that makes API calls to our Next.JS website and can return metrics in a CSV file. 
> [!NOTE]
> You must have the local version of the Next.JS repository running for this script to work. In particular we assume it's open on [localhost:3000](http://localhost:3000)


## Installation
1. `cd /path/to/Project-Thor-Backend/`
2.  To grab the .env file go to: [Google Drive Link](https://drive.google.com/drive/folders/1sdEnDH9pb2lWvhiTuz8H8wDrXKsc2zvy?usp=sharing) and change the file from to a .txt to a dotfile.
3. `pip install -r requirements.txt`

> [!NOTE]
> It is recommended to create a virtual environment like `venv` or `conda` to install these packages locally so they don't conflict with other packages.

## Web Scraper
To run the web scraper
1. `cd /path/to/Project-Thor-Backend/`
2. `cd isoscraper`
3. `scrapy crawl iso_main_spider -o output.json` You can name the output.json to whatever filename you want. 

### Customizing Settings
There are two settings you customize in the `isoscraper/isoscraper/settings.py` file.
1. `DEPTH_LIMIT` This allows you to adjust the BFS depth level of links to visit. If you set it to `0` it will run until there are no more links.

2. `PUBLISH_DATE_START` This is the start date you can set for range of PDFs grabbed from filepage tables. Must be in a format like so "2022-01-01T00:00:00Z".

## Embeddings
1. Ensure the repository contains a .env file.
2. Ensure that scrapy returned an output.json file under `./data`.
3. Run `python populate_db.py` to ensure that embeddings are created

## Testing
1. Ensure that the website is running on [localhost:3000](http://localhost:3000)
2. Run `python ragas_testing [INPUT_FILE.json] [OUTPUT_DIR]`
    1. `input_file`: Input JSON filename located in ./testing_data/'
    2. `output_dir`: Output directory name under ./testing_data/'