import urllib2
from pyvirtualdisplay import Display
from selenium import webdriver

#def parse_seg(seg):
    

def parse_perisearch():
    url = 'http://www.perisearch.net/'

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
            print seg
        driver.quit()
        display.stop()

    except:
        return

    return urls

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

    parse_perisearch()
