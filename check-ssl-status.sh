#!/bin/bash

echo "=== SSL Certificate Status Check ==="
echo ""

echo "1. Checking if certificates exist on host..."
if [ -f "./certbot/conf/live/carkeysamara.ru/fullchain.pem" ]; then
    echo "✅ Certificate files found!"
    ls -lh ./certbot/conf/live/carkeysamara.ru/
else
    echo "❌ NO CERTIFICATES FOUND - You need to run ./init-letsencrypt.sh first!"
fi

echo ""
echo "2. Checking certificate details (if exists)..."
if [ -f "./certbot/conf/live/carkeysamara.ru/fullchain.pem" ]; then
    docker-compose -f docker-compose.prod.yml run --rm certbot certificates
else
    echo "Skipped - no certificates"
fi

echo ""
echo "3. Checking nginx status..."
docker-compose -f docker-compose.prod.yml ps nginx

echo ""
echo "4. Testing HTTPS connectivity..."
echo "HTTP test:"
curl -I http://carkeysamara.ru 2>&1 | head -5
echo ""
echo "HTTPS test:"
curl -I https://carkeysamara.ru 2>&1 | head -5

echo ""
echo "5. Nginx error logs (last 10 lines)..."
docker-compose -f docker-compose.prod.yml logs nginx 2>&1 | tail -10

echo ""
echo "=== Status Check Complete ==="
