"""저장된 졸음 기록 보기:  python report.py"""
from database import EventDB

db = EventDB()
total, warnings, pull_overs, longest = db.alert_summary()
print("=== 졸음 경고 요약 ===")
print(f"전체 졸음 이벤트: {total}")
print(f"WARNING 이벤트: {warnings}")
print(f"PULL_OVER (안전 정차 필요) 이벤트: {pull_overs}")
print(f"가장 긴 눈 감김 시간: {longest}초")

print("=== 세션별 요약 ===")
print(f"{'ID':<4}{'시작':<22}{'종료':<22}{'졸음 횟수':<10}{'최대 지속(초)'}")
for sid, start, end, count, longest in db.session_summary():
    print(f"{sid:<4}{start or '-':<22}{end or '-':<22}{count:<10}{longest}")
print("\n=== 최근 졸음 기록 ===")
for sid, t, typ, sec, level in db.recent_events(include_alert_level=True):
    print(f"세션 {sid} | {t} | {typ} | {level or '-'} | {sec}초")
db.close()
