FROM python:3.7.0
WORKDIR /
COPY DataQualityEngine-dev/ .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8005
ENTRYPOINT ["/bin/bash", "/serve-api.sh" ] 




