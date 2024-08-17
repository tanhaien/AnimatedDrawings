import cProfile
import pstats
import io
from animated_drawings import render
import time

def benchmark_gif_render():
    start_time = time.time()
    
    # Sử dụng cProfile để profile quá trình render
    pr = cProfile.Profile()
    pr.enable()
    
    render.start("./examples/config/mvc/export_gif_example.yaml")
    
    pr.disable()
    
    end_time = time.time()
    
    # In thông số tổng quát
    print(f"Render time: {end_time - start_time:.2f} seconds")
    
 #     Xử lý và in kết quả chi tiết từ cProfile
    # s = io.StringIO()
    # ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    # ps.print_stats(1000)  # In top 20 hàm tốn nhiều thời gian nhất
    # print(s.getvalue())


from PIL import Image

def count_gif_frames(gif_path):
    with Image.open(gif_path) as img:
        frames = 0
        try:
            while True:
                frames += 1
                img.seek(img.tell() + 1)
        except EOFError:
            pass
    return frames



if __name__ == "__main__":
    benchmark_gif_render()
    # Sử dụng hàm
    gif_path = "./video.gif"
    frame_count = count_gif_frames(gif_path)
    print(f"Số frame trong GIF: {frame_count}")
