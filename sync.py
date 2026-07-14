import os
import csv
import json
import requests

# Link xuất bản CSV của bạn
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRQhdd9aNxY8pBChZgUILO8JyC_cpl9EmIgM5kwUDQ5X3PsGFdVuAfCWn1SE2GzRLgxkBEAGwTz1Hhz/pub?gid=0&single=true&output=csv"

JSON_FILE = "lessons.json"

def save_data(data):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def fetch_sheet_csv():
    response = requests.get(CSV_URL)
    response.raise_for_status()
    lines = response.content.decode('utf-8').splitlines()
    return list(csv.reader(lines))

def main():
    # Khởi tạo mảng trống hoàn toàn để hứng dữ liệu mới, không đọc lại file json cũ nữa
    fresh_lessons_list = []
    
    try:
        rows = fetch_sheet_csv()
    except Exception as e:
        print(f"Lỗi khi kết nối và tải dữ liệu từ Google Sheet: {e}")
        return

    if len(rows) < 2:
        print("Bảng tính trống hoặc sai cấu trúc dữ liệu.")
        return

    # Duyệt từ hàng số 3 trở đi (Bỏ qua dòng tiêu đề)
    for row in rows[2:]:
        if len(row) < 10:
            continue
            
        lesson_title = row[1].strip()      # Cột B: Tên bài học
        text_content = row[2].strip()      # Cột C: Văn bản gốc
        translation_raw = row[3].strip()   # Cột D: Từ điển
        quiz_raw = row[4].strip()          # Cột E: Câu hỏi trắc nghiệm
        image_url = row[5].strip()         # Cột F: Link ảnh
        audio_url = row[6].strip()         # Cột G: Link Audio
        approve_content = row[8].strip().upper()  # Cột I: Check nội dung
        approve_update = row[9].strip().upper()   # Cột J: Check cập nhật

        # CHỈ LẤY dữ liệu khi cả 2 cột I và J đều là TRUE
        if approve_content == "TRUE" and approve_update == "TRUE":
            
            # Fallback nếu quên nhập tiêu đề ở cột B
            if not lesson_title:
                if text_content:
                    lesson_title = text_content.split('\n')[0].replace('\r', '').strip()
                else:
                    continue # Bỏ qua nếu dòng này không có cả tiêu đề lẫn nội dung

            # Biên dịch chuỗi Dictionary sang Object JSON
            try:
                dictionary_obj = json.loads(translation_raw) if translation_raw else {}
            except Exception as e:
                print(f"❌ Lỗi cú pháp JSON Dictionary tại bài '{lesson_title}': {e}")
                dictionary_obj = {}

            # Biên dịch chuỗi Quiz sang Array JSON
            try:
                quiz_array = json.loads(quiz_raw) if quiz_raw else []
            except Exception as e:
                print(f"❌ Lỗi cú pháp JSON QuizData tại bài '{lesson_title}': {e}")
                quiz_array = []

            # Đóng gói dữ liệu bài học
            lesson_payload = {
                "title": lesson_title,
                "text": text_content,
                "dictionary": dictionary_obj,
                "quizData": quiz_array,
                "imageUrl": image_url,
                "audioUrl": audio_url
            }

            fresh_lessons_list.append(lesson_payload)
            print(f"✔ Đã nạp bài học: {lesson_title}")

    # Ghi đè toàn bộ danh sách mới thu thập được vào file JSON
    save_data(fresh_lessons_list)
    print(f"\n🚀 HOÀN TẤT! Đã làm mới toàn bộ cơ sở dữ liệu. Tổng số bài học hoạt động: {len(fresh_lessons_list)}")

if __name__ == "__main__":
    main()