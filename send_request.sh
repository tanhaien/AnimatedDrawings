#!/bin/bash

# Số lượng request cần gửi
NUM_REQUESTS=3

# Hàm gửi request
send_request() {
  curl -X POST \
    -F "image=@/home/p06lab/PHYS/AnimatedDrawings/examples/drawings/garlic.png" \
    -F "motion=/home/p06lab/PHYS/AnimatedDrawings/examples/config/motion/dab.yaml" \
    http://localhost:5000/render_gif &
}

# Gửi các request đồng thời
for i in $(seq 1 $NUM_REQUESTS); do
  send_request
done

# Đợi tất cả các request hoàn thành
wait

echo "Đã gửi $NUM_REQUESTS request."
