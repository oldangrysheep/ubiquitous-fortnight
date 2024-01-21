import os
import requests
from bs4 import BeautifulSoup
import csv
import os.path
import re

def get_download_links(url, valid_extensions):
    # Send a GET request to the specified URL
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all anchor tags with the 'href' attribute
        links = soup.find_all('a', href=True)
        
        # Extract the 'href' attribute and text from each anchor tag
        download_links = [(link['href'], link.text) for link in links if is_valid_link(link['href'], valid_extensions)]
        
        return download_links
    else:
        print(f"Error: Unable to fetch content from {url}")
        return None

def is_valid_link(link, valid_extensions):
    # Check if the link ends with a valid file extension
    return any(link.endswith(ext) for ext in valid_extensions)

def remove_extension(file_name):
    # Remove file extension from the file name
    return os.path.splitext(file_name)[0]

def extract_regions(link_text):
    # Extract region information using regular expression
    matches = re.findall(r'\((.*?)\)', link_text)
    return matches

def is_valid_combination(regions, valid_regions):
    # Check if the combination of regions is valid
    return all(region in valid_regions for region in regions)

def write_to_csv(file_path, website_url, data, valid_regions):
    # Write the data to a CSV file without headers
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write the filtered download links to the CSV file with the website URL prefix
        for row in data:
            link_href, link_text = row
            # Prepend the website URL followed by a slash to each link
            full_link = f"{website_url}/{link_href}"
            
            # Extract and remove region from link text
            regions = extract_regions(link_text)
            
            # Check if the combination of regions is valid, if not, skip this row
            if not is_valid_combination(regions, valid_regions):
                continue
            
            # Remove quotation marks from the content in the second column
            regions_without_quotes = [region.replace('"', '').replace("'", "") for region in regions]
            
            link_text_without_region = link_text
            for region in regions:
                link_text_without_region = link_text_without_region.replace(f"({region})", "")
            
            # Remove file extension from link text
            link_text_without_extension = remove_extension(link_text_without_region)
            
            # Write data row with columns arranged as described
            writer.writerow(["", ', '.join(regions_without_quotes), link_text_without_extension, full_link])

if __name__ == "__main__":
    # Get the directory of the Python script
    script_directory = os.path.dirname(os.path.realpath(__file__))
    
    # Get the website URL from the user
    website_url = input("Enter the URL of the website to parse: ")
    
    # Specify valid file extensions
    valid_extensions = ['.zip', '.nes', '.iso', '.z64']  # Add more extensions as needed
    
    # Specify valid regions
    valid_regions = ['USA', 'Japan', 'Europe', 'Australia', 'World', 'Spain', 'France', 'Korea']
    
    # Get the download links with link text
    download_links = get_download_links(website_url, valid_extensions)
    
    if download_links:
        # Create the CSV file path in the same directory as the script
        csv_file_path = os.path.join(script_directory, "download_links.csv")
        
        # Write the filtered download links to the CSV file with the website URL prefix
        write_to_csv(csv_file_path, website_url, download_links, valid_regions)
        
        print(f"Filtered download links with link text (without file extensions), region information, and column arrangement have been saved to {csv_file_path}")
    else:
        print("No download links found.")
