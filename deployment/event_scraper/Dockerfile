FROM python:3.12-slim

ARG SCRAPER_USER=scraper
ARG SCRAPER_PASS

RUN apt update && apt install -y \
    wget \
    unzip \
    curl \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm-dev \
    libu2f-udev \
    xdg-utils \
    ca-certificates \
    openssh-server

RUN useradd --shell /bin/bash -u 1000 $SCRAPER_USER \
    && mkdir -p /home/$SCRAPER_USER/.ssh \
    && chmod 700 /home/$SCRAPER_USER/.ssh \
    && chown -R $SCRAPER_USER:$SCRAPER_USER /home/$SCRAPER_USER

RUN mkdir -p /var/run/sshd \
    && echo "$SCRAPER_USER:$SCRAPER_PASS" | chpasswd \
    && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -i 's@session required pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd \
    && echo "export VISIBLE=now" >> /etc/profile

# Allow SSH to start without privilege issues
RUN chmod 755 /var/run/sshd

RUN wget -qO- https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb > /tmp/chrome.deb \
    && apt install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb

ARG CHROMEDRIVER_VERSION=134.0.6998.165
RUN wget -q "https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip" \
    && unzip chromedriver-linux64.zip \
    && mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf chromedriver-linux64.zip chromedriver-linux64
    
RUN mkdir -p /app

RUN pip install --upgrade pip && pip install --no-cache-dir selenium

COPY browser.py /app/
COPY common.py /app/
COPY config.py /app/
COPY init.py /app/
COPY scraper.py /app/
COPY smtp.py /app/

RUN chown -R $SCRAPER_USER:$SCRAPER_USER /app
#USER $SCRAPER_USER

WORKDIR /app

CMD ["/usr/sbin/sshd", "-D"]
