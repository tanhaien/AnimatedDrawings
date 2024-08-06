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
    print(f"Tổng thời gian render: {end_time - start_time:.2f} giây")
    
# #     Xử lý và in kết quả chi tiết từ cProfile
    # s = io.StringIO()
    # ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    # ps.print_stats(1000)  # In top 20 hàm tốn nhiều thời gian nhất
    # print(s.getvalue())

if __name__ == "__main__":
    benchmark_gif_render()