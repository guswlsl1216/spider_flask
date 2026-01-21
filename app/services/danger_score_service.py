import logging
from sqlalchemy import desc
from app import db
from ..models.dangerScore import DangerScore
import logging

logger = logging.getLogger(__name__)

class DangerScoreService:
  @staticmethod
  def save_danger_score(machine_number: int, danger_score: float | None = None) -> DangerScore | None:
          """
          위험 점수를 danger_score 테이블에 저장한다.
          (DB 서버 연결 실패 시에도 시뮬레이션을 중단하지 않음)
          """
          if danger_score is None:
              return None

          try:
              # 원본 저장 로직 유지
              row = DangerScore(
                  machine_number=machine_number,
                  dangerScore=float(danger_score)
              )

              db.session.add(row)
              db.session.commit()
              return row
              
          except Exception as e:
              # 1. 에러 시 롤백 (세션 상태 초기화)
              db.session.rollback()
              # 2. 로그 기록 (에러 원인 파악용)
              logger.error(f"[Machine {machine_number}] 위험점수 저장 실패(DB 연결 확인 필요): {e}")
              # 3. None 반환 (호출한 곳에서 저장 실패를 인지할 수 있게 함)
              return None

  @staticmethod
  def load_danger_score(machine_number):
    """특정 설비의 최근 10개 위험 점수를 가져온다."""
    try:
      last_10_scores = DangerScore.query.filter_by(machine_number=machine_number).order_by(desc(DangerScore.id)).limit(10).all()
      last_10_scores.reverse()
      scores = [score.to_dict() for score in last_10_scores]
      
      return scores
    except Exception as e:
      logger.error(f"[Machine {machine_number}] 위험점수 로드 실패: {e}")
      return []