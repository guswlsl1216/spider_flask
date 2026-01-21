import numpy as np
from ..extensions import model, scaler_X, scaler_y

class PredictionService:
    DATA_COUNT = 10

    @staticmethod
    def predict_next_values_list(data_list):
        # 1. DB 쿼리 대신 리스트에서 최근 10개 추출 (형식은 원본과 동일)
        last_10 = data_list[-PredictionService.DATA_COUNT:]
        data = [[log['temperature_DS18B20'], log['humidity'], log['noise']] for log in last_10]
        
        if len(data) < PredictionService.DATA_COUNT:
            return None, None

        # 2. 아래는 원본 로직과 100% 동일 (변수명, 수식 유지)
        input_sequence = []
        row = [data[0][0], data[0][1], data[0][2], 0.0, 0.0, 0.0]
        input_sequence.append(row)
        
        for i in range(1, PredictionService.DATA_COUNT):
            curr_data = data[i]
            prev_data = data[i-1]
            # 원본 수식 그대로 사용
            temp_change_1m = ((curr_data[0]-prev_data[0])/prev_data[0])*100
            hm_change_1m = ((curr_data[1]-prev_data[1])/prev_data[1])*100
            noise_change_1m = ((curr_data[2]-prev_data[2])/prev_data[2])*100
            
            row = [curr_data[0], curr_data[1], curr_data[2], temp_change_1m, hm_change_1m, noise_change_1m]
            input_sequence.append(row)
            
        scaled_data = scaler_X.transform(input_sequence)
        final_data = np.array([scaled_data])
        preded = model.predict(final_data)
        preded_final = scaler_y.inverse_transform(preded)

        return data, preded_final