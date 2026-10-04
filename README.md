# WebMiner

> Command-line web scraping and search utility for learning and small, authorized data-collection tasks.

## Features

- Scrape a URL and extract page title, metadata, paragraphs, headings, links, and image sources
- Filter extracted content by keyword
- Export content as JSON, CSV, or TXT
- Download images found on a page
- Optional Google-search integration through `googlesearch-python`
- Interactive and command-line modes
- Retry handling for HTTP requests
- Timestamped exports and in-memory command history

## Installation

Python 3.8+ is recommended.

```bash
python -m pip install requests beautifulsoup4 colorama tqdm googlesearch-python
```

## Usage

Interactive mode:

```bash
python WebMiner.py
```

Scrape and export:

```bash
python WebMiner.py --url https://example.com --format json --headless
```

Filter extracted content:

```bash
python WebMiner.py --url https://example.com --format txt --filter python --headless
```

Download page images:

```bash
python WebMiner.py --url https://example.com --download-images --output example --headless
```

Search:

```bash
python WebMiner.py --search "python tutorials"
```

## Responsible use

Only scrape websites and resources you are permitted to access. Respect applicable terms, robots policies, rate limits, copyright, privacy requirements, and other restrictions.

This is a learning utility, not a guarantee that a particular website permits automated collection.

## Current limitations

- Static HTML is parsed; JavaScript-rendered content is not executed.
- URL checking is format-oriented and does not establish that a target is safe or permitted to access.
- Image downloads use remote responses directly and should be treated cautiously, especially for untrusted targets.
- Search behavior depends on the optional third-party search package and service availability.
- There is no persistent database or distributed crawling system.
- The image downloader's URL handling is intentionally simple and is not a full URL-resolution/crawling implementation.

## Testing

The current automated test file covers the URL-validation helper:

```bash
python -m unittest discover -s tests
```

A GitHub Actions workflow also runs the test/syntax checks.

## Development

The scraper currently uses `requests` + BeautifulSoup for HTTP fetching and HTML parsing. Retries are built into the request helper, while interactive features and export formats remain in the main script.

## License

See [LICENSE](LICENSE).
