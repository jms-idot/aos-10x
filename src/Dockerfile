FROM python:3-alpine
ADD tenx*.py /
ADD seattle-weather.csv /
EXPOSE 8080
CMD ["python", "./tenx.py", "--server", "--port", "8080", "seattle-weather.csv"]