FROM python:3.9

WORKDIR /random-datagen

COPY ./requirements.txt ./requirement.txt

RUN pip3 install -r requirement.txt

EXPOSE 8501

COPY ["./docker/config.py", "./libs/datagen_functions.py", "./libs/form_checks.py", "./libs/datagen.py", "/random-datagen/libs/"]
COPY ["./docs/docs.md", "/random-datagen/docs/"]
COPY ["webapp.py", "/random-datagen/"]

CMD ["streamlit", "run", "webapp.py", "&"]