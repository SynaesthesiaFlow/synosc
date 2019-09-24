# needs checkpointing
from bs4 import BeautifulSoup
import urllib.request
import rarfile
import requests, io


CHECKPOINT_PATH = "/Users/davisdulin/src/synosc/data/phish-checkpoint"
curr_checkpoint = "https://www.google.com/url?q=http://www.mediafire.com/download/yvi8av9c32c8dd9/1990-01-28_-_The_Front_-_Burlington%252C_VT.rar&sa=D&ust=1569280314653000&usg=AFQjCNGTr88AfDbeoCd2I9smbdPvGmSoNw"

def write_checkpoint(last_dl_link):
    with open(CHECKPOINT_PATH, "w") as f:
        f.write(str(last_dl_link))

def read_checkpoint():
    # with open(CHECKPOINT_PATH, "r") as f:
    #         last_dl_link = f.readlines()
    # print("last dl linke: " + str(last_dl_link))
    # return last_dl_link.strip("\n")
    return curr_checkpoint

def get_remaining_download_links(download_links):
    last_dl_link = read_checkpoint()
    for i, l in enumerate(download_links):
        if l == last_dl_link:
            return download_links[i:]
    return None


def scrape_download_links():
    with open("../downloads.html") as f:
        html_docs_list = f.readlines()
    all_download_refs = []
    for html_doc in html_docs_list:
        soup = BeautifulSoup(html_doc, 'html.parser')
        refs = soup.find_all('a')
        download_refs = [r for r in refs if "download link" in r]
        all_download_refs.extend(download_refs)  # want refs with "download link"   
    download_links = [l.get('href') for l in all_download_refs]
    print(f"length of dl links: {len(download_links)}")
    write_download_links(download_links)
    return download_links


def scrub(dl):
    """
    cut beginning: "https://www.google.com/url?q="
    cut after: ".rar" 
    """
    scrub1 = dl[29:]
    scrub2 = scrub1.split("&")[0]
    return scrub2

def download_rar(rar_url):
    r = requests.get(rar_url, stream=True)
    rf = rarfile.RarFile(io.BytesIO(r.content))
    root_path = "/Users/davisdulin/src/synosc/data/jams"
    rf.extractall(root_path)

def get_download_links():
    with open("/Users/davisdulin/src/synosc/data/download_links", "r") as f:
        list_in = f.readlines()
    download_links = [l.strip("\n") for l in list_in]
    print(f"dl length: {len(download_links)}")
    return download_links

def write_download_links(download_links):
    with open("/Users/davisdulin/src/synosc/data/download_links", "w") as f:
        f.write("\n".join(download_links))

def is_set():
    l1 = scrape_download_links()
    b = len(l1) == len(set(l1))
    print(f"is set: {b}")


def execute():
    # download_links = scrape_download_links()
    download_links = get_download_links()
    # TODO: remove duplicates
    remaining_download_links = get_remaining_download_links(download_links)
    print(f"remaining links ot download: {len(remaining_download_links)}/{len(download_links)}")
    for link in remaining_download_links:
        scrubbed_link = scrub(link)
        print("download: " + str(scrubbed_link))
        download_rar(scrubbed_link)


execute()