FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install Flask_Admin

RUN pip install -U numpy

RUN pip install cryptography

COPY . .

EXPOSE 5000

CMD [ "python", "./korpustoken.py" ]