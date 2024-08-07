import os

def reduce_bvh_frames(input_file, output_file, reduction_factor=4):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Tìm vị trí bắt đầu của phần MOTION
    motion_index = lines.index('MOTION\n')

    # Đọc số lượng khung hình và thời gian khung hình
    frames = int(lines[motion_index + 1].split(':')[1])
    frame_time = float(lines[motion_index + 2].split(':')[1])

    # Tính toán giá trị mới
    new_frames = frames // reduction_factor
    new_frame_time = frame_time * reduction_factor

    # Cập nhật các dòng
    lines[motion_index + 1] = f'Frames: {new_frames}\n'
    lines[motion_index + 2] = f'Frame Time: {new_frame_time}\n'

    # Lọc các khung hình và loại bỏ ký tự tab
    motion_data = lines[motion_index + 3:]
    reduced_motion_data = [line.replace('\t', ' ').lstrip() for line in motion_data[::reduction_factor]]

    # Ghi file mới
    with open(output_file, 'w') as f:
        # Ghi phần đầu file, thay thế tab bằng dấu cách
        for line in lines[:motion_index + 3]:
            f.write(line.replace('\t', '    '))
        # Ghi dữ liệu chuyển động đã giảm
        f.writelines(reduced_motion_data)

    print(f"Đã giảm số lượng khung hình từ {frames} xuống {new_frames}")
    print(f"Đã tăng thời gian khung hình từ {frame_time} lên {new_frame_time}")

# Sử dụng script
input_file = 'examples/bvh/fair1/dab.bvh'
output_file = 'examples/bvh/fair1/dab_reduced.bvh'
reduce_bvh_frames(input_file, output_file, reduction_factor=2)
