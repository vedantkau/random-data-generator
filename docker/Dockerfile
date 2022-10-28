FROM python:3.9

WORKDIR /random-datagen

COPY ./docker/requirement.txt ./requirement.txt

RUN pip3 install -r requirement.txt

EXPOSE 8501

COPY ["./docker/config.py", "./libs/datagen_functions.py", "./libs/form_checks.py", "/random-datagen/libs/"]
COPY ["./docs/pattern_docs.md", "./docs/about.md", "/random-datagen/docs/"]
copy ["webapp.py", "/random-datagen/"]

CMD ["streamlit", "run", "webapp.py"]