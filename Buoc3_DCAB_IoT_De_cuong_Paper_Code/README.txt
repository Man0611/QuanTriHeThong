BỘ TÀI LIỆU NGHIÊN CỨU DCAB-IoT (16/11/2026)

1. 01_De_cuong_luan_van_DriftCost_IoT.docx — đề cương luận văn, mục tiêu, khoảng trống, toán học, thuật toán, benchmark và kế hoạch.
2. 02_Du_thao_paper_quoc_te_DCAB_IoT.docx — manuscript ban đầu với abstract tiếng Anh; nội dung chi tiết tiếng Việt để rà soát học thuật.
3. driftcost_demo.py — simulator giáo dục tự xây dựng, KHÔNG phải bản sao chính thức của thuật toán trong paper tham khảo.
4. demo_stream.csv — dữ liệu tổng hợp được tạo bởi mã Python, không dùng để khẳng định hiệu quả trên dữ liệu IoT thật.

CHẠY CODE (Python >=3.9, không cần cài package):
  python driftcost_demo.py
Sẽ ghi 3 dòng so sánh và tạo lại demo_stream.csv tại thư mục làm việc.

CÁC GIỚI HẠN QUAN TRỌNG:
- Không có số liệu SOTA từ thử nghiệm thật trong bộ Word này.
- Các mệnh đề chứng minh không suy ra optimality toàn hệ thống.
- Chứng minh conformal đòi hỏi exchangeability; không bảo đảm khi drift.
- Chưa thể khẳng định đóng góp có tính mới tuyệt đối nếu chưa rà soát tài liệu rộng và tái lập baseline.
- SWaT phải xin phép iTrust; không kèm hoặc tái phân phối.
