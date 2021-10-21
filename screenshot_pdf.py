import time
from PIL import Image
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def open_url(url):
    options = Options()

    options.headless = True

    driver = webdriver.Chrome(chrome_options=options)

    driver.maximize_window()
    driver.get(url)
    time.sleep(60)
    save_screenshot(driver, 'screen.png')

def save_screenshot(driver, file_name):
    height, width = scroll_down(driver)
    print(height, width)
    driver.set_window_size(width, height)
    img_binary = driver.get_screenshot_as_png()
    img = Image.open(BytesIO(img_binary))
    img.save(file_name)
    # print(file_name)
    print(" screenshot saved ")

def scroll_down(driver):
    total_width = driver.execute_script('return document.body.offsetWidth')+150
    total_height = driver.execute_script('return document.querySelector("#content-container > div:nth-child(5) > div > div > div.rp-report-container-preview").parentNode.scrollHeight')
    return (total_height, total_width)

if __name__ == "__main__":
    print("getting image")
    open_url("https://danam.cats.uni-heidelberg.de/report/d62e32fe-b78c-43af-817c-edb16e6d7ae8")
    print("image saved")
    img = Image.open("screen.png").convert("RGB")
    
    w, h = img.size
    pages = []
    page_height = 1838 # page height in pixels, using DINA4 ratio
    top_y = 0
    for i in range(0, h//page_height):
        bottom_y = top_y + page_height
        page_i = img.crop((0, top_y, w, bottom_y))
        #page_i.convert("RGB")
        pages.append(page_i)
        top_y = bottom_y
    
    last_page_height = h - (1838*(h//page_height))
    last_page = img.crop((0, top_y, w, h))
    pages.append(last_page)

    pages[0].save("test.pdf", save_all=True, append_images=pages[1:])
        
