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
    time.sleep(20)
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
    total_width = driver.execute_script('return document.body.offsetWidth')
    total_height = driver.execute_script('return document.querySelector("#content-container > div:nth-child(5) > div > div > div.rp-report-container-preview").parentNode.scrollHeight')
    viewport_width = driver.execute_script('return document.querySelector("#content-container > div:nth-child(5) > div > div > div.rp-report-container-preview").clientWidth')
    viewport_height = driver.execute_script("return window.innerHeight")

    rectangles = []

    i = 0
    while i < total_height:
        ii = 0
        top_height = i + viewport_height

        if top_height > total_height:
            top_height = total_height

        while ii < total_width:
            top_width = ii + viewport_width

            if top_width > total_width:
                top_width = total_width

            rectangles.append((ii, i, top_width, top_height))

            ii = ii + viewport_width

        i = i + viewport_height

    previous = None
    part = 0

    print(len(rectangles))
    for rectangle in rectangles:
        if not previous is None:
            driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
            time.sleep(0.5)
        # time.sleep(0.2)

        if rectangle[1] + viewport_height > total_height:
            offset = (rectangle[0], total_height - viewport_height)
        else:
            offset = (rectangle[0], rectangle[1])

        previous = rectangle

    return (total_height, total_width)

if __name__ == "__main__":
    #open_url("https://danam.cats.uni-heidelberg.de/report/e7151050-eb4e-11e9-b125-0242ac130002")
    
    img = Image.open("screen.png").convert("RGB")
    
    w, h = img.size
    pages = []
    page_height = 841 # page height in pixels
    top_y = 0
    for i in range(0, h//page_height + 1):
        bottom_y = top_y + page_height
        page_i = img.crop((0, top_y, w, bottom_y))
        #page_i.convert("RGB")
        pages.append(page_i)
        top_y = bottom_y
        
    pages[0].save("test.pdf", save_all=True, append_images=pages[1:])
        
