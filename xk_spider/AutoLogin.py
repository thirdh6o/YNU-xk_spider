from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import ast 

class AutoLogin:
    def __init__(self, url, path, stdCode, pswd):
        # 配置 Edge 选项
        edge_options = EdgeOptions()  # 使用正确的类名
        edge_options.add_argument('--ignore-certificate-errors')
        edge_options.add_argument('--ignore-ssl-errors')
        edge_options.add_argument('--log-level=3')
        edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # 初始化浏览器
        service = Service()
        self.driver = webdriver.Edge(service=service, options=edge_options)
        self.url = url
        self.stdCode = stdCode
        self.pswd = pswd

    def get_params(self):
        self.driver.get(self.url)
        time.sleep(2)
        
        name_ele = self.driver.find_element(By.XPATH, '//input[@id="loginName"]')
        name_ele.send_keys(self.stdCode)
        
        pswd_ele = self.driver.find_element(By.XPATH, '//input[@id="loginPwd"]')
        pswd_ele.send_keys(self.pswd)
        
        if WebDriverWait(self.driver, 180).until(EC.presence_of_element_located((By.ID, 'aPublicCourse'))):
            time.sleep(1)  # waiting for loading
            cookie_lis = self.driver.get_cookies()
            cookies = ''
            for item in cookie_lis:
                cookies += item['name'] + '=' + item['value'] + '; '
            token = self.driver.execute_script('return sessionStorage.getItem("token");')
            batch_str = self.driver. \
                execute_script('return sessionStorage.getItem("currentBatch");').replace('null', 'None').replace('false', 'False').replace('true', 'True')
            batch = ast.literal_eval(batch_str)
            self.driver.quit()

            return cookies, token, batch['code']

        else:
            print('page load failed')
            self.driver.quit()
            return False

    # 暂时无用
    def keep_connect(self):
        flag = 1
        st = time.perf_counter()
        while True:
            try:
                if flag == 1:
                    ele = self.driver.find_element_by_xpath('//a[@id="aPublicCourse"]')
                    ele.click()
                    flag = 2
                    time.sleep(30)
                elif flag == 2:
                    ele = self.driver.find_element_by_xpath('//a[@id="aProgramCourse"]')
                    ele.click()
                    flag = 1
                    time.sleep(30)

            except NoSuchElementException:
                print('连接已断开')
                print(f'运行时间：{(time.perf_counter() - st)//60} min')
                # self.driver.quit()
                break


if __name__ == '__main__':
    Url = 'http://xk.ynu.edu.cn/xsxkapp/sys/xsxkapp/*default/index.do'
    Name = ''
    Pswd = ''
    Headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/80.0.3987.116 Safari/537.36'
    }
