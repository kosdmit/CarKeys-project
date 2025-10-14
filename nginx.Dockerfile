FROM nginx:1.23-alpine

# Remove default nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx/nginx.conf /etc/nginx/conf.d/

# Create directory for static files
RUN mkdir -p /vol/static