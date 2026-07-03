# ksml_lib_14.py
# 相較 ksml_lib_13.py 的主要變更：
#   - 新增驗證碼自動辨識功能（Tesseract OCR + pytesseract）
#   - 新增登入重試機制（最多 3 次）
#   - 其餘借閱/預約資料擷取邏輯完全不變
#
# 系統依賴（在樹莓派 Bullseye 上執行一次）：
#   sudo apt-get install tesseract-ocr
#   pip install pytesseract Pillow
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from datetime import datetime
import time
import requests
import sys
from dotenv import dotenv_values
import os
import socket
import base64
import io
import pytesseract
from PIL import Image


# --------------------------------------------------------------------------- #
# Telegram 通知（保留，未來擴充用）
# --------------------------------------------------------------------------- #
async def telegram_send_text(text):
    bot = Bot(token=TELEGRAM_TOKEN)
    try:
        await bot.send_message(
            chat_id=TELEGRAM_ID,
            text=text
        )
        return True
    except Exception as e:
        print(f'Error sending text: {e}')
        return False


# --------------------------------------------------------------------------- #
# 驗證碼辨識
# --------------------------------------------------------------------------- #
def solve_captcha(browser):
    """
    從頁面上的 <img class="captcha"> 讀取 base64 inline 圖片資料，
    透過 Tesseract OCR（pytesseract）辨識後回傳驗證碼文字。

    驗證碼圖片的 src 格式為：
        data:image/png;base64,<base64_data>
    不需要 HTTP 請求，直接解碼即可。

    影像預處理流程（提升辨識準確率）：
        1. 轉灰階     — 移除彩色干擾
        2. 二值化     — 白底黑字，threshold=200（彩色文字灰階值通常低於背景）
        3. 放大 3 倍  — Tesseract 對較大圖片準確率更高

    Tesseract 參數：
        --psm 7 : 單行文字模式（適合橫排數字驗證碼）
        --oem 3 : 預設引擎（LSTM + Legacy 混合）
        tessedit_char_whitelist=0123456789 : 僅辨識數字
    """
    # XPath 定位驗證碼圖片（比 CSS Selector 更精確）
    captcha_img = browser.find_element(By.XPATH, '//img[contains(@class,"captcha")]')
    img_src = captcha_img.get_attribute('src')
    # 分割 "data:image/png;base64," 前綴，取得純 base64 字串
    b64_data = img_src.split(',', 1)[1]
    img_bytes = base64.b64decode(b64_data)

    # --- 影像預處理 ---
    img = Image.open(io.BytesIO(img_bytes))
    img = img.convert('L')  # 轉灰階
    # 二值化：深色像素（彩色文字）→ 黑(0)；淺色（白色背景）→ 白(255)
    img = img.point(lambda px: 0 if px < 200 else 255)
    # 放大 3 倍，讓 Tesseract 取得更多像素細節
    img = img.resize((img.width * 3, img.height * 3), Image.LANCZOS)

    # --- Tesseract 辨識 ---
    tess_config = '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789'
    raw = pytesseract.image_to_string(img, config=tess_config)
    # 過濾殘留的非數字字元（換行、空白等）
    result = re.sub(r'[^0-9]', '', raw)
    return result


# --------------------------------------------------------------------------- #
# 含驗證碼重試的登入函式
# --------------------------------------------------------------------------- #
def login_with_captcha(browser, account, password, max_retry=3):
    """
    含驗證碼的登入函式，最多重試 max_retry 次。

    重試策略：
      - 第 1 次：頁面已在 get_books() 中載入，直接登入。
      - 第 2~3 次：先清除所有 Cookie（避免失敗後 session 狀態影響 modal 顯示）
                  再重載頁面，並等待登入表單出現。
      - 所有元素定位均改用 XPath（不依賴 class 名稱變化）。
      - 登入成功判斷超時從 5 秒延長至 20 秒（適應 Pi 3B 較慢的頁面載入速度）。

    Args:
        browser   : Selenium WebDriver 實例
        account   : 借閱證號或身分證字號
        password  : 自訂密碼
        max_retry : 最大重試次數（預設 3）

    Returns:
        bool : 登入成功回傳 True，否則回傳 False
    """
    for attempt in range(1, max_retry + 1):
        try:
            # --- 重試時清除 Cookie 並重載頁面，確保登入 modal 不受前一次失敗的影響 ---
            if attempt > 1:
                browser.delete_all_cookies()
                browser.get('https://webpacx.ksml.edu.tw/personal/')

            # --- 等待登入表單出現（XPath，最多 30 秒，適應 Pi 3B 較慢的 AJAX 載入）---
            loginid = WebDriverWait(browser, 30).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@id="logxinid"]'))
            )
            loginid.clear()
            loginid.send_keys(account)

            # --- 填入密碼 ---
            pincode = browser.find_element(By.XPATH, '//input[@id="pincode"]')
            pincode.clear()
            pincode.send_keys(password)

            # --- 辨識並填入驗證碼 ---
            captcha_text = solve_captcha(browser)
            print(f'[嘗試 {attempt}/{max_retry}] 驗證碼辨識結果: {captcha_text}')
            vcode_input = browser.find_element(By.XPATH, '//input[@id="captcha"]')
            vcode_input.clear()
            vcode_input.send_keys(captcha_text)

            # --- 點擊登入按鈕 ---
            login_btn = browser.find_element(
                By.XPATH, '//div[contains(@class,"btn_grp")]//input'
            )
            login_btn.click()

            # --- 判斷登入是否成功 ---
            # 暫時關閉 implicit wait，避免與 WebDriverWait 衝突
            # 超時設為 20 秒：Pi 3B 頁面載入較慢，5 秒可能不夠
            browser.implicitly_wait(0)
            try:
                WebDriverWait(browser, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'redblock'))
                )
                print(f'登入成功（第 {attempt} 次嘗試）')
                return True
            except Exception:
                print(f'[嘗試 {attempt}/{max_retry}] 登入失敗，準備重試...')
                # 嘗試在目前頁面上就地刷新驗證碼（若失敗則下一輪重載）
                if attempt < max_retry:
                    try:
                        time.sleep(1)  # 等頁面狀態穩定
                        refresh_btn = browser.find_element(
                            By.XPATH, '//button[contains(.,"更換驗證碼")]'
                        )
                        refresh_btn.click()
                        time.sleep(2)  # 等待新驗證碼圖片載入
                    except Exception:
                        pass  # 找不到刷新按鈕沒關係，下一輪將重載頁面
            finally:
                # 無論成敗，恢復 implicit wait
                browser.implicitly_wait(60)

        except Exception as e:
            print(f'[嘗試 {attempt}/{max_retry}] 發生例外: {e}')
            browser.implicitly_wait(60)  # 確保外層也恢復

    print('登入失敗：已達最大重試次數（3 次）')
    return False


# --------------------------------------------------------------------------- #
# 主要爬蟲函式（借閱 / 預約資料擷取邏輯與 v13 完全一致）
# --------------------------------------------------------------------------- #
def get_books(account, password):
    browser = None
    result = (None, None)  # 預設回傳值
    try:
        # --- 瀏覽器初始化 ---
        # 設定一個在 SD 卡上的暫存目錄 (for Trixie)
        chrome_tmp_path = os.path.expanduser('~/chrome_tmp')
        if not os.path.exists(chrome_tmp_path):
            os.makedirs(chrome_tmp_path)
        options = Options()
        options.add_argument("--headless=new")        # 新版無頭擬真瀏覽器
        options.add_argument("--no-sandbox")          # Trixie 必加
        options.add_argument("--disable-dev-shm-usage")  # 避免擠爆 /dev/shm
        options.add_argument('--disable-gpu')         # 避免 GPU 驅動崩潰
        # 強迫使用 SD 卡空間 (特別是 Trixie 必須)
        options.add_argument(f'--user-data-dir={chrome_tmp_path}')
        # 限制快取大小為 100MB (防止 chrome_tmp 資料夾隨著時間變得巨大)
        options.add_argument('--disk-cache-size=104857600')
        options.binary_location = '/usr/bin/chromium'
        service = Service('/usr/bin/chromedriver')
        browser = webdriver.Chrome(service=service, options=options)
        browser.implicitly_wait(60)
        browser.set_window_size(1920, 1080)

        # --- 載入登入頁並執行含驗證碼的登入 ---
        browser.get('https://webpacx.ksml.edu.tw/personal/')
        if not login_with_captcha(browser, account, password):
            return result  # 登入失敗，提早結束，回傳 (None, None)

        # --- 擷取借閱紀錄 ---
        div_redblock = browser.find_element(By.CLASS_NAME, 'redblock')
        div_redblock.click()
        books = browser.find_elements(By.CLASS_NAME, 'bookdata')
        borrow_books = []
        for book in books:
            item = dict()
            book_name = book.find_element(By.XPATH, './h2/a').text
            item['book_name'] = book_name.replace('/', '').strip()
            book_site = book.find_element(By.XPATH, './ul[3]/li[1]').text
            reg = r'典藏地：(\S+)'
            item['book_site'] = re.findall(reg, book_site)[0]
            reg = r'\d{4}-\d{2}-\d{2}'
            due_date = book.find_element(By.XPATH, './ul[4]/li[2]').text
            item['due_date'] = re.findall(reg, due_date)[0]
            due_times = book.find_element(By.XPATH, './ul[5]/li[1]').text
            item['due_times'] = re.findall(r'\d{1}', due_times)[0]
            try:
                state = book.find_element(By.XPATH, './ul[6]/li[1]').text
            except:
                state = ''
            finally:
                if '有人預約' in state:
                    item['state'] = ', 有人預約'
                else:
                    item['state'] = ''
            borrow_books.append(item)
        print('擷取借閱紀錄 ... OK')
        browser.back()  # 回上一頁

        # --- 擷取預約紀錄 ---
        div_blueblock = browser.find_element(By.CLASS_NAME, 'blueblock')
        div_blueblock.click()
        books = browser.find_elements(By.CLASS_NAME, 'bookdata')
        reserve_books = []
        for book in books:
            item = dict()
            book_name = book.find_element(By.XPATH, './h2/a').text
            item['book_name'] = book_name.replace('/', '').strip()
            sequence = book.find_element(By.XPATH, './ul[7]/li[1]').text
            if '預約待取' in sequence:  # 已到館
                item['ready_for_pickup'] = True
                reg = r'\d{4}-\d{2}-\d{2}'
                item['expiration'] = re.findall(reg, sequence)[0]
                item['sequence'] = '0'
            else:  # 預約中
                item['ready_for_pickup'] = False
                item['expiration'] = ''
                item['sequence'] = re.findall(r'\d+', sequence)[0]
            reserve_books.append(item)
        print('擷取預約紀錄 ... OK')
        result = (borrow_books, reserve_books)

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


# --------------------------------------------------------------------------- #
# 程式進入點（命令列參數設計與 v13 完全相容，Cron Job 無需修改）
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    start = time.time()
    config = dotenv_values('.env')
    TELEGRAM_TOKEN = config.get('TELEGRAM_TOKEN')
    TELEGRAM_ID = config.get('TELEGRAM_ID')
    host_name = socket.gethostname()
    print(f'主機 : {host_name}')

    # 命令列參數驗證：必須傳入帳號與密碼
    if len(sys.argv) != 3:
        print(f'用法: {sys.argv[0]} 帳號 密碼')
        sys.exit(1)

    # 取得傳入的帳密參數
    account = sys.argv[1]
    password = sys.argv[2]

    # 呼叫 get_books() 取得借書與預約書
    borrow_books, reserve_books = get_books(account, password)
    b_msg = ''  # 借書資訊字串初始值
    r_msg = ''  # 預約資訊字串初始值

    # --- 處理借書 ---
    if borrow_books:
        borrow = []
        for book in borrow_books:
            book_name = book['book_name']
            book_site = book['book_site']
            due_times = book['due_times']
            due_date = book['due_date']
            state = book['state']
            due_date = datetime.strptime(due_date, '%Y-%m-%d')  # 到期日
            today_str = datetime.today().strftime('%Y-%m-%d')
            today = datetime.strptime(today_str, "%Y-%m-%d")
            delta = (due_date - today).days  # 計算離到期日還有幾天
            if delta < 0:  # 負數=已逾期
                msg = f'🅧 {book_name} (逾期 {abs(delta)} 天{state}, {book_site})'
                borrow.append(msg)
            elif delta == 0:  # 0=今天到期
                msg = f'⓿ {book_name} (今日到期, 續借次數 {due_times}{state}, {book_site})'
                borrow.append(msg)
            elif delta == 1:  # 1=明天到期
                msg = f'❶ {book_name} (明日到期, 續借次數 {due_times}{state}, {book_site})'
                borrow.append(msg)
            elif delta == 2:  # 2=後天到期
                msg = f'❷ {book_name} (後天到期, 續借次數 {due_times}{state}, {book_site})'
                borrow.append(msg)
            elif 2 < delta < 8:  # 3 天以上一周內到期
                msg = f'✦ {book_name} ({book["due_date"]} 到期, '\
                      f'續借次數 {due_times}{state}, {book_site})'
                borrow.append(msg)
        # 製作借書到期摘要字串
        if len(borrow) != 0:
            borrow.insert(0, f'\n❖ {account} 的借閱 :')
            b_msg = '\n'.join(borrow)  # 更新借書資訊字串
        print('產生借書到期摘要 ... OK')

    # --- 處理預約書 ---
    if reserve_books:
        reserve = []
        i = 0
        j = ['①', '②', '③', '④', '⑤']
        k = ['❶', '❷', '❸', '❹', '❺']
        # 預約狀態
        for book in reserve_books:
            book_name = book['book_name']
            sequence = book['sequence']
            ready_for_pickup = book['ready_for_pickup']  # 已到館
            expiration = book['expiration']              # 取書截止日
            if ready_for_pickup:
                msg = f'{k[i]} {book_name} (已到館, 保留期限 {expiration})'
            else:
                msg = f'{j[i]} {book_name} (順位 {sequence})'
            reserve.append(msg)
            i += 1
        # 製作預約書摘要字串
        if len(reserve) != 0:
            reserve.insert(0, f'\n❖ {account} 的預約 :')
            r_msg = '\n'.join(reserve)  # 更新資訊字串
    print('產生預約書摘要 ... OK')

    # --- 推送資料 ---
    if b_msg or r_msg:  # 任一不為空字串就更新資料表
        url = "https://serverless-5e6i.onrender.com/function/update_ksml_books"
        payload = {
            "account": account,
            "borrow_books": b_msg,
            "reserve_books": r_msg
        }
        res = requests.post(url, json=payload)
        print(res.json())

    end = time.time()
    print(f'執行時間:{end - start}')
