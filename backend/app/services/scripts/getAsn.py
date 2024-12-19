from tld import get_tld
import sys
import requests
from bs4 import BeautifulSoup
import os
import subprocess

bgpUrl = "https://bgp.he.net/search?search%5Bsearch%5D="

def getAsn(domain):
    
    url = "https://" + domain
    urlObj = get_tld(url, as_object=True)

    print(f"Domain: {urlObj.domain}")
    print(f"Requesting to {bgpUrl}{urlObj.domain}")
    
    response = requests.get(f"{bgpUrl}{urlObj.domain}")
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find all ASN tags
    asns = soup.find_all('a', href=True)
    asnNumbers = []
    # Extract the ASN numbers
    for asn in asns:
        href = asn['href']
        if href.startswith('/AS'):
            asnNumber = href.split('/')[1]
            asnNumbers.append(asnNumber)
    # Write the ASN numbers to a file in the corresponding directory
    with open('asn.txt', 'a') as asnFile:
        for number in asnNumbers:
            print(f"ASN Number for {urlObj.domain}: {number}")
            asnFile.write(f"{number}\n")
                

if __name__ == "__main__":
    getAsn(sys.argv[1])
   

