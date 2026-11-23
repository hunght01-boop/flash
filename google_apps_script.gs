// Dán FILE_ID của file tu_vung_tieng_trung.md trên Google Drive vào giữa dấu ngoặc kép.
// Cách lấy FILE_ID: Mở file trên Google Drive -> Chia sẻ -> Sao chép đường liên kết.
// Link có dạng: https://drive.google.com/file/d/<FILE_ID>/view?usp=sharing
const FILE_ID = "DAN_FILE_ID_CUA_BAN_VAO_DAY";

function doGet(e) {
  const file = DriveApp.getFileById(FILE_ID);
  const content = file.getBlob().getDataAsString("UTF-8");
  const payload = {
    name: file.getName(),
    updatedAt: file.getLastUpdated().toISOString(),
    markdown: content
  };
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
