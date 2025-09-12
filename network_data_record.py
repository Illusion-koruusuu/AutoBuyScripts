import json
import time
from datetime import datetime
from pathlib import Path
from telnetlib import EC
from time import sleep

import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options

# 1️⃣ 生成 “启动时间” 字符串
start_ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# 2️⃣ 设置日志目录并保证存在
log_dir = Path("network_data_logs")
log_dir.mkdir(parents=True, exist_ok=True)
# 3️⃣  设置文件名
log_file = log_dir / f"network_data_{start_ts}.log"
# 4️⃣ 配置 logging：同时输出到文件和控制台
logging.basicConfig(
    level=logging.WARNING,                    # 只想看 INFO 以上就写 INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),    #输出到文件
        logging.StreamHandler()                             #在控制台打印
    ]
)

logging.info("正在打开chrome浏览器...")
# 设置 Chrome 启动选项
chrome_options = Options()
# chrome_options.set_capability(
#     "goog:loggingPrefs",
#     {"performance": "ALL"}
# )
chrome_options.add_argument('--disable-infobars')

# 启动 Chrome
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
logging.info("chrome浏览器已经打开...")

#打开淘宝网页
driver.get("https://www.taobao.com")
time.sleep(6)

first_enter = True
click_submit_times = 0

while True:

    try:
        if click_submit_times < 10000:
            # 设置最大等待时间为0.1秒
            submit_btn = WebDriverWait(driver, 0.1).until(
                EC.presence_of_element_located((By.CLASS_NAME, "btn--QDjHtErD"))
            )
            submit_btn.click()
            print("已经点击提交订单按钮")
            break
        else:
            print("提交订单失败...")
            exit(0)
    except Exception:
        print("没发现提交订单按钮，可能页面还没加载出来，重试...")
        click_submit_times += 1
        driver.refresh()
        time.sleep(0.001)

    if "confirm_order" in driver.current_url:

        if first_enter:
            logging.info("正在提交订单页面...")
            first_enter = False

        # # ---------- 整理并输出 ----------
        # out_path = log_dir / f'detail_{start_ts}.jsonl'
        # with out_path.open('a', encoding='utf-8') as fp:
        #     records = []
        #     for req in driver.requests:
        #         if not req.response:
        #             logging.info("还没响应或被浏览器取消")
        #             continue
        #         try:
        #             rec = {
        #                 'url': req.url,
        #                 'method': req.method,
        #                 'request_headers': dict(req.headers),
        #                 'request_payload': (req.body or b'').decode('utf-8', 'ignore'),
        #                 'status': req.response.status_code,
        #                 'response_headers': dict(req.response.headers),
        #                 # 'response_body': (req.response.body or b'').decode('utf-8', 'ignore'),
        #                 'timing_ms': round(
        #                     (req.response.date - req.date).total_seconds() * 1000, 2
        #                 ) if req.date and req.response.date else None
        #             }
        #             if req.method != "GET":
        #                 records.append(rec)
        #                 fp.write(json.dump(records, fp, ensure_ascii=False, indent=4, sort_keys=True) + '\n' + '\r\n')
        #                 fp.write('\r\n')
        #
        #         except Exception as e:
        #             logging.warning(f'处理请求失败: {e}')
        #
        # logging.info(f'已写入 {out_path}')



    sleep(0.1)
