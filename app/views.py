from django.shortcuts import render

from django.conf import settings 
from django.conf.urls.static import static

import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse

from urllib.parse import urljoin

import logging

# Create your views here.

def home(request):
    return render(request, 'home.html')

# extract external resources
def extract_external_resources(soup, tag_name, attr_name, base_url):
    """Extracts URLs of external resources like CSS and JS files."""
    resources = []
    tags = soup.find_all(tag_name)
    for tag in tags:
        resource_url = tag.get(attr_name)
        if resource_url:
            # Check if the URL is relative
            if not resource_url.startswith(('http://', 'https://')):
                # Construct absolute URL using base URL and relative URL
                resource_url = urljoin(base_url, resource_url)
            resources.append(resource_url)
    return resources

# fetch external resources
def fetch_external_resources(resource_urls):
    """Fetches content of external resources."""
    content = {}
    for url in resource_urls:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for non-2xx status codes
            content[url] = response.text
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 406:
                logging.error(f"Failed to fetch resource from {url}: Server returned status code 406 (Not Acceptable)")
            else:
                logging.error(f"Failed to fetch resource from {url}: {e}")
        except Exception as e:
            logging.error(f"Failed to fetch resource from {url}: {e}")
    return content

# generate codes
def generate_codes(request):
    if request.method == 'POST':
        website_link = request.POST.get('website_link')
        try:
            response = requests.get(website_link)
            if response.status_code == 200:
                html_content = response.text
                # Parse HTML content
                soup = BeautifulSoup(html_content, 'html.parser')
                # Extract HTML
                html_code = soup.prettify()
                # Extract inline CSS
                css_code = ''
                style_tags = soup.find_all('style')
                for style_tag in style_tags:
                    if style_tag.string:  # Check if style_tag.string is not None
                        css_code += style_tag.string + '\n'
                # Extract inline JavaScript
                js_code = ''
                script_tags = soup.find_all('script')
                for script_tag in script_tags:
                    if script_tag.string:
                        js_code += script_tag.string + '\n'
                # Extract external CSS and JS
                base_url = website_link  # Base URL of the website
                external_css_urls = extract_external_resources(soup, 'link', 'href', base_url)
                external_js_urls = extract_external_resources(soup, 'script', 'src', base_url)
                # Fetch content of external resources
                external_css_content = fetch_external_resources(external_css_urls)
                external_js_content = fetch_external_resources(external_js_urls)
                # Return JSON response with generated code
                return JsonResponse({
                    'html_code': html_code,
                    'css_code': css_code,
                    'js_code': js_code,
                    'external_css_content': external_css_content,
                    'external_js_content': external_js_content
                })
            else:
                return JsonResponse({'error_message': f'Failed to fetch website content. Server returned status code: {response.status_code}'}, status=400)
        except requests.exceptions.SSLError as e:
            return JsonResponse({'error_message': f'SSL Error: {str(e)}'}, status=400)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error_message': f'Request Error: {str(e)}'}, status=400)
    else:
        return render(request, 'home.html')
    
# error page
def error_page(request):
    return render(request, 'error_page.html')
