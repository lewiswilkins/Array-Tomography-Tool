#python and node base image
FROM nikolaik/python-nodejs:python3.7-nodejs14

WORKDIR /ArrayTomographyTool

#backend setup
COPY backend/requirements.txt . 
RUN pip install --trusted-host pypi.python.org -r requirements.txt
ENV PYTHONPATH="$PYTHONPATH:/ArrayTomographyTool/backend"

#frontend setup
WORKDIR /ArrayTomographyTool/frontend/
COPY frontend/package.json .
COPY frontend/yarn.lock . 
RUN yarn install

#exposing ports
EXPOSE 3000:3000
EXPOSE 5000:5000
EXPOSE 5006:5006

WORKDIR /ArrayTomographyTool/
COPY . /ArrayTomographyTool

# run 
CMD ./start_servers.sh
