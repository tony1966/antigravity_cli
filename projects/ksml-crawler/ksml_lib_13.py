# ksml_lib_13.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import re
from datetime import datetime
import time
import requests
import sys
from dotenv import dotenv_values
import os
import socket

async def telegram_send_text(text):
    bot=Bot(token=TELEGRAM_TOKEN)
    try:
        await bot.send_message(
            chat_id=TELEGRAM_ID,
            text=text
        )
        return True
    except Exception as e:
        print(f'Error sending text: {e}')
        return False

def get_books(account, password):
    browser=None
    result=(None, None)  # 預設回傳值   
    try:
        # 登入我的書房
        # 設定一個在 SD 卡上的暫存目錄 (for Trixie)
        chrome_tmp_path=os.path.expanduser('~/chrome_tmp')
        if not os.path.exists(chrome_tmp_path):
            os.makedirs(chrome_tmp_path)        
        options=Options()
        options.add_argument("--headless=new") # 新版無頭擬真瀏覽器
        options.add_argument("--no-sandbox") # Trixie 必加
        options.add_argument("--disable-dev-shm-usage") # 避免擠爆 /dev/shm
        options.add_argument('--disable-gpu') # 避免 GPU 驅動崩潰
        # 強迫使用 SD 卡空間 (特別是 Trixie 必須)
        options.add_argument(f'--user-data-dir={chrome_tmp_path}')
        # 限制快取大小為 100MB (防止 chrome_tmp 資料夾隨著時間變得巨大)
        options.add_argument('--disk-cache-size=104857600')
        options.binary_location='/usr/bin/chromium'       
        service=Service('/usr/bin/chromedriver')
        browser=webdriver.Chrome(service=service, options=options)
        browser.implicitly_wait(60)
        browser.set_window_size(1920, 1080)        
        # 載入網頁
        browser.get('https://webpacx.ksml.edu.tw/personal/')
        loginid=browser.find_element(By.ID, 'logxinid')
        loginid.send_keys(account)
        pincode=browser.find_element(By.ID, 'pincode')
        pincode.send_keys(password)
        div_btn_grp=browser.find_element(By.CLASS_NAME, 'btn_grp')
        login_btn=div_btn_grp.find_element(By.TAG_NAME, 'input')
        login_btn.click()
        # 擷取借閱紀錄
        div_redblock=browser.find_element(By.CLASS_NAME, 'redblock')
        div_redblock.click()
        books=browser.find_elements(By.CLASS_NAME, 'bookdata')
        borrow_books=[]
        for book in books:
            item=dict()
            book_name=book.find_element(By.XPATH, './h2/a').text    
            item['book_name']=book_name.replace('/', '').strip()
            book_site=book.find_element(By.XPATH, './ul[3]/li[1]').text
            reg=r'典藏地：(\S+)'
            item['book_site']=re.findall(reg, book_site)[0]
            reg=r'\d{4}-\d{2}-\d{2}'
            due_date=book.find_element(By.XPATH, './ul[4]/li[2]').text
            item['due_date']=re.findall(reg, due_date)[0] 
            due_times=book.find_element(By.XPATH, './ul[5]/li[1]').text
            item['due_times']=re.findall(r'\d{1}', due_times)[0]
            try: 
                state=book.find_element(By.XPATH, './ul[6]/li[1]').text
            except:
                state=''
            finally:
                if '有人預約' in state:
                    item['state']=', 有人預約'
                else:
                    item['state']=''
            borrow_books.append(item)
        print('擷取借閱紀錄 ... OK')
        browser.back() # 回上一頁
        # 擷取預約紀錄
        div_blueblock=browser.find_element(By.CLASS_NAME, 'blueblock')
        div_blueblock.click()
        books=browser.find_elements(By.CLASS_NAME, 'bookdata')
        reserve_books=[]
        for book in books:
            item=dict()
            book_name=book.find_element(By.XPATH, './h2/a').text    
            item['book_name']=book_name.replace('/', '').strip()
            sequence=book.find_element(By.XPATH, './ul[7]/li[1]').text
            if '預約待取' in sequence:  # 已到館
                item['ready_for_pickup']=True
                reg=r'\d{4}-\d{2}-\d{2}'
                item['expiration']=re.findall(reg, sequence)[0]
                item['sequence']='0'
            else: # 預約中
                item['ready_for_pickup']=False
                item['expiration']=''
                item['sequence']=re.findall(r'\d+', sequence)[0]
            reserve_books.append(item)
        print('擷取預約紀錄 ... OK')
        result=(borrow_books, reserve_books)        
    except Exception as e:
        print(f'發生錯誤 : {e}')
    finally:
        if browser:
            try:
                browser.quit()  # 釋放記憶體
                print('資源已釋放')
            except:
                pass            
    return result   
    
if __name__ == '__main__':
    start=time.time()
    config=dotenv_values('.env')
    TELEGRAM_TOKEN=config.get('TELEGRAM_TOKEN')
    TELEGRAM_ID=config.get('TELEGRAM_ID')
    #print(TELEGRAM_TOKEN)
    #print(TELEGRAM_ID)
    host_name=socket.gethostname()
    print(f'主機 : {host_name}')    
    if len(sys.argv) != 3:
        print(f'用法: {sys.argv[0]} 帳號 密碼')
        sys.exit(1)
    # 取得傳入的帳密參數
    account=sys.argv[1]
    password=sys.argv[2]
    # 呼叫 get_books() 取得借書與預約書        
    borrow_books, reserve_books=get_books(account, password)
    b_msg=''  # 借書資訊字串初始值
    r_msg=''  # 預約資訊字串初始值
    # 處理借書 
    if borrow_books: 
        borrow=[]
        for book in borrow_books:
            book_name=book['book_name']
            book_site=book['book_site'] 
            due_times=book['due_times']
            due_date=book['due_date']
            state=book['state']
            due_date=datetime.strptime(due_date, '%Y-%m-%d') # 到期日   
            today_str=datetime.today().strftime('%Y-%m-%d')   
            today=datetime.strptime(today_str, "%Y-%m-%d")   
            delta=(due_date-today).days  # 計算離到期日還有幾天
            if delta < 0:  # 負數=已逾期
                msg=f'🅧 {book_name} (逾期 {abs(delta)} 天{state}, {book_site})'
                borrow.append(msg)
            elif delta == 0:  # 0=今天到期
                msg=f'⓿ {book_name} (今日到期, 續借次數 {due_times}{state}, {book_site})'
                borrow.append(msg)
            elif delta == 1:  # 1=明天到期 
                msg=f'❶ {book_name} (明日到期, 續借次數 {due_times}{state}, {book_site})'
                borrow.append(msg)
            elif delta == 2:  # 2=後天到期 
                msg=f'❷ {book_name} (後天到期, 續借次數 {due_times}{state}, {book_site})'
                borrow.append(msg)
            elif 2 < delta < 8:  # 3 天以上一周內到期
                msg=f'✦ {book_name} ({book["due_date"]} 到期, '\
                    f'續借次數 {due_times}{state}, {book_site})'
                borrow.append(msg)
        # 製作借書到期摘要字串 
        if len(borrow) != 0:
            borrow.insert(0, f'\n❖ {account} 的借閱 :')
            b_msg='\n'.join(borrow)  # 更新借書資訊字串
        print('產生借書到期摘要 ... OK')
    # 處理預約書
    if reserve_books:
        reserve=[]
        i=0
        j=['①', '②', '③', '④', '⑤']
        k=['❶', '❷', '❸', '❹', '❺']
        # 預約狀態
        for book in reserve_books:
            book_name=book['book_name']
            sequence=book['sequence']
            ready_for_pickup=book['ready_for_pickup'] # 已到館
            expiration=book['expiration']  # 取書截止日
            if ready_for_pickup:
                msg=f'{k[i]} {book_name} (已到館, 保留期限 {expiration})'
            else:
                msg=f'{j[i]} {book_name} (順位 {sequence})'
            reserve.append(msg)
            i += 1
        # 製作預約書摘要字串    
        if len(reserve) != 0:
            reserve.insert(0, f'\n❖ {account} 的預約 :')
            r_msg='\n'.join(reserve)  # 更新資訊字串
    print('產生預約書摘要 ... OK')
    if b_msg or r_msg:  # 任一不為空字串就更新資料表
        url="https://serverless-5e6i.onrender.com/function/update_ksml_books"
        payload={
            "account": account,
            "borrow_books": b_msg,   
            "reserve_books": r_msg
            }
        res=requests.post(url, json=payload)
        print(res.json())        
    end=time.time()
    print(f'執行時間:{end-start}')