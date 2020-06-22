#python and node base image
FROM nikolaik/python-nodejs:python3.7-nodejs14

WORKDIR /ArrayTomographyTool

COPY backend/requirements.txt . 
#backend setup

RUN pip install --trusted-host pypi.python.org -r requirements.txt
ENV PYTHONPATH="$PYTHONPATH:/ArrayTomographyTool/backend"

#frontend setup
WORKDIR /ArrayTomographyTool/frontend/
COPY frontend/package.json .
COPY frontend/yarn.lock . 
RUN yarn install

#exposing ports
EXPOSE 3000
EXPOSE 5000

WORKDIR /ArrayTomographyTool/
COPY . /ArrayTomographyTool

# run 
CMD ./start_servers.sh
