import urllib2
import youtube_dl

ydl_opts = {
    'format': 'bestvideo/best',
    'sanitize_filename': True,
    'prefer_ffmpeg': True,
    'writeinfojson': True,
    'verbose': True
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
while True:
	response = urllib2.urlopen("http://periscope.tv/couchmode")
	html = response.read()
	segs = html.split('content="https://periscope.tv')
	matching_seg = []
	for seg in segs:
		if seg.find('"><meta propert') >= 0:
			#print seg
			matching_seg += [seg]
			#print ''
	video_url= 'https://periscope.tv' + matching_seg[-2].split('"><meta propert')[0]
	print video_url

	download_video([video_url])
