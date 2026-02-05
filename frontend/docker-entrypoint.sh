#!/bin/sh
# Inject API_URL environment variable into JavaScript at runtime
export API_URL=${API_URL:-}

# Create a simple JS file that sets window.API_URL if env var exists
cat > /usr/share/nginx/html/js/env-config.js << EOF
// Runtime environment configuration - injected by Docker entrypoint
if ('${API_URL}') {
    window.API_URL = '${API_URL}';
}
EOF

# Start nginx
exec nginx -g "daemon off;"
