FROM python:3.7-slim

ADD requirements.txt requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

WORKDIR /ArrayTomographyTool
ADD . /ArrayTomographyTool

CMD [ "python", "process_stacks.py" ]
