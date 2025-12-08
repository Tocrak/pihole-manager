FROM python:3.12.12-alpine
WORKDIR /app

# Install the application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY ./ /app
EXPOSE 8100

# Setup an app user so the container doesn't run as the root user
RUN adduser -S piholemgr
USER piholemgr

CMD ["sh", "/app/run.sh"]
