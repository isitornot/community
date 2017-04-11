FROM python:3.6
MAINTAINER Trevor R.H. Clarke <trevor@notcows.com>

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/
ADD https://github.com/isitornot/common/releases/download/v1.1.1-alpha/isitornot-1.1.1-py3-none-any.whl /tmp/wheels/
RUN pip install wheel && pip install --find-links /tmp/wheels --no-cache-dir -r requirements.txt

COPY . /usr/src/app/

WORKDIR /usr/src/app/isitornot
ENV CONFIG_FILE=/etc/isitornot
EXPOSE 9000
CMD python -mcommunity.main
