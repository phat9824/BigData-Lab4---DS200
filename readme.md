# Student Performance Prediction System

Hệ thống dự đoán kết quả học tập của sinh viên sử dụng dòng dữ liệu (data streaming) với Apache Spark và học máy.

## Mô tả

Dự án này xây dựng một hệ thống dự đoán điểm thi của sinh viên dựa trên các yếu tố khác nhau như giờ học, giờ xem phim, chế độ ăn uống, giấc ngủ, v.v. Hệ thống sử dụng:
- **Apache Spark Streaming**: Để xử lý dữ liệu theo thời gian thực
- **Mô hình hồi quy tuyến tính**: Để dự đoán điểm số
- **Socket-based streaming**: Mô phỏng luồng dữ liệu thời gian thực

## Cấu trúc dự án

```
/project/
    ├── transforms.py        # Tiền xử lý dữ liệu
    ├── dataloader.py        # Tải và xử lý dữ liệu từ luồng
    ├── trainer.py           # Huấn luyện và đánh giá mô hình
    ├── model.py             # Định nghĩa mô hình học máy
    ├── main.py              # Script chính để chạy hệ thống
    ├── stream.py            # Phát dữ liệu qua socket
    ├── README.md            # Hướng dẫn sử dụng
    └── datasets/
        └── Student_Data.csv # Dữ liệu sinh viên
```

## Yêu cầu hệ thống

- Python 3.7+
- Apache Spark 3.0+
- PySpark
- NumPy
- Pandas
- tqdm

## Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd student-performance-prediction
```

2. Cài đặt các gói phụ thuộc:
```bash
pip install pyspark pandas numpy tqdm
```

3. Đặt dữ liệu của bạn:
```bash
mkdir -p datasets
# Đặt tệp Student_Data.csv vào thư mục datasets
```

## Cách sử dụng

### Thay đổi cổng kết nối (Không bắt buộc)

Nếu bạn muốn sử dụng cổng khác thay vì cổng mặc định 6100, hãy sửa đổi các tệp sau:

1. Trong `stream.py`, tìm và sửa:
```python
TCP_PORT = 6100  # Thay đổi thành cổng bạn muốn
```

2. Trong `trainer.py`, tìm và sửa trong class `SparkConfig`:
```python
port = 6100  # Thay đổi thành cùng cổng như trong stream.py
```

### Chạy hệ thống

1. **Chạy server stream**: Mở terminal đầu tiên
```bash
python stream.py --batch-size 10 --sleep 3
```

Các tham số:
- `--batch-size` hoặc `-b`: Số lượng mẫu trong mỗi batch (bắt buộc)
- `--sleep` hoặc `-t`: Thời gian nghỉ giữa các batch (giây, mặc định: 3)
- `--endless` hoặc `-e`: Nếu True, sẽ gửi dữ liệu liên tục (mặc định: False)
- `--split` hoặc `-s`: Chỉ định phần dữ liệu (train/test, mặc định: train)

2. **Chạy ứng dụng Spark**: Mở terminal thứ hai
```bash
python main.py
```

## Điều chỉnh mô hình

Bạn có thể điều chỉnh siêu tham số của mô hình trong `main.py`:

```python
# Thay đổi siêu tham số
lr_model = LinearRegressionModel(elasticNetParam=0.1, regParam=0.1)
```

- `elasticNetParam`: Tham số cho ElasticNet (0 = Ridge, 1 = Lasso)
- `regParam`: Tham số điều chỉnh (regularization parameter)

## Đánh giá kết quả

Hệ thống đánh giá mô hình bằng các chỉ số:
- **RMSE** (Root Mean Square Error): Lỗi trung bình bình phương
- **MSE** (Mean Square Error): Lỗi trung bình bình phương
- **MAE** (Mean Absolute Error): Lỗi tuyệt đối trung bình
- **R2** (R-squared): Hệ số xác định

## Xử lý dữ liệu

- **Dữ liệu đầu vào**: Hệ thống xử lý dữ liệu sinh viên với các tính năng số và phân loại.
- **Tiền xử lý**: Các tính năng phân loại được mã hóa one-hot, tất cả tính năng được chuẩn hóa.
- **Mô hình**: Sử dụng hồi quy tuyến tính để dự đoán điểm số dựa trên các tính năng.

## Khắc phục sự cố

1. **Lỗi kết nối**: Đảm bảo không có tiến trình nào đang sử dụng cổng đã chỉ định.
2. **Lỗi Spark**: Kiểm tra xem Spark đã được cài đặt và cấu hình đúng chưa.
3. **Lỗi dữ liệu**: Đảm bảo định dạng dữ liệu của bạn phù hợp với cấu trúc mong đợi.

## Ghi chú

- Đảm bảo server stream đang chạy trước khi khởi động ứng dụng Spark.
- Đối với datasets lớn, hãy cân nhắc điều chỉnh batch_size để tối ưu hiệu suất.
- Hệ thống được thiết kế để chạy cục bộ, nhưng có thể được mở rộng để chạy trên cụm Spark.
