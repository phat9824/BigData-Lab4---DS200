# Student Performance Prediction System

Hệ thống dự đoán kết quả học tập của sinh viên sử dụng dòng dữ liệu (data streaming) với Apache Spark và học máy.

## 📌 Mô tả

Dự án này xây dựng một hệ thống dự đoán **điểm thi** của sinh viên dựa trên các yếu tố như: thời gian học, thời gian xem phim, thói quen ăn uống, giấc ngủ, v.v. Hệ thống được triển khai với:

- **Apache Spark Streaming**: Xử lý dữ liệu theo thời gian thực
- **Hồi quy tuyến tính**: Dự đoán điểm số đầu ra
- **Socket-based Streaming**: Mô phỏng luồng dữ liệu thời gian thực

## 🗂️ Cấu trúc dự án

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

## 📊 Dataset

- Dataset được sử dụng: [Student Habits and Academic Performance Dataset](https://www.kaggle.com/datasets/aryan208/student-habits-and-academic-performance-dataset/data)
- Dữ liệu bao gồm thông tin hành vi, lối sống và kết quả học tập của sinh viên.

## ⚙️ Yêu cầu hệ thống

- Python 3.7+
- Apache Spark 3.0+
- PySpark
- NumPy
- Pandas
- tqdm

## 🚀 Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd student-performance-prediction
```

2. Cài đặt các gói phụ thuộc:
```bash
pip install pyspark pandas numpy tqdm
```

3. Đặt dataset:
```bash
mkdir -p datasets
# Tải Student_Data.csv từ Kaggle và đặt vào thư mục datasets/
```

## ▶️ Cách sử dụng

### Tuỳ chọn thay đổi cổng kết nối

Bạn có thể thay đổi cổng mặc định 6100 trong 2 tệp:

- `stream.py`:  
  ```python
  TCP_PORT = 6100
  ```

- `trainer.py` trong class `SparkConfig`:  
  ```python
  port = 6100
  ```

### Bước chạy hệ thống

1. **Terminal 1: Chạy server phát dữ liệu**
```bash
python stream.py --batch-size 10 --sleep 3
```

Tham số:
- `--batch-size`: Số mẫu gửi mỗi lần
- `--sleep`: Thời gian chờ giữa các batch
- `--endless`: Phát vô hạn (mặc định: False)
- `--split`: train/test (mặc định: train)

2. **Terminal 2: Chạy ứng dụng Spark**
```bash
python main.py
```

## 🧠 Điều chỉnh mô hình

Trong `main.py`, bạn có thể điều chỉnh các siêu tham số của mô hình hồi quy tuyến tính:

```python
lr_model = LinearRegressionModel(elasticNetParam=0.1, regParam=0.1)
```

- `elasticNetParam`: 0 = Ridge, 1 = Lasso
- `regParam`: Độ mạnh của regularization

## 📈 Đánh giá kết quả

Hệ thống sử dụng các chỉ số sau để đánh giá độ chính xác:
- **RMSE**: Sai số căn trung bình bình phương
- **MSE**: Sai số trung bình bình phương
- **MAE**: Sai số tuyệt đối trung bình
- **R²**: Hệ số xác định

## 🔄 Xử lý dữ liệu

- Các tính năng phân loại được **mã hóa one-hot**
- Dữ liệu được **chuẩn hóa**
- Mô hình học máy sử dụng hồi quy tuyến tính để dự đoán `exam_score`

## 🛠️ Khắc phục sự cố

- **Lỗi kết nối**: Đảm bảo cổng chưa bị chiếm dụng
- **Lỗi Spark**: Kiểm tra cấu hình và cài đặt Spark
- **Lỗi dữ liệu**: Xác minh định dạng và nội dung file CSV đầu vào
