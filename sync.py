import os
import csv
import json
import requests

# Dán trực tiếp link xuất bản CSV của bạn vào đây
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRQhdd9aNxY8pBChZgUILO8JyC_cpl9EmIgM5kwUDQ5X3PsGFdVuAfCWn1SE2GzRLgxkBEAGwTz1Hhz/pub?gid=0&single=true&output=csv"

JSON_FILE = "lessons.json"

def load_existing_data():
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_data(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def fetch_sheet_csv():
    response = requests.get(CSV_URL)
    response.raise_for_status()
    # Ép kiểu decode utf-8 tránh lỗi font chữ tiếng Việt/Trung
    lines = response.content.decode('utf-8').splitlines()
    return list(csv.reader(lines))

def main():
    existing_lessons = load_existing_data()
    # Chuyển đổi danh sách sang cấu trúc dict để dễ đối chiếu và cập nhật đè theo Tiêu đề bài học
    lesson_dict = {l['title']: l for l in existing_lessons if 'title' in l}
    
    rows = fetch_sheet_csv()
    if len(rows) < 2:
        print("Bảng tính trống hoặc sai cấu trúc dữ liệu.")
        return

    # Duyệt từ hàng số 3 trở đi (Chỉ mục Index 2 trong mảng Python vì Hàng 1,2 là ghi chú & tiêu đề)
    for row in rows[2:]:
        # Phòng tránh lỗi thiếu số lượng cột do người dùng nhập thiếu
        if len(row) < 10:
            continue
            
        text_content = row[2].strip()      # Cột C
        translation_raw = row[3].strip()   # Cột D
        quiz_raw = row[4].strip()          # Cột E
        image_url = row[5].strip()         # Cột F
        audio_url = row[6].strip()         # Cột G
        approve_content = row[8].strip().upper()  # Cột I
        approve_update = row[9].strip().upper()   # Cột J

        # Điều kiện: Cả hai cột Duyệt nội dung và Duyệt update đều phải bằng TRUE
        if approve_content == "TRUE" and approve_update == "TRUE":
            if not text_content:
                continue

            # Tự động lấy dòng văn bản trước tiên trong ô làm Tiêu đề Menu bài học
            title = text_content.split('\n')[0].replace('\r', '').strip()
            
            # Khởi tạo giải mã chuỗi JSON từ ô dữ liệu Sheet sang Object/Array
            try:
                dictionary_obj = json.loads(translation_raw) if translation_raw else {}
            except Exception as e:
                print(f"Lỗi cú pháp JSON Dictionary tại bài '{title}': {e}")
                dictionary_obj = {}

            try:
                quiz_array = json.loads(quiz_raw) if quiz_raw else []
            except Exception as e:
                print(f"Lỗi cú pháp JSON QuizData tại bài '{title}': {e}")
                quiz_array = []

            # Đóng gói bản ghi bài học
            lesson_payload = {
                "title": title,
                "text": text_content,
                "dictionary": dictionary_obj,
                "quizData": quiz_array,
                "imageUrl": image_url,
                "audioUrl": audio_url
            }

            # Cập nhật đè hoặc thêm mới vào kho cơ sở dữ liệu
            lesson_dict[title] = lesson_payload
            print(f"Đã xử lý đồng bộ bài học: {title}")

    # Chuyển đổi ngược lại sang mảng Array để ghi vào file lưu trữ cuối cùng
    updated_lessons = list(lesson_dict.values())
    save_data(updated_lessons)
    print("Hoàn tất quy trình cập nhật cơ sở dữ liệu lessons.json!")

if __name__ == "__main__":
    main()