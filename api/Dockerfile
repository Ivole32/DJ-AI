FROM python:3.11-slim
WORKDIR /app
# Copy API code
COPY api/ .
# Copy ML model requirements
COPY ml_model/requirements.txt /app/ml_model_requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
	&& pip install --no-cache-dir -r ml_model_requirements.txt
EXPOSE 8080
CMD ["python", "main.py"]
