import random
from datetime import datetime
import logging
import os
import json
import time
from collections import defaultdict
import subprocess
import platform
from threading import Thread


class DummySensor:

    def __init__(self, log_file='mars_base_sensor.log'):
        self.log_file = log_file
        self.init_logger()
        self.env_values = {
            "mars_base_internal_temperature": random.randint(18, 30),
            "mars_base_external_temperature": random.randint(0, 21),
            "mars_base_internal_humidity": random.randint(50, 60),
            "mars_base_external_illuminance": random.randint(500, 715),
            "mars_base_internal_co2": random.uniform(0.02, 0.1),
            "mars_base_internal_oxygen": random.randint(4, 7)
        }

    def init_logger(self):
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.logger = logging.getLogger('MarsBaseSensor')
        self.logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(
            os.path.join(log_dir, self.log_file), encoding='utf-8')

        formatter = logging.Formatter('%(asctime)s | %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(file_handler)

    def set_env(self):
        self.env_values = {
            "mars_base_internal_temperature": random.randint(18, 30),
            "mars_base_external_temperature": random.randint(0, 21),
            "mars_base_internal_humidity": random.randint(50, 60),
            "mars_base_external_illuminance": random.randint(500, 715),
            "mars_base_internal_co2": random.uniform(0.02, 0.1),
            "mars_base_internal_oxygen": random.randint(4, 7)
        }

    def get_env(self):
        self.logger.info(self.env_values)
        return self.env_values


class MissionComputer:
    def __init__(self):
        self.env_values = {
            "mars_base_internal_temperature": None,
            "mars_base_external_temperature": None,
            "mars_base_internal_humidity": None,
            "mars_base_external_illuminance": None,
            "mars_base_internal_co2": None,
            "mars_base_internal_oxygen": None
        }

        self.ds = DummySensor()

        self.data_history = defaultdict(list)
        self.last_average_time = time.time()
        self.settings = self.load_settings()

    def load_settings(self):
        default_settings = {
            "system_info_items": {
                "operating_system": True,
                "os_version": True,
                "cpu_type": True,
                "cpu_cores": True,
                "memory_size_gb": True
            },
            "system_load_items": {
                "cpu_usage_percent": True,
                "memory_usage_percent": True
            }
        }

        try:
            if not os.path.exists("setting.txt"):
                return default_settings

            settings = {}
            current_section = None

            with open("setting.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if line.startswith("[") and line.endswith("]"):
                        current_section = line[1:-1]
                        if (current_section in ["system_info_items",
                                                "system_load_items"]):
                            settings[current_section] = {}

                    elif "=" in line and current_section:
                        key, value = line.split("=", 1)
                        key = key.strip()

                        value = value.strip().lower()
                        tmp = value in ["true", "1", "yes", "on"]
                        settings[current_section][key] = tmp

            # 기본값과 병합
            for key, default_value in default_settings.items():
                if key not in settings:
                    settings[key] = default_value
                elif isinstance(default_value, dict):
                    for sub_key, sub_default in default_value.items():
                        if sub_key not in settings[key]:
                            settings[key][sub_key] = sub_default

            return settings

        except Exception as e:
            print(f"설정 파일 로드 중 오류 발생: {e}")
            return default_settings

    def filter_data_by_settings(self, data, setting_key):
        if setting_key not in self.settings:
            return data

        filtered_data = {}
        for key, value in data.items():
            if self.settings[setting_key].get(key, True):
                filtered_data[key] = value

        return filtered_data

    def calculate_5min_average(self):
        if not self.data_history:
            return

        print("\n" + "="*60)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 5분 평균 환경 데이터")
        print("="*60)

        averages = {}
        for key, values in self.data_history.items():
            if values:
                if key == "mars_base_internal_co2":
                    averages[key] = round(sum(values) / len(values), 3)
                else:
                    averages[key] = round(sum(values) / len(values), 1)

        print(json.dumps(averages, indent=2, ensure_ascii=False))
        print("="*60)

        self.data_history.clear()
        self.last_average_time = time.time()

    def store_data_for_average(self, data):
        for key, value in data.items():
            if value is not None:
                self.data_history[key].append(value)

    def get_sensor_data(self):
        try:
            while True:
                sensor_data = self.ds.get_env()
                self.env_values.update(sensor_data)

                print("=" * 60)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
                      " 화성 기지 환경 데이터")
                print("=" * 60)
                print(
                    json.dumps(self.env_values, indent=2, ensure_ascii=False))
                print("=" * 60)

                self.store_data_for_average(sensor_data)

                time.sleep(5)

                current_time = time.time()
                if current_time - self.last_average_time >= 300:
                    self.calculate_5min_average()

                self.ds.set_env()

        except KeyboardInterrupt:
            print("\nSystem stoped...")
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")

    def get_mission_computer_info(self):
        try:
            memory_gb = self._get_memory_info()
            cpu_cores = self._get_cpu_cores()

            system_info = {
                "operating_system": platform.system(),
                "os_version": platform.release(),
                "cpu_type": platform.processor() or platform.machine(),
                "cpu_cores": cpu_cores,
                "memory_size_gb": memory_gb
            }

            filtered_info = self.filter_data_by_settings(
                system_info, "system_info_items")

            if filtered_info:
                print("\n" + "="*60)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
                      " 미션 컴퓨터 시스템 정보")
                print("="*60)
                print(json.dumps(filtered_info, indent=2, ensure_ascii=False))
                print("="*60)

            return filtered_info

        except Exception as e:
            print(f"시스템 정보를 가져오는 중 오류 발생: {e}")
            return None

    def _get_memory_info(self):
        try:
            system = platform.system()

            if system == "Windows":
                # Windows에서 메모리 정보 가져오기
                result = subprocess.run(
                    ['wmic', 'computersystem', 'get', 'TotalPhysicalMemory'],
                    capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if line.strip() != 'TotalPhysicalMemory':
                            memory_bytes = int(line.strip())
                            return round(memory_bytes / (1024**3), 2)

            elif system == "Linux":
                # Linux에서 /proc/meminfo 읽기
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal:'):
                            memory_kb = int(line.split()[1])
                            return round(memory_kb / (1024**2), 2)

            elif system == "Darwin":  # macOS
                result = subprocess.run(['sysctl', 'hw.memsize'],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    memory_bytes = int(result.stdout.split(':')[1].strip())
                    return round(memory_bytes / (1024**3), 2)

            return "정보 없음"

        except Exception:
            return "정보 없음"

    def _get_cpu_cores(self):
        try:
            return os.cpu_count() or "정보 없음"
        except Exception:
            return "정보 없음"

    def get_mission_computer_load(self):
        try:
            cpu_usage = self._get_cpu_usage()
            memory_usage = self._get_memory_usage()

            load_info = {
                "cpu_usage_percent": cpu_usage,
                "memory_usage_percent": memory_usage,
                "load_info": "표준 라이브러리 기반 측정"
            }

            filtered_load = self.filter_data_by_settings(load_info,
                                                         "system_load_items")

            if filtered_load:
                print("\n" + "="*60)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
                      " 미션 컴퓨터 실시간 부하")
                print("="*60)
                print(json.dumps(filtered_load, indent=2, ensure_ascii=False))
                print("="*60)

            return filtered_load

        except Exception as e:
            print(f"시스템 부하 정보를 가져오는 중 오류 발생: {e}")
            return None

    def _get_cpu_usage(self):
        try:
            system = platform.system()

            if system == "Windows":
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'loadpercentage', '/value'],
                    capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'LoadPercentage' in line and '=' in line:
                            return f"{line.split('=')[1].strip()}%"

            elif system == "Linux":
                with open('/proc/loadavg', 'r') as f:
                    load = f.read().split()[0]
                    return f"Load Average: {load}"

            elif system == "Darwin":  # macOS
                result = subprocess.run(['top', '-l', '1', '-n', '0'],
                                        capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'CPU usage' in line:
                            return line.split(':')[1].strip()

            return "측정 불가"

        except Exception:
            return "측정 불가"

    def _get_memory_usage(self):
        try:
            system = platform.system()

            if system == "Linux":
                with open('/proc/meminfo', 'r') as f:
                    meminfo = {}
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 2:
                            meminfo[parts[0].rstrip(':')] = int(parts[1])

                    total = meminfo.get('MemTotal', 0)
                    available = meminfo.get('MemAvailable', 0)
                    if total > 0:
                        used_percent = ((total - available) / total) * 100
                        return f"{used_percent:.1f}%"

            return "측정 불가"

        except Exception:
            return "측정 불가"


def main():
    try:
        ds = DummySensor()

        env_values = ds.get_env()
        print(env_values, "\n")

        ds.set_env()

        print(ds.get_env(), "\n")

        RunComputer = MissionComputer()

        th1 = Thread(target=RunComputer.get_sensor_data, daemon=True)

        th1.start()
        while True:
            th2 = Thread(target=RunComputer.get_mission_computer_info,
                         daemon=True)
            th3 = Thread(target=RunComputer.get_mission_computer_load,
                         daemon=True)

            th2.start()
            th3.start()

            th2.join()
            th3.join()
            time.sleep(5)

    except KeyboardInterrupt:
        if th1.is_alive():
            th1.join(timeout=1)
        if th2.is_alive():
            th2.join(timeout=1)
        if th3.is_alive():
            th3.join(timeout=1)
        print()


if __name__ == '__main__':
    main()
