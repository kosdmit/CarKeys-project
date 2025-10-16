#!/bin/bash

# SSL Certificate Initialization Script for Let's Encrypt
# This script obtains SSL certificates for your domains using certbot

set -e

domains=(carkeysamara.ru www.carkeysamara.ru)
# Note: Add carkeysamara.online www.carkeysamara.online when DNS is configured
rsa_key_size=4096
data_path="./certbot"
email="kosdmit@hotmail.com" # Adding a valid email is strongly recommended
staging=0 # Set to 1 if you're testing your setup to avoid hitting request limits

echo "### Preparing directories ..."
mkdir -p "$data_path/conf"
mkdir -p "$data_path/www"

if [ -d "$data_path/conf/live/${domains[0]}" ]; then
  read -p "Existing data found for ${domains[0]}. Continue and replace existing certificate? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    exit
  fi
fi

echo "### Downloading recommended TLS parameters ..."
mkdir -p "$data_path/conf"
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"

echo "### Creating dummy certificate for ${domains[0]} ..."
path="/etc/letsencrypt/live/${domains[0]}"
mkdir -p "$data_path/conf/live/${domains[0]}"
docker-compose -f docker-compose.prod.yml run --rm --entrypoint "\
  sh -c 'mkdir -p $path && openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1 \
    -keyout $path/privkey.pem \
    -out $path/fullchain.pem \
    -subj /CN=localhost'" certbot
echo

echo "### Starting nginx ..."
# Stop and remove existing containers to avoid conflicts
docker-compose -f docker-compose.prod.yml down
# Start all services
docker-compose -f docker-compose.prod.yml up -d

echo "### Waiting for services to be ready..."
sleep 10

echo "### Testing ACME challenge path..."
# Create a test file in the webroot
mkdir -p "$data_path/www/.well-known/acme-challenge"
echo "test" > "$data_path/www/.well-known/acme-challenge/test.txt"
# Give nginx time to pick it up
sleep 2
echo

echo "### Deleting dummy certificate for ${domains[0]} ..."
docker-compose -f docker-compose.prod.yml run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/${domains[0]} && \
  rm -Rf /etc/letsencrypt/archive/${domains[0]} && \
  rm -Rf /etc/letsencrypt/renewal/${domains[0]}.conf" certbot
echo

echo "### Requesting Let's Encrypt certificate for ${domains[0]} ..."
# Join $domains to -d args
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

# Select appropriate email arg
case "$email" in
  "") email_arg="--register-unsafely-without-email" ;;
  *) email_arg="--email $email" ;;
esac

# Enable staging mode if needed
if [ $staging != "0" ]; then staging_arg="--staging"; fi

docker-compose -f docker-compose.prod.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $email_arg \
    $domain_args \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal" certbot
echo

echo "### Reloading nginx ..."
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload

echo "### Certificate setup complete!"
