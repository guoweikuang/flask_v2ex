FROM daocloud.io/python:3.5

RUN mkdir -p /home/guoweikuang/app 
WORKDIR /home/guoweikuang/app 

ADD ./requirements.txt /home/guoweikuang/app/requirements.txt 

RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip 
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt 

ADD . /home/guoweikuang/app 

CMD python manage.py runserver -h 0.0.0.0

