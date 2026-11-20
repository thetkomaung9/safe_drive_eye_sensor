"""저장된 졸음 기록 보기:  python report.py"""
from database import EventDB

db = EventDB()
print("=== 세션별 요약 ===")
print(f"{'ID':<4}{'시작':<22}{'종료':<22}{'졸음 횟수':<10}{'최대 지속(초)'}")
for sid, start, end, count, longest in db.session_summary():
    print(f"{sid:<4}{start or '-':<22}{end or '-':<22}{count:<10}{longest}")
print("\n=== 최근 졸음 기록 ===")
for sid, t, typ, sec in db.recent_events():
    print(f"세션 {sid} | {t} | {typ} | {sec}초")
db.close()
