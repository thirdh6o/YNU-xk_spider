from concurrent.futures import ThreadPoolExecutor, as_completed

from AutoLogin import AutoLogin
from GetCourse import GetCourse

# 程序运行后会打开浏览器进入选课登录页面，请登录进去直到能看到具体的课程，然后就可以把浏览器关了
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/80.0.3987.116 Safari/537.36'
}
url = 'http://xk.ynu.edu.cn/xsxkapp/sys/xsxkapp/*default/index.do'
stdCode = '。'  # 在''中填入你的学号
pswd = '。'  # 填你的密码
# 邮箱配置
email_config = {
    'sender': '',      # 发件人邮箱
    'password': '',    # 发件人邮箱密码或授权码
    'receiver': '',    # 收件人邮箱
    'smtp_server': 'smtp.qq.com',  # SMTP服务器，这里以QQ邮箱为例
    'smtp_port': 465   # SMTP端口，QQ邮箱使用465
}
# 删除 path 变量的定义


# 下面这个列表填你想查询的 素选课 ，以 ['课程名称', '授课老师'], 的格式填，注意最后有一个 英文 逗号

# -----  注意，课程名称要保证在选课页面你能用这个名称搜得出来 !!!  -----

publicCourses = [
    ['初级泰语', '侬常生'],  # 这是个测试用例，可以先不修改直接运行看看是否成功，如果不小心抢到了自己手动退掉就好
]

# 下面这个列表填你想查询的 主修课，包括必修和选修，格式填写同上
programCourse = [
]

'''以上两个列表理论上可以接受任意数量的课程，填写模板如下。但数量最好不要超过你CPU的核心数（一般电脑都在4核以上）
programCourse = [
    ['课程1', '老师1'], 
    ['课程2', '老师2'], 
    ['课程3', '老师3'], 
]
'''
al = AutoLogin(url, None, stdCode, pswd)  # 将 path 参数改为 None
headers['cookie'], headers['token'], batchCode = al.get_params()

'''至此程序已经可以运行了。在程序运行期间请不要登录选课系统，否则程序会终止运行'''
'''已破除自动注销机制，实现了7*24小时运行，如果程序突然中止了，那是选课系统在更新，这个没办法解决，只能等更新结束后重新运行'''
'''因为用了线程池，按理说会有线程同步上的问题，但在这个爬虫上几乎不会产生，如果您遇到了可以联系我，我再对代码做修改'''

'''如果本项目有帮到你，还请点击GitHub主页右上角的star支持下 :)'''
gc = GetCourse(headers, stdCode, batchCode)

ec = ThreadPoolExecutor()
taskList = []
for course in publicCourses:
    taskList.append(ec.submit(gc.judge, course[0], course[1], email_config, kind='素选'))
for course in programCourse:
    taskList.append(ec.submit(gc.judge, course[0], course[1], email_config, kind='主修'))

for future in as_completed(taskList):
    print(future.result())
