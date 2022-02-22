FROM python:3
RUN apt update
RUN apt install -y at
RUN git clone git@github.com:dbmage/tur-dc-bot.git /app/
cp /app/requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt &&\
rm /tmp/requirements.txt
CMD [ "python", "/app/bot.py" ]
