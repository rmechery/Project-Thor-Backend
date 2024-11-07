# Project Thor Backend

Please note this documentation is a work in progress. 

This repository contains code to scrape data from the ISO website and store it in a JSON file. 

This repository also contains code to convert the raw data into vector embeddings and store it in the ISO Database. 

## `.env` Note
To grab the .env file go to: [Google Drive Link](https://drive.google.com/drive/folders/1sdEnDH9pb2lWvhiTuz8H8wDrXKsc2zvy?usp=sharing) and change the file from to a .txt to a dotfile.

## Package Installation
To install the required dependencies please install from the requirements.txt file

1. `cd /path/to/thorwebscraper/`
2. `pip install -r requirements.txt`

### Note
It is recommended to create a virtual environment like `venv` or `conda` to install these packages locally so they don't conflict with other packages.

## Web Scraper
To run the web scraper
1. `cd /path/to/thorwebscraper/` 
2. `cd isoscraper`
3. `scrapy crawl iso_main_spider -o output.json` You can name the output.json to whatever filename you want. 

### Customizing Settings
There are two settings you customize in the `isoscraper/isoscraper/settings.py` file.
1. `DEPTH_LIMIT` This allows you to adjust the BFS depth level of links to visit. If you set it to `0` it will run until there are no more links.

2. `PUBLISH_DATE_START` This is the start date you can set for range of PDFs grabbed from filepage tables. Must be in a format like so "2022-01-01T00:00:00Z".
