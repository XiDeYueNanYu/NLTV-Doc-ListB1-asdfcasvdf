import os
import csv
import json
import requests

# Link xuất bản CSV của bạn
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
    lines = response.content.decode('utf-8').splitlines()
    return list(csv.reader(lines))

def main():
    existing_lessons = load_existing_data()
    lesson_dict = {l['title']: l for l in existing_lessons if 'title' in l}
    
    rows = fetch_sheet_csv()
    if len(rows) < 2:
        print("Bảng tính trống hoặc sai cấu trúc dữ liệu.")
        return

    # Duyệt từ hàng số 3 trở đi
    for row in rows[2:]:
        if len(row) < 10:
            continue
            
        lesson_title = row[1].strip()      # Cột B: Tên bài học mới thêm
        text_content = row[2].strip()      # Cột C
        translation_raw = row[3].strip()   # Cột D
        quiz_raw = row[4].strip()          # Cột E
        image_url = row[5].strip()         # Cột F
        audio_url = row[6].strip()         # Cột G
        approve_content = row[8].strip().upper()  # Cột I
        approve_update = row[9].strip().upper()   # Cột J

        if approve_content == "TRUE" and approve_update == "TRUE":
            # Nếu cột B trống, tự động lấy dòng đầu Cột C làm fallback dự phòng
            if not lesson_title:
                if text_content:
                    lesson_title = text_content.split('\n')[0].replace('\r', '').strip()
                else:
                    continue

            try:
                dictionary_obj = json.loads(translation_raw) if translation_raw else {}
            except Exception as e:
                print(f"Lỗi cú pháp JSON Dictionary tại bài '{lesson_title}': {e}")
                dictionary_obj = {}

            try:
                quiz_array = json.loads(quiz_raw) if quiz_raw else []
            except Exception as e:
                print(f"Lỗi cú pháp JSON QuizData tại bài '{lesson_title}': {e}")
                quiz_array = []

            lesson_payload = {
                "title": lesson_title,
                "text": text_content,
                "dictionary": dictionary_obj,
                "quizData": quiz_array,
                "imageUrl": image_url,
                "audioUrl": audio_url
            }

            lesson_dict[lesson_title] = lesson_payload
            print(f"Đã xử lý đồng bộ bài học: {lesson_title}")

    updated_lessons = list(lesson_dict.values())
    save_data(updated_lessons)
    print("Hoàn tất quy trình cập nhật cơ sở dữ liệu lessons.json!")

if __name__ == "__main__":
    main()