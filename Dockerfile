FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN python -m pip install -U numpy==1.19.5 telebot --no-build-isolation

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install Flask_Admin

RUN pip install -U tzlocal==2.1 cryptography

COPY . .

EXPOSE 5000

CMD [ "python", "./korpustoken.py" ]