from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup
from tistory_info import *
import requests
import re
import time
import json

date = str(datetime.today().month)+ "월" + str(datetime.today().day) + "일"

# headless 옵션 설정
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument("window-size=1920x1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36")
    
browser = webdriver.Chrome(options=options)

def createImage(filename,file_png):
    with open('image/{}_{}.png'.format(filename,date), 'wb') as f:
        f.write(file_png)

def scrapeData():
    url = 'https://sports.news.naver.com/kbaseball/schedule/index.nhn#'
    browser.get(url)

    # 일정 테이블에서 한화 클릭하기
    browser.find_element_by_class_name('tab_team').find_element_by_link_text("한화").click()
    soup = BeautifulSoup(browser.page_source, "lxml")

    # 오늘 날짜의 경기 고르기
    today = datetime.today().day

    game = soup.find("div", attrs={"class":"tb_wrap"}).find_all("div", attrs={"class":re.compile("^sch_tb")})
    link = "https://sports.news.naver.com/" + game[today - 1].find("span", attrs={"class":"td_btn"}).find("a")["href"]

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

def uploadImage(filePath):
    files = {'uploadedfile': open(filePath, 'rb')}
    parameters = {
        'access_token': access_token,
        'blogName': blogName,
        'output': 'json'
    }
    rq = requests.post(upload_url, params=parameters, files=files)

    try:
        item = json.loads(rq.text)
    except:
        print("Upload Image Error")
    
    return item["tistory"]["replacer"]

def autoPosting():
    url = posting_url
    keyEnter = '<h3 data-ke-size="size23">&nbsp;</h3>'
    
    title = '{}의 야구 기록'.format(date)

    content = '<p style="text-align: right;" data-ke-size="size16">이 글은 python 프로그램에 의해 자동으로 업로드된 글입니다.</p>'
    content += keyEnter + keyEnter + keyEnter
    content += '<h3 data-ke-size="size23">경기 결과</h3>'+ keyEnter
    content += '<p>' + uploadImage('./image/result_{}.png'.format(date)) + '</p>'
    content += keyEnter + keyEnter + keyEnter
    content += '<h3 data-ke-size="size23">기록 그래프</h3>'+ keyEnter
    content += '<p>' + uploadImage('./image/recordGraph_{}.png'.format(date)) + '</p>'
    content += keyEnter + keyEnter + keyEnter
    content += '<h3 data-ke-size="size23">한화 선수단 기록</h3>'+ keyEnter
    content += '<p>' + uploadImage('./image/playerRecord_{}.png'.format(date)) + '</p>'
    content += keyEnter + keyEnter + keyEnter
    
    parameters = {
        'access_token': access_token,
        'output': '{output-type}',
        'blogName': blogName,
        'title': title,
        'content': content,
        'visibility': '3',
        'category': categoryId,
        'tag': '한화이글스',
    }

    requests.post(url, params=parameters)

scrapeData()
autoPosting()