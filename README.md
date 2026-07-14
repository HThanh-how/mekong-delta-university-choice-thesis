# Luận văn LaTeX - Đại học Cần Thơ

Đề tài: **Các yếu tố ảnh hưởng đến quyết định chọn trường/ngành học của học sinh THPT tại các tỉnh Đồng bằng sông Cửu Long**.

Tác giả: **Phạm Duy Tân (B2407059)**, ngành Kỹ thuật điện, K50, Khoa Kỹ thuật điện, Trường Bách khoa, Trường Đại học Cần Thơ. Cán bộ hướng dẫn: **TS. Ngô Quang Hiếu**.

Thư mục `analysis/` chứa syntax SPSS và mã Python để tính lại kết quả; `data/` chứa bộ dữ liệu khảo sát gồm 486 quan sát.

## Biên dịch

Yêu cầu TeX Live/MiKTeX có XeLaTeX và BibTeX. Trên PowerShell:

```powershell
xelatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex
Move-Item -Force main.pdf output/pdf/luan-van-chon-truong-nganh-dbscl.pdf
```

Để kiểm tra lại số liệu bằng Python, cài `pandas`, `numpy`, `scipy`, `statsmodels`, `factor_analyzer` rồi chạy:

```powershell
python analysis/recompute_results.py
```

PDF hoàn chỉnh được lưu tại `output/pdf/luan-van-chon-truong-nganh-dbscl.pdf`.

## Trước khi nộp

Kiểm tra thông tin trong `main.tex` (họ tên, MSSV, ngành, khoa, giảng viên hướng dẫn), cập nhật kết quả phân tích khi dữ liệu thay đổi và xin xác nhận biểu mẫu chính thức từ khoa.
