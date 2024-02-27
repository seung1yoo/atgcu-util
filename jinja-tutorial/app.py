

# try 1.
#from jinja2 import Environment, PackageLoader, select_autoescape
#
#env = Environment(
#        loader=PackageLoader("yourapp"),
#        autoescape=select_autoescape()
#
#)


# try 2.
#from jinja2 import Environment, FileSystemLoader
#
#env = Environment(loader=FileSystemLoader('yourapp/templates'))
#context = {'username': 'John Doe'}
#template = env.get_template('index.html')
#output = template.render(context)



# try 3.
from jinja2 import Environment, FileSystemLoader

# 템플릿 엔진 설정
env = Environment(loader=FileSystemLoader('yourapp/templates'))

# 각 템플릿에서 사용할 변수
context_home = {'username': 'John Doe'}
context_about = {}  # about.html에는 추가 변수가 없음

# index.html 템플릿 렌더링
template_home = env.get_template('index.jinja')
output_home = template_home.render(context_home)

# about.html 템플릿 렌더링
template_about = env.get_template('about.jinja')
output_about = template_about.render(context_about)

# 렌더링 결과 출력
outfh = open("index.html", "w")
outfh.write(output_home)
outfh.close()

outfh = open("about.html", "w")
outfh.write(output_about)
outfh.close()




