#!/usr/bin/env python3
# WebMiner v1.0 - Enhanced Web Scraper/Searcher
# FINAL FIXED VERSION - Colorama init order fixed

import os
import sys
import time
import json
import csv
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from datetime import datetime
from typing import Optional, List, Dict

# Initialize colorama FIRST before any colored output
from colorama import Fore, Style, init
init(autoreset=True)

try:
    from tqdm import tqdm
except ImportError:
    # Fallback if tqdm not available
    def tqdm(iterable, desc="Progress"):
        return iterable

# Try multiple import methods for googlesearch
search = None
GOOGLESEARCH_AVAILABLE = False

try:
    # Method 1: Standard import
    from googlesearch import search
    GOOGLESEARCH_AVAILABLE = True
    print(Fore.GREEN + "[✓] Google search module loaded successfully" + Style.RESET_ALL)
except ImportError:
    try:
        # Method 2: Import module then get function
        import googlesearch
        if hasattr(googlesearch, 'search'):
            search = googlesearch.search
            GOOGLESEARCH_AVAILABLE = True
            print(Fore.GREEN + "[✓] Google search module loaded (method 2)" + Style.RESET_ALL)
    except ImportError:
        pass

if not GOOGLESEARCH_AVAILABLE:
    print(Fore.YELLOW + "[!] Google search unavailable. Install: pip install googlesearch-python" + Style.RESET_ALL)

BANNER1 = '''
░██╗░░░░░░░██╗███████╗██████╗░███╗░░░███╗██╗███╗░░██╗███████╗██████╗░
░██║░░██╗░░██║██╔════╝██╔══██╗████╗░████║██║████╗░██║██╔════╝██╔══██╗
░╚██╗████╗██╔╝█████╗░░██████╦╝██╔████╔██║██║██╔██╗██║█████╗░░██████╔╝
░░████╔═████║░██╔══╝░░██╔══██╗██║╚██╔╝██║██║██║╚████║██╔══╝░░██╔══██╗
░░╚██╔╝░╚██╔╝░███████╗██████╦╝██║░╚═╝░██║██║██║░╚███║███████╗██║░░██║
░░░╚═╝░░░╚═╝░░╚══════╝╚═════╝░╚═╝░░░░░╚═╝╚═╝╚═╝░░╚══╝╚══════╝╚═╝░░╚═╝
'''

BANNER2 = '''
        WebMiner v1.0 - Web Scraping & Search Tool
'''

HISTORY = []

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    """Display the WebMiner banner"""
    print(Fore.CYAN + BANNER1 + Style.RESET_ALL)
    print(Fore.MAGENTA + BANNER2 + Style.RESET_ALL)

def is_valid_url(url):
    """Validate URL format"""
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc])

def retry_request(url, retries=3, delay=2):
    """Make HTTP request with retry logic"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(Fore.RED + f"[!] Attempt {attempt+1} failed: {str(e)}" + Style.RESET_ALL)
            if attempt < retries - 1:
                print(Fore.YELLOW + f"[*] Retrying in {delay} seconds..." + Style.RESET_ALL)
                time.sleep(delay)
    raise requests.RequestException("Max retries exceeded")

def print_filtered_matches(content, keyword):
    """Filter and display content matching keyword"""
    matches = [line for line in content if keyword.lower() in line.lower()]
    print(Fore.CYAN + f"\n{'='*60}" + Style.RESET_ALL)
    print(Fore.CYAN + f"Filtered Results ({len(matches)} matches for '{keyword}'):" + Style.RESET_ALL)
    print(Fore.CYAN + f"{'='*60}" + Style.RESET_ALL)
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match[:200]}...")

def export_content(content: List[str], export_format: str, output_name: Optional[str]):
    """Export scraped content to file"""
    name = output_name or "mined_content"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if export_format == 'json':
        filename = f"{name}_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump({"data": content, "timestamp": timestamp, "count": len(content)}, f, indent=2)
        print(Fore.BLUE + f"[+] Content saved to {filename}" + Style.RESET_ALL)
    elif export_format == 'csv':
        filename = f"{name}_{timestamp}.csv"
        with open(filename, "w", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Index", "Content", "Length"])
            for idx, row in enumerate(content, 1):
                writer.writerow([idx, row, len(row)])
        print(Fore.BLUE + f"[+] Content saved to {filename}" + Style.RESET_ALL)
    elif export_format == 'txt':
        filename = f"{name}_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"WebMiner Export - {timestamp}\n")
            f.write(f"{'='*60}\n\n")
            f.write("\n\n".join([f"[{i}] {item}" for i, item in enumerate(content, 1)]))
        print(Fore.BLUE + f"[+] Content saved to {filename}" + Style.RESET_ALL)

def export_summary(url: str, title: str, description: str, keywords: str, counts: Dict[str, int], output_name: Optional[str]):
    """Export page summary as JSON"""
    summary = {
        "url": url,
        "title": title,
        "meta_description": description,
        "meta_keywords": keywords,
        "element_counts": counts,
        "timestamp": datetime.utcnow().isoformat(),
        "mined_by": "WebMiner v1.0"
    }
    name = output_name or "mined_content"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_summary_{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(Fore.BLUE + f"[+] Summary saved to {filename}" + Style.RESET_ALL)

def download_images(images, base_url: str):
    """Download all images from a webpage"""
    if not images:
        print(Fore.YELLOW + "[!] No images found to download." + Style.RESET_ALL)
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    img_dir = f"images_{timestamp}"
    os.makedirs(img_dir, exist_ok=True)
    
    successful = 0
    for img in tqdm(images, desc="Downloading images"):
        src = img.get('src')
        if not src: 
            continue
        
        # Handle relative URLs
        if src.startswith('//'):
            img_url = 'https:' + src
        elif src.startswith(('http://', 'https://')):
            img_url = src
        else:
            img_url = base_url.rstrip('/') + '/' + src.lstrip('/')
        
        try:
            img_data = requests.get(img_url, timeout=10).content
            filename = os.path.basename(src.split('?')[0]) or f"image_{successful}.jpg"
            filepath = os.path.join(img_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(img_data)
            successful += 1
        except Exception:
            continue
    
    print(Fore.GREEN + f"[+] Downloaded {successful}/{len(images)} images to {img_dir}/" + Style.RESET_ALL)

def scrape_url(url, **kwargs):
    """Main web scraping function"""
    HISTORY.append({'type':'scrape', 'url':url, 'time':datetime.now().isoformat()})
    
    if not is_valid_url(url):
        print(Fore.RED + "[!] Invalid URL format. Use format: https://example.com" + Style.RESET_ALL)
        return
    
    print(Fore.CYAN + f"\n[*] Scraping: {url}" + Style.RESET_ALL)
    
    try:
        response = retry_request(url)
    except Exception as e:
        print(Fore.RED + f"[!] Error fetching URL: {e}" + Style.RESET_ALL)
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    content = []
    
    # Extract title and meta information
    title = soup.title.string.strip() if soup.title else "(No Title Found)"
    meta_desc = soup.find("meta", attrs={"name":"description"})
    meta_keywords = soup.find("meta", attrs={"name":"keywords"})
    
    desc = meta_desc["content"].strip() if meta_desc and meta_desc.get("content") else "(No Meta Description)"
    keywords = meta_keywords["content"].strip() if meta_keywords and meta_keywords.get("content") else "(No Meta Keywords)"
    
    # Display page info
    print(Fore.MAGENTA + f"\n{'='*60}" + Style.RESET_ALL)
    print(Fore.MAGENTA + f"Page Title: {title}" + Style.RESET_ALL)
    print(Fore.MAGENTA + f"Meta Description: {desc[:100]}..." + Style.RESET_ALL)
    print(Fore.MAGENTA + f"{'='*60}" + Style.RESET_ALL)
    
    # Extract all elements
    paragraphs = soup.find_all('p')
    links = soup.find_all('a')
    headings = soup.find_all(['h1','h2','h3','h4','h5','h6'])
    images = soup.find_all('img')
    
    # Extract text from paragraphs
    text_data = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
    content.extend(text_data)
    
    # Display text content (limited)
    if text_data:
        print(Fore.GREEN + f"\n--- Page Text (showing first 5) ---" + Style.RESET_ALL)
        for i, t in enumerate(text_data[:5], 1):
            print(f"{i}. {t[:150]}...")
        if len(text_data) > 5:
            print(Fore.YELLOW + f"... and {len(text_data)-5} more paragraphs" + Style.RESET_ALL)
    
    # Extract and display headings
    if headings:
        print(Fore.GREEN + f"\n--- Headings ({len(headings)} found) ---" + Style.RESET_ALL)
        for i, h in enumerate(headings[:10], 1):
            h_text = h.get_text(strip=True)
            if h_text: 
                print(f"{h.name.upper()}: {h_text}")
                content.append(f"{h.name}: {h_text}")
    
    # Extract links
    if links:
        print(Fore.GREEN + f"\n--- Links (showing first 10 of {len(links)}) ---" + Style.RESET_ALL)
        for link in links[:10]:
            href = link.get('href')
            if href and href.startswith('http'):
                print(f"  → {href}")
                content.append(href)
    
    # Image sources
    if images:
        print(Fore.GREEN + f"\n--- Images ({len(images)} found) ---" + Style.RESET_ALL)
        for i, img in enumerate(images[:5], 1):
            src = img.get('src')
            alt = img.get('alt', 'No alt text')
            if src: 
                print(f"{i}. {src[:80]}... (alt: {alt[:30]})")
                content.append(src)
    
    # Summary statistics
    counts = {
        'paragraphs': len(paragraphs), 
        'headings': len(headings), 
        'links': len(links), 
        'images': len(images)
    }
    print(Fore.CYAN + f"\n{'='*60}" + Style.RESET_ALL)
    print(Fore.CYAN + "Summary Statistics:" + Style.RESET_ALL)
    print(Fore.CYAN + f"  • Paragraphs: {counts['paragraphs']}" + Style.RESET_ALL)
    print(Fore.CYAN + f"  • Headings: {counts['headings']}" + Style.RESET_ALL)
    print(Fore.CYAN + f"  • Links: {counts['links']}" + Style.RESET_ALL)
    print(Fore.CYAN + f"  • Images: {counts['images']}" + Style.RESET_ALL)
    print(Fore.CYAN + f"{'='*60}\n" + Style.RESET_ALL)
    
    # Export summary
    export_summary(url, title, desc, keywords, counts, kwargs.get('output'))
    
    # Download images
    if kwargs.get('download_images', False) or (not kwargs.get('headless', False) and input("\nDownload all images? (y/n): ").strip().lower()=='y'):
        download_images(images, url)
    
    # Filter content
    if 'filter' in kwargs and kwargs['filter']:
        print_filtered_matches(content, kwargs['filter'])
    elif not kwargs.get('headless', False):
        keyword_search = input("\nEnter keyword to filter content (or press Enter to skip): ").strip()
        if keyword_search:
            print_filtered_matches(content, keyword_search)
    
    # Export content
    if content:
        fmt = kwargs.get('format') or ("skip" if kwargs.get('headless', False) else input("\nSave content? (json/csv/txt/skip): ").strip().lower())
        if fmt in ['json','csv','txt']:
            export_content(content, fmt, kwargs.get('output'))

def search_term(term):
    """Perform Google search"""
    if not GOOGLESEARCH_AVAILABLE or search is None:
        print(Fore.RED + "[!] Google search is unavailable." + Style.RESET_ALL)
        print(Fore.YELLOW + "[!] Install with: pip install googlesearch-python" + Style.RESET_ALL)
        print(Fore.YELLOW + "[!] If already installed, try: pip uninstall googlesearch-python && pip install googlesearch-python" + Style.RESET_ALL)
        return
    
    print(Fore.CYAN + f"\n{'='*60}" + Style.RESET_ALL)
    print(Fore.CYAN + f"Google Search Results for: '{term}'" + Style.RESET_ALL)
    print(Fore.CYAN + f"{'='*60}\n" + Style.RESET_ALL)
    
    try:
        results = list(search(term, num_results=20))
        if not results:
            print(Fore.YELLOW + "[i] No results found." + Style.RESET_ALL)
            return
        
        for i, result in enumerate(results, start=1):
            print(f"{i:2}. {result}")
        
        print(Fore.CYAN + f"\n{'='*60}" + Style.RESET_ALL)
        save = input("\nSave results to file? (y/n): ").strip().lower()
        if save == 'y':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_results_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Google Search: {term}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"{'='*60}\n\n")
                f.write("\n".join([f"{i}. {r}" for i, r in enumerate(results, 1)]))
            print(Fore.BLUE + f"[+] Results saved to {filename}" + Style.RESET_ALL)
        
    except Exception as e:
        print(Fore.RED + f"[!] Error during search: {e}" + Style.RESET_ALL)

def show_history():
    """Display command history"""
    if not HISTORY:
        print(Fore.YELLOW + "\n[i] No history yet." + Style.RESET_ALL)
        return
    
    print(Fore.YELLOW + f"\n{'='*60}" + Style.RESET_ALL)
    print(Fore.YELLOW + "Command History" + Style.RESET_ALL)
    print(Fore.YELLOW + f"{'='*60}" + Style.RESET_ALL)
    for i, entry in enumerate(HISTORY, 1):
        entry_type = entry['type'].capitalize()
        target = entry.get('url', '') or entry.get('term', '')
        timestamp = entry['time'].split('T')[1].split('.')[0] if 'T' in entry['time'] else entry['time']
        print(f"{i:2}. [{entry_type}] {target} @ {timestamp}")
    print(Fore.YELLOW + f"{'='*60}\n" + Style.RESET_ALL)

def show_help():
    """Display help information"""
    help_text = f"""
{Fore.CYAN}{'='*60}
WebMiner v1.0 - Help & Usage Guide
{'='*60}{Style.RESET_ALL}

{Fore.GREEN}INTERACTIVE MENU OPTIONS:{Style.RESET_ALL}
  [1] Scrape URL       - Extract content from any webpage
  [2] Google Search    - Search Google and get top results  
  [3] Show History     - View your command history
  [h] Help            - Show this help message
  [c] Clear Screen    - Clear terminal and show banner
  [x] Exit            - Exit WebMiner

{Fore.GREEN}COMMAND-LINE ARGUMENTS:{Style.RESET_ALL}
  --url URL                 Scrape specified URL
  --search TERM            Perform Google search
  --format {{json,csv,txt}}  Export format
  --download-images        Download all images from page
  --output NAME            Output filename (without extension)
  --filter KEYWORD         Filter content by keyword
  --headless               Non-interactive mode
  --log PATH               Save terminal output to file

{Fore.GREEN}EXAMPLES:{Style.RESET_ALL}
  python WebMiner.py --url https://example.com --format json
  python WebMiner.py --search "python tutorials" 
  python WebMiner.py --url https://site.com --download-images --output mydata

{Fore.GREEN}DEPENDENCIES:{Style.RESET_ALL}
  pip install requests beautifulsoup4 colorama tqdm googlesearch-python

{Fore.CYAN}{'='*60}{Style.RESET_ALL}
"""
    print(help_text)

def main_menu():
    """Main interactive menu"""
    banner()
    print(Fore.GREEN + "[*] Type 'h' for help and usage guide" + Style.RESET_ALL)
    
    while True:
        print(f"\n{Fore.YELLOW}[1]{Style.RESET_ALL} Scrape URL  {Fore.YELLOW}[2]{Style.RESET_ALL} Google Search  {Fore.YELLOW}[3]{Style.RESET_ALL} Show History")
        print(f"{Fore.YELLOW}[h]{Style.RESET_ALL} Help  {Fore.YELLOW}[c]{Style.RESET_ALL} Clear Screen  {Fore.YELLOW}[x]{Style.RESET_ALL} Exit")
        
        choice = input(f"\n{Fore.CYAN}[?]{Style.RESET_ALL} ").strip().lower()
        
        if choice == '1':
            url = input(f"{Fore.GREEN}Enter URL to scrape: {Style.RESET_ALL}").strip()
            if url:
                scrape_url(url)
        elif choice == '2':
            term = input(f"{Fore.GREEN}Enter search term: {Style.RESET_ALL}").strip()
            if term:
                HISTORY.append({'type':'search', 'term':term, 'time':datetime.now().isoformat()})
                search_term(term)
        elif choice == '3':
            show_history()
        elif choice == 'h':
            show_help()
        elif choice == 'c':
            clear_screen()
            banner()
        elif choice == 'x':
            print(Fore.MAGENTA + "\n[x] Exiting WebMiner... Goodbye!" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "[!] Invalid option. Type 'h' for help." + Style.RESET_ALL)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='WebMiner v1.0 - Advanced Web Scraper and Search Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python WebMiner.py --url https://example.com --format json
  python WebMiner.py --search "web scraping" --output results
  python WebMiner.py --url https://site.com --download-images
        """
    )
    parser.add_argument('--url', help='Scrape specified URL')
    parser.add_argument('--search', help='Google Search for a term')
    parser.add_argument('--format', choices=['json','csv','txt'], help='Export format')
    parser.add_argument('--download-images', action='store_true', help='Download all images from page')
    parser.add_argument('--output', help='Output file name base (without extension)')
    parser.add_argument('--filter', help='Keyword to filter content')
    parser.add_argument('--headless', action='store_true', help='Non-interactive mode')
    parser.add_argument('--log', help='Path for terminal log output')
    args = parser.parse_args()
    
    if args.log:
        sys.stdout = open(args.log, 'w', encoding='utf-8')
        sys.stderr = sys.stdout
    
    if args.url:
        scrape_url(args.url, format=args.format, download_images=args.download_images, 
                   output=args.output, filter=args.filter, headless=args.headless)
        sys.exit()
    elif args.search:
        search_term(args.search)
        sys.exit()
    else:
        main_menu()
