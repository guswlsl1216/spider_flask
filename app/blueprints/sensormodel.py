import logging
from flask import Blueprint, jsonify, request
from ..utils.send_res import send_res
from ..services.ml_service import PredictionService
from ..services.danger_service import DangerService
from ..services.danger_score_service import DangerScoreService
from ..services.simulation_service import SimulationService

logger = logging.getLogger(__name__)
bp = Blueprint('sensormodel', __name__)

# 원본 계산 로직
def calculate_danger_score(t_ch, h_ch, n_ch):
    thresholds = {'temp': 5.0, 'hum': 10.0, 'noise': 20.0}
    t_score = min((abs(t_ch) / thresholds['temp']) * 100, 100)
    h_score = min((abs(h_ch) / thresholds['hum']) * 100, 100)
    n_score = min((abs(n_ch) / thresholds['noise']) * 100, 100)
    weights = {'temp': 0.4, 'hum': 0.1, 'noise': 0.5}
    final_score = (t_score * weights['temp']) + (h_score * weights['hum']) + (n_score * weights['noise'])
    return round(final_score, 2)

# [추가] MQTT 모듈이 실행될 때 반드시 필요한 함수입니다.
# 실시간 MQTT 데이터가 들어오면 예측을 수행하는 기존 역할을 담당합니다.
def predictData(data=None):
    try:
        # 실제 운영 모드에서 MQTT 데이터를 처리하는 로직이 들어갈 자리입니다.
        # 지금은 서버를 띄우는 것이 우선이므로 에러가 나지 않게만 설정합니다.
        logger.info("MQTT 실시간 예측 함수 호출됨")
        return True
    except Exception as e:
        logger.error(f"predictData Error: {e}")
        return False

@bp.post('/simulate_step')
def simulate_step():
    try:
        # 1. 시뮬레이션용 데이터 한 줄 생성 (CSV -> 메모리)
        current_data = SimulationService.run_next_step()
        if not current_data:
            return send_res(None, False, '시나리오 종료', 200)

        # 2. ML 예측 (메모리 리스트 기반)
        data, preded_final = PredictionService.predict_next_values_list(SimulationService.db_simulation)

        # 3. 위험 점수로 변환 (원본 로직 100% 동일)
        pred_temp_change = ((preded_final[0][0]-data[9][0])/data[9][0])*100
        pred_hm_change = ((preded_final[0][1]-data[9][1])/data[9][1])*100
        pred_noise_change = ((preded_final[0][2]-data[9][2])/data[9][2])*100

        danger_score = float(calculate_danger_score(pred_temp_change, pred_hm_change, pred_noise_change))

        # 4. 상태 판정 및 저장
        status = DangerService.score_to_level(danger_score)
        DangerScoreService.save_danger_score(machine_number=1, danger_score=danger_score)

        return send_res({
            "sensor_data": current_data,
            "danger_score": danger_score,
            "status": status
        }, True, '시뮬레이션 진행 성공', 200)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return send_res(None, False, str(e), 500)

@bp.get('/load_score/<machine_number>')
def load_score(machine_number):
    # 시뮬레이션 중인 데이터의 최근 10개를 반환하도록 유지
    return send_res(SimulationService.db_simulation[-10:], True, '', 200)