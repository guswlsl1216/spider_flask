import pandas as pd
import os

class SimulationService:
    current_idx = 0
    csv_data = None
    db_simulation = [] 

    @staticmethod
    def load_csv():
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, 'data', 'test_simulation_data.csv')
        
        if not os.path.exists(file_path): 
            print(f"파일을 찾을 수 없습니다 : {file_path}")
            return False

        SimulationService.csv_data = pd.read_csv(file_path)

        # 10개 초기 데이터 주입
        init_rows = SimulationService.csv_data.iloc[:10]
        SimulationService.db_simulation = [
            {'temperature_DS18B20': float(r.iloc[3]), 'humidity': float(r.iloc[4]), 
             'noise': float(r.iloc[5]), 'leak': int(r.iloc[6])} for _, r in init_rows.iterrows()
        ]
        SimulationService.current_idx = 0
        return True

    @staticmethod
    def run_next_step():
        if SimulationService.csv_data is None: SimulationService.load_csv()
        if SimulationService.current_idx >= len(SimulationService.csv_data): return None
        row = SimulationService.csv_data.iloc[SimulationService.current_idx]
        SimulationService.current_idx += 1
        new_data = {
            'temperature_DS18B20': float(row.iloc[3]), 'humidity': float(row.iloc[4]),
            'noise': float(row.iloc[5]), 'leak': int(row.iloc[6])
        }
        SimulationService.db_simulation.append(new_data)
        return new_data