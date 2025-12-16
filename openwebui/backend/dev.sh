export CORS_ALLOW_ORIGIN="${CORS_ALLOW_ORIGIN:-*}"
PORT="${PORT:-8767}"
uvicorn open_webui.main:app --port $PORT --host 0.0.0.0 --forwarded-allow-ips '*' --reload &
echo $! > /tmp/openwebui_backend.pid
