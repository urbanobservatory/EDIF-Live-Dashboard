FROM python:3.9
RUN pip install dash pandas plotly python-dotenv requests numpy dash-bootstrap-components
ADD code/ /code/
WORKDIR /code/
CMD  python3 save_env_to_file.py && python3 -u app.py