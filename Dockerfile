FROM node:lts-alpine

# python
RUN apk update && apk add --no-cache python3 py3-pip zip && python3 --version

# cdk
RUN npm install -g aws-cdk

# source
WORKDIR /tmp
COPY ./requirements.txt /tmp
COPY ./requirements-dev.txt /tmp
RUN pip install -r requirements.txt && pip install -r requirements-dev.txt

WORKDIR /workspace
CMD ["sh"]
