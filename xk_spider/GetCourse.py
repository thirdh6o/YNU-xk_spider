import requests
import ast
import time
import re
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from requests.exceptions import HTTPError


def send_notification(email_config, title, content):
    sender = email_config['sender']
    password = email_config['password']
    receiver = email_config['receiver']
    smtp_server = email_config['smtp_server']
    smtp_port = email_config['smtp_port']

    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header(sender)
    message['To'] = Header(receiver)
    message['Subject'] = Header(title)

    try:
        smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        smtp.login(sender, password)
        smtp.sendmail(sender, receiver, message.as_string())
        smtp.quit()
        return title + '：已发送至邮箱'
    except Exception as e:
        print(f'邮件发送失败：{str(e)}')
        return f'邮件发送失败：{str(e)}'


class GetCourse:
    def __init__(self, headers: dict, stdcode, batchcode):
        self.headers = headers
        self.stdcode = stdcode
        self.batchcode = batchcode

    def judge(self, courseName, teacher, email_config, kind='素选'):
        # 人数未满才返回classid
        classtype = "XGXK"
        if kind == '素选':
            kind = 'publicCourse.do'
        elif kind == '主修':
            kind = 'programCourse.do'
            classtype = "FANKC"
        url = 'http://xk.ynu.edu.cn/xsxkapp/sys/xsxkapp/elective/' + kind

        while True:
            try:
                query = self.__judge_datastruct(courseName, kind)  # 修改变量名：course_name -> courseName, classtype -> kind
                r = requests.post(url, data=query, headers=self.headers)
                r.raise_for_status()
                flag = 0
                while not r:
                    if flag > 2:
                        if email_config:
                            send_notification(email_config, f'{course_name} 查询失败，请检查失败原因', '线程结束')
                        return False
                    print(f'[warning]: jugde()函数正尝试再次爬取')
                    time.sleep(3)
                    r = requests.post(url, data=query, headers=self.headers)

                try:
                    setcookie = r.headers['set-cookie']
                except KeyError:
                    setcookie = ''
                if setcookie:
                    print(f'[set-cookie]: {setcookie}')
                    update = re.search(r'_WEU=.+?; ', setcookie).group(0)
                    self.headers['cookie'] = re.sub(r'_WEU=.+?; ', update, self.headers['cookie'])

                    print(f'[current cookie]: {self.headers["cookie"]}')

                temp = r.text.replace('null', 'None').replace('false', 'False').replace('true', 'True')
                res = ast.literal_eval(temp)
                if kind == 'publicCourse.do':
                    try:
                        if not res['dataList']:
                            print(f"未找到课程：{courseName}，等待重试...")
                            time.sleep(2)  # 添加延迟避免请求过快
                            
                        datalist = res['dataList'][0]['tcList']
                        if not datalist:
                            print(f"课程 {courseName} 暂无教师信息，等待重试...")
                            time.sleep(2)

                            
                    except (KeyError, IndexError) as e:
                        print(f"获取课程信息失败：{e}，等待重试...")
                        time.sleep(2)
                elif kind == 'programCourse.do':
                    datalist = res['dataList'][0]['tcList']
                else:
                    print('kind参数错误，请重新输入')
                    return False

                if res['msg'] == '未查询到登录信息':
                    print('登录失效，请重新登录')
                    if email_config:
                        send_notification(email_config, '登录失效，请重新登录', '线程结束')
                    return False

                for course in datalist:
                    remain = int(course['classCapacity']) - int(course['numberOfFirstVolunteer'])
                    if remain > 0 and course['teacherName'] == teacher:
                        string = f'{course_name} {teacher}：{remain}人空缺'
                        print(string)
                        if email_config:
                            send_notification(email_config, f'{course_name} 余课提醒', string)
                        res = self.post_add(course_name, teacher, classtype, course['teachingClassID'], email_config)
                        return res

                print(f'{course_name} {teacher}：人数已满 {time.ctime()}')
                time.sleep(15)

            except HTTPError or SyntaxError:
                print('登录失效，请重新登录')
                if email_config:
                    send_notification(email_config, '登录失效，请重新登录', '线程结束')
                return False

    def post_add(self, classname, teacher, classtype, classid, email_config):
        query = self.__add_datastruct(classid, classtype)

        url = 'http://xk.ynu.edu.cn/xsxkapp/sys/xsxkapp/elective/volunteer.do'
        r = requests.post(url, headers=self.headers, data=query)
        flag = 0
        while not r:
            if flag > 2:
                if email_config:
                    send_notification(email_config, f'{classname} 有余课，但post未成功', '线程结束')
                break
            print(f'[warning]: post_add()函数正尝试再次请求')
            time.sleep(3)
            r = requests.post(url, headers=self.headers, data=query)
            flag += 1

        messge_str = r.text.replace('null', 'None').replace('false', 'False').replace('true', 'True')
        messge = ast.literal_eval(messge_str)['msg']
        title = '抢课结果'
        string = '[' + teacher + ']' + classname + ': ' + messge
        if email_config:
            send_notification(email_config, title, string)
        return string

    def __add_datastruct(self, classid, classtype) -> dict:
        post_course = {
            "data": {
                "operationType": "1",
                "studentCode": self.stdcode,
                "electiveBatchCode": self.batchcode,
                "teachingClassId": classid,
                "isMajor": "1",
                "campus": "05",
                "teachingClassType": classtype
            }
        }
        query = {
            'addParam': str(post_course)
        }

        return query

    def __judge_datastruct(self, course, classtype) -> dict:
        data = {
            "data": {
                "studentCode": self.stdcode,
                "campus": "05",
                "electiveBatchCode": self.batchcode,
                "isMajor": "1",
                "teachingClassType": classtype,
                "checkConflict": "2",
                "checkCapacity": "2",
                "queryContent": course
            },
            "pageSize": "10",
            "pageNumber": "0",
            "order": ""
        }
        query = {
            'querySetting': str(data)
        }

        return query


if __name__ == '__main__':
    Headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/80.0.3987.116 Safari/537.36',
        'cookie': '',
        'token': ''
    }
    stdCode = ''
    batchCode = ''

    test = GetCourse(Headers, stdCode, batchCode)
