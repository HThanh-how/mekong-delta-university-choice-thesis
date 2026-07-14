# Luận văn LaTeX - Đại học Cần Thơ

> **TRẠNG THÁI BẢN DEMO:** Chương 3 và `data/survey_synthetic_486.csv` hiện sử dụng dữ liệu mô phỏng để kiểm thử quy trình SPSS và dàn trang. Đây không phải kết quả khảo sát thực địa và không dùng để nộp/bảo vệ. Dữ liệu thật sẽ được làm sạch, phân tích và thay thế ở phiên bản chính thức.

Đề tài: **Các yếu tố ảnh hưởng đến quyết định chọn trường/ngành học của học sinh THPT tại các tỉnh Đồng bằng sông Cửu Long**.

Tác giả: **Phạm Duy Tân (B2407059)**, ngành Kỹ thuật điện, K50, Khoa Bách khoa, Trường Đại học Cần Thơ. Cán bộ hướng dẫn: **TS. Ngô Quang Hiếu**.

Thư mục `analysis/` chứa syntax SPSS; `data/` chứa bộ dữ liệu minh họa 486 quan sát để kiểm tra quy trình. Bộ dữ liệu này không phải dữ liệu khảo sát thực địa.

## Biên dịch

Yêu cầu TeX Live/MiKTeX có XeLaTeX và BibTeX:

```bash
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

PDF được tạo tại `output/pdf/luan-van-chon-truong-nganh-dbscl.pdf` khi chạy GitHub Actions. Bản biên dịch cục bộ là `main.pdf`.

## Trước khi nộp

Thay thông tin trong `main.tex` (họ tên, MSSV, ngành, khoa, giảng viên hướng dẫn), thay số liệu minh họa ở Chương 3 bằng dữ liệu khảo sát thật, cập nhật kết quả phân tích và xin xác nhận biểu mẫu chính thức từ khoa.
