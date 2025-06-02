cat > gunicorn_config.py << 'EOL'
bind = "0.0.0.0:10000"
workers = 2
threads = 2
timeout = 120
EOL