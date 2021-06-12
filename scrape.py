from selenium import webdriver
from datetime import datetime
from bs4 import BeautifulSoup
from tistory_info import *
import requests
import re
import time
import json
import os
import shutil

date = str(datetime.today().month)+ "월" + str(datetime.today().day) + "일"
isDH = False # 더블헤더 경기

# headless 옵션 설정
options = webdriver.ChromeOptions()
options.headless = True
options.add_argument("window-size=1920x1080")
options.add_argument('--start-fullscreen')
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36")
    
browser = webdriver.Chrome(options=options)

def createImage(filename, file_png, num):
    if not isDH:
        with open('image/{}_{}.png'.format(filename,date), 'wb') as f:
            f.write(file_png)
    else:
        with open('image/{}_{}_{}.png'.format(filename,date,num), 'wb') as f:
            f.write(file_png)

def enterPage(link, num):
    browser.get(link)

    try:
        time.sleep(1)
        
        # 경기 결과 캡쳐 후 이미지 저장
        result = browser.find_element_by_class_name('Home_game_head__3EEZZ').screenshot_as_png
        recordGraph = browser.find_element_by_class_name('TeamVS_comp_team_vs__fpu3N').screenshot_as_png
        playerRecord = browser.find_element_by_class_name('PlayerRecord_record_table_group__2bRI3').screenshot_as_png

        createImage('result', result, num)
        createImage('recordGraph', recordGraph, num)
        createImage('playerRecord', playerRecord, num)
    except:
        print("Enter page Error")

def scrapeData():
    url = 'https://sports.news.naver.com/kbaseball/schedule/index.nhn#'
    browser.get(url)

    # 일정 테이블에서 한화 클릭하기
    browser.find_element_by_class_name('tab_team').find_element_by_link_text("한화").click()
    soup = BeautifulSoup(browser.page_source, "lxml")

    game = soup.find("div", attrs={"class":"tb_wrap"}).find_all("div", attrs={"class":re.compile("^sch_tb")})
    today = datetime.today().day
    global isDH 

    # 오늘 날짜에 더블헤더 일정이 있는지 체크
    if(game[today - 1].find("td", attrs={"rowspan":"2"}) == None):
        isDH = False
    else:
        isDH = True

    # 오늘 날짜의 경기 고르기
    if not isDH:
        link = "https://sports.news.naver.com/" + game[today - 1].find("span", attrs={"class":"td_btn"}).find("a")["href"]
        enterPage(link, 0)
    else:
        for i in range(0,2):
            link = "https://sports.news.naver.com/" + game[today - 1].find_all("span", attrs={"class":"td_btn"})[i].find_all("a")[0]["href"]
            enterPage(link, i + 1)
    
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
        
        # 정상 작동 확인
        print("Upload Image... status" + item["tistory"]["status"])
    except:
        print("Upload Image Error")
        # print(rq.text)
    
    return item["tistory"]["replacer"]

def createImgContent(imgName, imgNum):
    if isDH:
        content = '<p>' + uploadImage('./image/{}_{}_{}.png'.format(imgName, date, imgNum)) + '</p>'
    else:
        content = '<p>' + uploadImage('./image/{}_{}.png'.format(imgName, date)) + '</p>'
    return content

def postingResult():
    content = ''
    if isDH:
        for i in range(0, 2):
            content += '<h3 data-ke-size="size23">{}차전 경기 결과</h3>'.format(i + 1)+ keyEnter
            content += createImgContent('result', i + 1) + keyEnter
    else:
        content = '<h3 data-ke-size="size23">경기 결과</h3>'+ keyEnter
        content += createImgContent('result', 0) + keyEnter
    content += keyEnter
    
    return content

def postingGraph():
    content = ''
    if isDH:
        for i in range(0, 2):
            content += '<h3 data-ke-size="size23">{}차전 기록 그래프</h3>'.format(i + 1)+ keyEnter
            content += createImgContent('recordGraph', i + 1) + keyEnter
    else:
        content = '<h3 data-ke-size="size23">기록 그래프</h3>'+ keyEnter
        content += createImgContent('recordGraph', 0) + keyEnter
    content += keyEnter
    
    return content

def postingPlayerRecord():
    content = ''
    if isDH:
        for i in range(0, 2):
            content += '<h3 data-ke-size="size23">{}차전 한화 선수단 기록</h3>'.format(i + 1)+ keyEnter
            content += createImgContent('playerRecord', i + 1) + keyEnter
    else:
        content = '<h3 data-ke-size="size23">한화 선수단 기록</h3>'+ keyEnter
        content += createImgContent('playerRecord', 0) + keyEnter
    content += keyEnter
    
    return content

def autoPosting():
    url = posting_url
    global keyEnter 
    keyEnter = '<h3 data-ke-size="size23">&nbsp;</h3>'
    
    title = '{}의 야구 기록'.format(date)

    content = '<p style="text-align: right;" data-ke-size="size16">이 글은 python 프로그램에 의해 자동으로 업로드된 글입니다.</p>'
    content += keyEnter + keyEnter

    content += postingResult()
    content += postingGraph()
    content += postingPlayerRecord()
    
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

    rq = requests.post(url, params=parameters)
    try:
        posting = json.loads(rq.text)
        
        # 정상 작동 확인
        print("Posting... status" + posting["tistory"]["status"])
    except:
        print("Posting Error")
        # print(rq.text)

def createDirectory():
    try: 
        if not os.path.exists('image'):
            os.makedirs('image')
    except OSError:
        print('createDirectory Error')

def removeDirectory():
    try: 
        if os.path.exists('image'):
            shutil.rmtree('image')
    except OSError:
        print('removeDirectory Error')

if __name__ == '__main__':
    createDirectory()
    scrapeData()
    autoPosting()
    removeDirectory()
