#!/bin/bash

echo "=== SSL Setup Debug Script ==="
echo ""

echo "1. Checking certbot directories on host..."
ls -la ./certbot/ 2>/dev/null || echo "❌ ./certbot/ doesn't exist"
ls -la ./certbot/www/.well-known/acme-challenge/ 2>/dev/null || echo "❌ Challenge directory doesn't exist"

echo ""
echo "2. Checking files in nginx container..."
docker-compose -f docker-compose.prod.yml exec nginx ls -la /var/www/certbot/.well-known/acme-challenge/ 2>/dev/null || echo "❌ Directory not accessible in nginx container"

echo ""
echo "3. Testing HTTP access to challenge path..."
curl -I http://carkeysamara.ru/.well-known/acme-challenge/test.txt 2>/dev/null || echo "❌ HTTP test failed"

echo ""
echo "4. Checking nginx configuration..."
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

echo ""
echo "5. Recent nginx logs..."
docker-compose -f docker-compose.prod.yml logs nginx --tail=10

echo ""
echo "=== Debug Complete ==="
