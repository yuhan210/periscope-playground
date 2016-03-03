import traceback
import os
import time
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

    
## get new video name without extension
def getNewVideoName(videoname):

    nstr = re.sub(r'[?|$|.|!]',r'', videoname)
    nestr = nestr = re.sub(r'[^a-zA-Z0-9 ]',r'',nstr)
    new_videoname = '_'.join([str(x).lower() for x in nestr.split(' ')])

    return new_videoname


def get_metadata(url, filename):

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
            #<a href="/w/1YpKkaOvwzVJj">
            m = re.search(r'<a href="([A-Za-z0-9_/]+)', seg)
            #print  m.group(1)
            broadcast_ids += [m.group(1)]
        driver.quit()
        display.stop()

    except:
        return

    return list(set(broadcast_ids))


def download_videos(ids, DEST_FOLDER = './videos'):
  
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        for bid in ids:
            url = 'https://www.periscope.tv' + bid
            #get_metadata(url, 'tmp')
            try: 
                ret, res = ydl.download([url])
                prefix = res['title'] + '-' + res['id']
                new_prefix = getNewVideoName(prefix) 

                get_metadata(url,  os.path.join(DEST_FOLDER, new_prefix + '.metadata'))

                files = [prefix + '.mp4', prefix  + '.info.json']
                new_files = [new_prefix + '.mp4', new_prefix  + '.info.json']

                for fid, f in enumerate(files):
                    if os.path.exists(f):
                        os.rename(f, os.path.join(DEST_FOLDER, new_files[fid]))

            except:
                print 'Error:', traceback.format_exc()
                continue

if __name__ == "__main__":

    DEST_FOLDER = './videos'
    while True:
        if len(os.listdir(DEST_FOLDER)) >= 5000 * 3 + 1000:
            break
        broadcast_ids = parse_perisearch()
        download_videos(broadcast_ids)
        time.sleep(2 * 60)
