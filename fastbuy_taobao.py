##################################################################################################################
# 淘宝抢购脚本                                                                                                   #
# 使用方法：                                                                                                     #
#     1、先将需要抢购的商品放到购物车中（注意购物车中只能放需要抢购的东西，到时抢购的时候会全部提交）；          #
#     2、修改下本脚本中的BUY_TIME值，设定为需要抢购的时间；                                                      #
#     3、执行此脚本，然后等待浏览器打开弹出登陆界面，手机淘宝扫描登陆；                                          #
#     4、脚本开始执行后，会定时刷新防止超时退出，到了设定时间点会自动尝试提交订单；                              #
#     5、抢购时为了防止一次网络拥堵出问题，设置了尝试机制，会不停尝试提交订单，直到提交成功或达到最大重试次数为止#
#     6、脚本只负责提交订单，之后24小时内需要自行完成付款操作。                                                  #
##################################################################################################################
import os
import sys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import datetime
import time
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

# ==== 设定抢购时间 （修改此处，指定抢购时间点）====
BUY_TIME = "2025-06-05 20:00:00.000"



# ====  标识登录状态、重试次数 ====
MAX_LOGIN_RETRY_TIMES = 6

current_retry_login_times = 0
login_success = False
buy_time_object = datetime.datetime.strptime(BUY_TIME, '%Y-%m-%d %H:%M:%S.%f')

now_time = datetime.datetime.now()
if now_time > buy_time_object:
    print("当前已过抢购时间，请确认抢购时间是否填错...")
    exit(0)

print("正在打开chrome浏览器...")
#让浏览器不要显示当前受自动化测试工具控制的提醒
option = webdriver.ChromeOptions()
option.add_argument('disable-infobars')
driver = webdriver.Chrome(options=option)
driver.maximize_window()
print("chrome浏览器已经打开...")


def __login_operates():
    driver.get("https://www.taobao.com")
    try:
        if driver.find_element(By.LINK_TEXT,"亲，请登录"):
            print("没登录，开始点击登录按钮...")
            driver.find_element(By.LINK_TEXT,"亲，请登录").click()
            print("请使用手机淘宝扫描屏幕上的二维码进行登录...")
            time.sleep(10)
    except:
        print("已登录，开始执行跳转...")
        global login_success
        global current_retry_login_times
        login_success = True
        current_retry_login_times = 0

def login():
    print("开始尝试登录...")
    __login_operates()
    global current_retry_login_times
    while current_retry_login_times < MAX_LOGIN_RETRY_TIMES:
        current_retry_login_times = current_retry_login_times + 1
        print("当前尝试登录次数：" + str(current_retry_login_times))
        __login_operates()
        if login_success:
            print("登录成功")
            break
        else:
            print("等待登录中...")

    if not login_success:
        print("规定时间内没有扫码登录淘宝成功，执行失败，退出脚本!!!")
        exit(0)

    # time.sleep(3)
    now = datetime.datetime.now()
    print('login success:', now.strftime('%Y-%m-%d %H:%M:%S'))

def __refresh_keep_alive():
    #重新加载购物车页面，定时操作，防止长时间不操作退出登录
    driver.get("https://cart.taobao.com/cart.htm")
    print("刷新购物车界面，防止登录超时...")
    time.sleep(60)


def keep_login_and_wait():
    print("当前距离抢购时间点还有较长时间，开始定时刷新防止登录超时...")
    while True:
        currentTime = datetime.datetime.now()
        if (buy_time_object - currentTime).seconds > 120:
            __refresh_keep_alive()
        else:
            print("抢购时间点将近，停止自动刷新，准备进入抢购阶段...")
            break
    

# ==== 精确等待直到抢购时间 ====
def wait_until_buy_time():
    print("开始精确等待抢购时间...")
    while True:
        now = datetime.datetime.now()
        print(" 现在时间： " + now.strftime("%Y-%m-%d %H:%M:%S.%f"))
        if now >= buy_time_object:
            print("==== 到达抢购时间 ====")
            break
        time.sleep(0.001)  # 提高时间精度


def buy():
    #打开购物车
    driver.get("https://cart.taobao.com/cart.htm")
    time.sleep(1)
 
    #点击购物车里全选按钮

    # 等待页面加载并找到所有 ant-checkbox-input
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input.ant-checkbox-input"))
    )

    # 获取全部 checkbox 元素
    checkboxes = driver.find_elements(By.CSS_SELECTOR, "input.ant-checkbox-input")

    # 点击第一个，也就是“全选”按钮
    if checkboxes:
        checkboxes[1].click()
        print("点击了“全选”按钮。")
    else:
        print("没有找到全选按钮")

    submit_succ = False
    retry_submit_times = 0
    # 提前找到结算按钮，待时间到点击
    wait = WebDriverWait(driver, 10)
    checkout_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn--QDjHtErD")))
    print("已经找到结算按钮")
    while True:
        # now = datetime.datetime.now()
        # if now >= buy_time_object:
        #     print("到达抢购时间，开始执行抢购...尝试次数：" + str(retry_submit_times))
        #     if submit_succ:
        #         print("订单已经提交成功，无需继续抢购...")
        #         break
        #     if retry_submit_times > 50:
        #         print("重试抢购次数达到上限，放弃重试...")
        #         break

            retry_submit_times = retry_submit_times + 1

            try:
                # 等待“结算”按钮出现并点击
                # wait = WebDriverWait(driver, 10)
                # checkout_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn--QDjHtErD")))
                wait_until_buy_time()
                checkout_btn.click()
                print("点击结算成功，正在提交订单...")

                click_submit_times = 0
                while True:
                    try:
                        if click_submit_times < 10000:
                            submit_btn = WebDriverWait(driver, 0.5, 0.01).until(
                                EC.element_to_be_clickable((By.CLASS_NAME, "btn--QDjHtErD  "))
                            )
                            submit_btn.click()
                            print("已经点击提交订单按钮")
                            submit_succ = True
                            break
                        else:
                            print("提交订单失败...")
                            exit(0)
                    except Exception:
                        print("没发现提交订单按钮，可能页面还没加载出来，重试...")
                        click_submit_times += 1
                        time.sleep(0.001)
            except Exception as e:
                if submit_succ:
                    print("订单已经提交成功，无需继续抢购...")
                    time.sleep(300)
                    exit(0)
                print(e)
                print("不好，挂了，提交订单失败了...")

            time.sleep(0.001)

# 创建 logs 文件夹
os.makedirs("logs", exist_ok=True)

# 生成当前时间的日志文件名
log_filename = datetime.datetime.now().strftime("logs/log_%Y-%m-%d_%H-%M-%S.log")
log_file = open(log_filename, "w", encoding="utf-8")

# 自定义 Logger 类，把 print 输出重定向到文件和终端
class Logger:
    def __init__(self, stream1, stream2):
        self.stream1 = stream1  # 终端
        self.stream2 = stream2  # 文件

    def write(self, message):
        self.stream1.write(message)
        self.stream2.write(message)
        self.flush()

    def flush(self):
        self.stream1.flush()
        self.stream2.flush()

sys.stdout = Logger(sys.stdout, log_file)
sys.stderr = Logger(sys.stderr, log_file)

login()
keep_login_and_wait()
buy()
 