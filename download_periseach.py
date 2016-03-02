import re
import urllib2
from pyvirtualdisplay import Display
from selenium import webdriver
import youtube_dl

ydl_opts = {
    'format': 'bestvideo/best',
    'sanitize_filename': True,
    'prefer_ffmpeg': True,
    'writeinfojson': True,
    'verbose': True,
    'hls_prefer_native': True
    #'logger': MyLogger()
    #'progress_hooks': [my_hook],
}

def replace_extension(filename, ext, expected_real_ext=None):
    name, real_ext = os.path.splitext(filename)
    return '{0}.{1}'.format(
        name if not expected_real_ext or real_ext[1:] == expected_real_ext else filename,
        ext)

    
def get_metadata(url, filename):

    watch_urls = []
    try:
        html_doc = urllib2.urlopen(url).readlines()

    except urllib2.URLError, e:
        # For Python 2.7
        print 'URLError %r' % e
        return

    except socket.timeout, e:
        # For Python 2.7
        print 'Timeout %r' % e
        return

    with open(filename, 'w') as fh:
        for line in html_doc:
            fh.write(line)
         

def parse_perisearch():
    url = 'http://www.perisearch.net/'

    broadcast_ids =[]
    try:
        display = Display(visible=0, size=(1024, 768))
        display.start()

        driver= webdriver.Firefox()
        driver.get(url)
        page_source = driver.page_source
        page_source = str(page_source.encode('utf-8'))
        urls = []
        chunks = []
        segs = page_source.split('<div onmouseout="this.className=\'gallery_item\';" onmouseover="this.className=\'gallery_item hover\';" class="gallery_item">')
        chunks += [segs[0].split('<div onmouseout="this.className=\'gallery_item\';" onmouseover="this.className=\'gallery_item hover\';" class="gallery_item hover">')[1]]
        for seg in segs[1:]:
            chunks += [seg]
        for seg in chunks:
            #print seg
            #<a href="/w/1YpKkaOvwzVJj">
            m = re.search(r'<a href="([A-Za-z0-9_/]+)', seg)
            print  m.group(1)
            broadcast_ids += [m.group(1)]
        driver.quit()
        display.stop()

    except:
        return

    return broadcast_ids

def download_video(urls):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            try:
                get_metadata(url, 'tmp')
                ret, ress = ydl.download([url])
                metadata_fname = ress[0]['title'] + '-' + ress[0]['id'] + '.metadata'
		print 'metadata_name:', metadata_fname
            except:
                print 'Download Error'
                continue

def download_videos(ids):
  
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for bid in ids:
            url = 'https://www.periscope.tv' + bid
            #get_metadata(url, 'tmp')
            try: 
                print url
                ret = ydl.download([url])
   
            except:
                print 'Download Error'
                continue

if __name__ == "__main__":

    #with closing(Firefox()) as browser:
    #    browser.get(url)
        #button = browser.find_element_by_name('button')
        #button.click()
        # wait for the page to load
        #WebDriverWait(browser, timeout=10).until(lambda x: x.find_element_by_id('someId_that_must_be_on_new_page'))
        # store it to string variable
    #    page_source = browser.page_source
    #print(page_source)

    broadcast_ids = parse_perisearch()
    download_videos(broadcast_ids)
