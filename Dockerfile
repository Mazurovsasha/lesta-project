FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# RUN addgroup --system appuser && adduser --system --ingroup appuser appuser

COPY . .


# RUN chown -R appuser:appuser /app
COPY entrypoint.sh /entrypoint.sh
# RUN chown appuser:appuser /entrypoint.sh && chmod +x /entrypoint.sh
RUN chmod +x /entrypoint.sh
# USER appuser

CMD ["/entrypoint.sh"]

