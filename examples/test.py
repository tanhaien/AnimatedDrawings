from locust import HttpUser, task, between
from locust.contrib.fasthttp import FastHttpUser
import os

class RenderGifUser(FastHttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        # Tải ảnh một lần khi bắt đầu
        self.image_data = open("/home/p06lab/PHYS/AnimatedDrawings/examples/drawings/garlic.png", "rb").read()

    @task
    def render_gif(self):
        # Sử dụng dữ liệu ảnh đã tải
        self.client.post("/render_gif", files={"image": ("garlic.png", self.image_data, "image/png")})

    @task
    def get_gif(self):
        # Thêm task để lấy GIF đã tạo
        self.client.get("/get_gif/some_hash_value")  # Thay thế some_hash_value bằng giá trị hash thực tế
