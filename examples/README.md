# Step 1: Run Model AI
```
cd PHYS/AnimatedDrawings/torchserve
docker run -d -p 8080:8080 -p 8081:8081 docker_torchserve
```

# Step 2: Run Server
```
cd ../examples
python app.py
ssh -o ServerAliveInterval=60 -R 80:localhost:5000 serveo.net
```
