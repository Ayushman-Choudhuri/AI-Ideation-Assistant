FROM python:3.9

RUN mkdir -p /usr/sokrates
WORKDIR /usr/sokrates

RUN apt-get update && apt-get install -y 

COPY ./requirements.txt ./ 
COPY ./src ./src


RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash", "-c", "cd src/ai_ideation_assistant && streamlit run app.py"]
