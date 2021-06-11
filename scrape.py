from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup
from tistory_info import *
import re
import time

date = str(datetime.today().month)+ "월" + str(datetime.today().day) + "일"

def createImage(filename,file_png):
    with open('image/{}_{}.png'.format(filename,date), 'wb') as f:
        f.write(file_png)

def scrapeData():

    # headless 옵션 설정
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36")

    url = 'https://sports.news.naver.com/kbaseball/schedule/index.nhn#'
    browser = webdriver.Chrome(options=options)
    browser.get(url)

    # 일정 테이블에서 한화 클릭하기
    browser.find_element_by_class_name('tab_team').find_element_by_link_text("한화").click()
    soup = BeautifulSoup(browser.page_source, "lxml")

    # 오늘 날짜의 경기 고르기 일단 day - 2로 보고 이후 -1로 수정
    today = datetime.today().day

    game = soup.find("div", attrs={"class":"tb_wrap"}).find_all("div", attrs={"class":re.compile("^sch_tb")})
    link = "https://sports.news.naver.com/" + game[today - 2].find("span", attrs={"class":"td_btn"}).find("a")["href"]

    browser.get(link)
    soup = BeautifulSoup(browser.page_source, "lxml")

    try:
        time.sleep(2)
        
        # 경기 결과 캡쳐 후 이미지 저장
        result = browser.find_element_by_class_name('Home_game_head__3EEZZ').screenshot_as_png
        recordGraph = browser.find_element_by_class_name('TeamVS_comp_team_vs__fpu3N').screenshot_as_png
        playerRecord = browser.find_element_by_class_name('PlayerRecord_record_table_group__2bRI3').screenshot_as_png

        createImage('result', result)
        createImage('recordGraph', recordGraph)
        createImage('playerRecord', playerRecord)

    finally:
        browser.quit()

