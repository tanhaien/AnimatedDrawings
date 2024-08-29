# Bước 1: Chạy Model AI
``` cd PHYS/AnimatedDrawings/torchserve
 docker run -d -p 8080:8080 -p 8081:8081 docker_torchserve```

# Bước 2: Chạy server 
```cd ../examples
 python app.py
 ssh -o ServerAliveInterval=60 -R 80:localhost:5000 serveo.net```
