# Hướng dẫn sử dụng & Đồng bộ từ Google Drive / Sheets

Thư mục `Flash Card/` chứa toàn bộ ứng dụng học từ vựng tiếng Trung:
- `tu_vung_tieng_trung.md`: **Kho từ vựng gốc** dạng bảng Markdown để bạn đọc, chỉnh sửa hoặc thêm từ mới.
- `tu_vung_google_sheets.csv`: **Bản CSV chuẩn 5 cột** để nhập nhanh vào Google Sheets chỉ trong 1 click.
- `google_apps_script.gs`: **Đoạn code 15 dòng** để đọc trực tiếp file `.md` từ Google Drive (không cần deploy lại web).
- `index.html`: **Ứng dụng Flashcard** chạy mượt trên máy tính, iPad, iPhone và Android.
- `audio/female/` & `audio/male/`: 758 file đọc chuẩn bản xứ giọng **Nữ** (`XiaoxiaoNeural`) và **Nam** (`YunxiNeural`).
- `build_flashcard.py`: Script tự động cập nhật `index.html`, xuất `tu_vung_google_sheets.csv` và sinh MP3 Nam/Nữ cho từ mới.

---

## 1. Mở nhanh trên Máy tính (Mac / Windows)
- Nhấp đúp trực tiếp vào file `index.html` để mở bằng Chrome / Safari / Edge.
- **Phím tắt máy tính:** `Space` lật thẻ • `← / →` chuyển thẻ • `1` giọng **Nữ** • `2` giọng **Nam** • `K` Đã thuộc • `U` Chưa nhớ.

---

## 2. Đẩy lên Link Tĩnh miễn phí (chỉ cần làm 1 LẦN DUY NHẤT)

> Trên iPhone/iPad, nếu mở trực tiếp file `.html` trong app Google Drive hoặc Tệp (Files), iOS sẽ chặn âm thanh. Chỉ cần đưa thư mục `Flash Card` lên 1 đường link HTTPS miễn phí 1 lần duy nhất, sau đó mỗi khi thêm từ mới bạn chỉ bấm **🔄 Đồng bộ** trên app mà không cần deploy lại!

### Cách A: Netlify Drop (Nhanh nhất – 1 phút)
1. Truy cập **https://app.netlify.com/drop** và đăng nhập miễn phí (Google / Email).
2. Mở Finder, **kéo và thả cả thư mục `Flash Card`** vào khung upload.
3. Chờ vài giây → Netlify cấp đường link dạng `https://ten-ngau-nhien.netlify.app` (có thể đổi tên tại **Site configuration → Change site name**, ví dụ `https://hung-tieng-trung.netlify.app`).

### Cách B: GitHub Pages
1. Tạo 1 Repository **Public** trên GitHub, upload toàn bộ các file bên trong `Flash Card/` (`index.html`, `manifest.json`, `sw.js`, `icon-192.png`, `icon-512.png`, `audio/`) lên nhánh `main`.
2. Vào **Settings → Pages → Branch: `main` / `/ (root)` → Save** để nhận link `https://<ten-github>.github.io/<ten-repo>/`.

### Cài thành App trên iPhone / iPad (Safari):
1. Mở link vừa tạo bằng **Safari** → bấm nút **Chia sẻ** (ô vuông mũi tên lên) → **Thêm vào MH chính** (*Add to Home Screen*) → **Thêm**.

---

## 3. Đồng bộ từ mới trực tiếp từ Google Drive (Không cần deploy lại web)

Ứng dụng hỗ trợ **CẢ 2 CÁCH** dưới đây (chỉ cần dán link vào mục **☰ → Đồng bộ trực tuyến**, app tự nhận diện định dạng `.md` hay `.csv`):

> **Lưu ý tài khoản công ty (`ckjvn.vn`):** Một số Workspace công ty chặn chế độ chia sẻ công khai (*Anyone*). Nếu khi bấm Đồng bộ báo lỗi quyền truy cập, bạn chỉ cần để bản `tu_vung_tieng_trung.md` hoặc Google Sheet trên **Google Drive cá nhân (`@gmail.com`)** là chạy thông suốt 100%.

### Cách 1: Sửa trực tiếp file `tu_vung_tieng_trung.md` trên Google Drive (Qua Apps Script)
1. **Lấy File ID:** Trên Google Drive, chuột phải vào `tu_vung_tieng_trung.md` → **Chia sẻ** → đổi quyền xem thành **Bất kỳ ai có đường liên kết** → **Sao chép đường liên kết**.
   - Link có dạng `https://drive.google.com/file/d/ABC123XYZ.../view?usp=sharing` → phần `ABC123XYZ...` chính là **FILE_ID**.
2. **Tạo cầu nối Google Apps Script (chỉ làm 1 lần):**
   - Vào **https://script.google.com** → bấm **Dự án mới** (*New project*).
   - Xóa hết code mặc định, dán toàn bộ nội dung file `google_apps_script.gs` vào và thay `DAN_FILE_ID_CUA_BAN_VAO_DAY` bằng `FILE_ID` ở bước 1 → bấm **Lưu (Ctrl+S / Cmd+S)**.
   - Bấm **Triển khai (Deploy) → Triển khai mới (New deployment)** → chọn loại **Ứng dụng web (Web app)**:
     - *Thực thi với tư cách (Execute as):* **Tôi (Me)**
     - *Người có quyền truy cập (Who has access):* **Bất kỳ ai (Anyone)**
   - Bấm **Triển khai** → cấp quyền đọc Drive → sao chép đường link kết thúc bằng `/exec`.
3. **Gắn vào App Flashcard:**
   - Mở App trên điện thoại/iPad/máy tính → bấm **☰** (hoặc **🔄**) → dán link `/exec` vào ô **Đồng bộ trực tuyến** → bấm **🔄 Lưu link & Đồng bộ ngay**.
4. **Hàng ngày:** Chỉ cần thêm dòng mới vào `tu_vung_tieng_trung.md` trên Google Drive rồi bấm **🔄** trên app!

### Cách 2: Sửa trực tiếp bằng app Google Sheets trên Điện thoại / iPad
1. Tạo một bảng tính mới trên Google Sheets → vào **Tệp (File) → Nhập (Import) → Tải lên** và chọn file `tu_vung_google_sheets.csv` có sẵn trong thư mục `Flash Card`.
2. Bật xuất bản CSV (chỉ làm 1 lần): vào **Tệp (File) → Chia sẻ (Share) → Xuất bản lên web (Publish to web)**:
   - Chọn trang tính hiện tại và đổi định dạng từ *Trang web* sang **Giá trị được phân cách bằng dấu phẩy (.csv)** → bấm **Xuất bản (Publish)** → sao chép link `.csv`.
3. Mở App Flashcard → bấm **☰** (hoặc **🔄**) → dán link `.csv` vào ô **Đồng bộ trực tuyến** → bấm **🔄 Lưu link & Đồng bộ ngay**.
4. **Hàng ngày:** Mở app Google Sheets trên iPhone gõ thêm dòng mới (có thể bỏ trống cột Pinyin, app tự điền!) → quay lại Flashcard bấm **🔄** là học ngay!

---

## 4. Nâng cấp từ mới lên giọng HD MP3 (tùy chọn, làm định kỳ)
- Tất cả 379 từ gốc luôn phát bằng **HD MP3** chuẩn bản xứ; các từ mới bạn thêm qua Google Drive / Sheets sẽ dùng **giọng đọc trình duyệt (TTS)** để nghe được ngay lập tức.
- Khi tích lũy được nhiều từ mới (ví dụ mỗi tháng 1 lần), bạn chỉ cần chạy `uv run build_flashcard.py` tại thư mục `Flash Card` để tạo thêm file MP3 cho các từ mới và kéo thả cập nhật lên Netlify 1 lần.
