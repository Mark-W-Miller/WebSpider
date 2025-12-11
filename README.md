# WebSpider

Small utility that takes a starting URL, follows every link on that page (one level deep only), pulls the readable text from each linked page, and writes the results into a single text file. Each section in the output starts with the link URL on its own line, followed by the extracted text.

## Setup

```bash
python3 -m pip install -r requirements.txt
```

## Usage

```bash
python3 web_spider.py https://example.com -o output.txt
```

- The script fetches only the links found on the starting page; it does not follow links from those linked pages.
- Non-HTML links are skipped with a note in the output.
- Output defaults to `web_spider_output.txt` if `-o/--output` is omitted.
