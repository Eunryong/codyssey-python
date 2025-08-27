import pyaudio
import wave
import threading
from datetime import datetime, timedelta
from pathlib import Path
import speech_recognition as sr
import csv
import contextlib


class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.recording_thread = None
        self.records_dir = Path('records')
        self.sample_rate = 44100
        self.channels = 1
        self.chunk = 1024
        self.format = pyaudio.paInt16

        self.records_dir.mkdir(exist_ok=True)

    def list_microphones(self):
        print('\n사용 가능한 마이크 목록:')
        print('-' * 50)
        info = self.audio.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')

        mic_devices = []
        for i in range(num_devices):
            device_info = self.audio.\
                get_device_info_by_host_api_device_index(0, i)
            if device_info.get('maxInputChannels') > 0:
                mic_devices.append((i, device_info.get('name')))
                print(f'[{i}] {device_info.get('name')}')

        if not mic_devices:
            print('사용 가능한 마이크를 찾을 수 없습니다.')
            return None

        return mic_devices

    def select_microphone(self):
        mics = self.list_microphones()
        if not mics:
            return None

        while True:
            try:
                choice = input('\n사용할 마이크 번호를 선택하세요 (기본값: 0): ').strip()
                if choice == '':
                    return 0
                device_index = int(choice)
                if any(mic[0] == device_index for mic in mics):
                    return device_index
                else:
                    print('올바른 마이크 번호를 입력하세요.')
            except ValueError:
                print('숫자를 입력하세요.')

    def start_recording(self, device_index=None):
        if self.is_recording:
            print('이미 녹음 중입니다.')
            return

        try:
            self.frames = []
            self.is_recording = True

            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk
            )

            print('\n녹음을 시작합니다... (Enter 키를 누르면 중지)')

            self.recording_thread = threading.Thread(target=self._record)
            self.recording_thread.start()

        except Exception as e:
            print(f'녹음 시작 실패: {e}')
            self.is_recording = False

    def _record(self):
        while self.is_recording:
            try:
                data = self.stream.read(
                    self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f'녹음 중 오류: {e}')
                break

    def stop_recording(self):
        if not self.is_recording:
            print('녹음 중이 아닙니다.')
            return None

        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join()

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        if self.frames:
            filename = self._save_recording()
            print(f'녹음이 저장되었습니다: {filename}')
            return filename
        else:
            print('녹음된 데이터가 없습니다.')
            return None

    def _save_recording(self):
        now = datetime.now()
        filename = now.strftime('%Y%m%d-%H%M%S.wav')
        filepath = self.records_dir / filename

        wf = wave.open(str(filepath), 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.audio.get_sample_size(self.format))
        wf.setframerate(self.sample_rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        return filename

    def list_recordings(self, start_date=None, end_date=None):
        print('\n녹음 파일 목록:')
        print('-' * 70)

        recordings = []
        for file in sorted(self.records_dir.glob('*.wav')):
            try:
                date_str = file.stem
                file_date = datetime.strptime(date_str, '%Y%m%d-%H%M%S')

                if start_date and file_date < start_date:
                    continue
                if end_date and file_date > end_date:
                    continue

                file_size = file.stat().st_size / (1024 * 1024)
                recordings.append((file.name, file_date, file_size))

            except ValueError:
                continue

        if recordings:
            print(f'{'파일명':<30} {'녹음 시간':<25} {'크기 (MB)':<10}')
            print('-' * 70)
            for name, date, size in recordings:
                date_str = date.strftime('%Y-%m-%d %H:%M:%S')
                print(f'{name:<30} {date_str:<25} {size:>8.2f}')
        else:
            if start_date or end_date:
                print('지정된 날짜 범위에 녹음 파일이 없습니다.')
            else:
                print('녹음 파일이 없습니다.')

        return recordings

    def filter_recordings_by_date(self):
        print('\n날짜 범위로 녹음 파일 필터링')
        print('-' * 50)

        try:
            start_input = input('시작 날짜 (YYYY-MM-DD, Enter로 건너뛰기): ').strip()
            start_date = None
            if start_input:
                start_date = datetime.strptime(start_input, '%Y-%m-%d')

            end_input = input('종료 날짜 (YYYY-MM-DD, Enter로 건너뛰기): ').strip()
            end_date = None
            if end_input:
                end_date = datetime.strptime(end_input, '%Y-%m-%d') + \
                    timedelta(days=1)

            self.list_recordings(start_date, end_date)

        except ValueError:
            print('올바른 날짜 형식이 아닙니다. (YYYY-MM-DD)')

    def get_audio_duration(self, filepath):
        '''정확한 오디오 파일 길이 구하기'''
        try:
            with contextlib.closing(wave.open(str(filepath), 'r')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
                return duration
        except Exception as e:
            print(f'오디오 길이 확인 오류: {e}')
            return None

    def transcribe_audio(self, audio_file):
        print(f"\n'{audio_file}' 파일을 텍스트로 변환 중...")

        recognizer = sr.Recognizer()
        filepath = self.records_dir / audio_file

        if not filepath.exists():
            print(f'파일을 찾을 수 없습니다: {filepath}')
            return None

        total_duration = self.get_audio_duration(filepath)
        if total_duration is None:
            return None

        print(f'전체 길이: {total_duration:.2f}초')

        segments = []
        chunk_duration = 2  # 2초 단위로 변경
        current_time = 0.0

        while current_time < total_duration:
            remaining = total_duration - current_time
            actual_duration = min(chunk_duration, remaining)

            # 무한루프 방지
            if actual_duration <= 0:
                print(f'❌ actual_duration이 {actual_duration}이므로 중단합니다.')
                break

                print(f'🎤 처리 중: {current_time:.1f}s ~ '
                      f'{current_time + actual_duration:.1f}s')

            try:
                with sr.AudioFile(str(filepath)) as source:
                    audio_data = recognizer.record(
                        source,
                        offset=current_time,
                        duration=actual_duration
                    )

                try:
                    text = recognizer.recognize_google(
                        audio_data, language='ko-KR')
                    segments.append((current_time, text))
                    print(f'  ✅ [{current_time:.1f}s-'
                          f'{current_time + actual_duration:.1f}s] {text}')

                except sr.UnknownValueError:
                    print(f'  ❌ [{current_time:.1f}s-'
                          f'{current_time + actual_duration:.1f}s] (인식 불가)')
                except sr.RequestError as e:
                    print(f'  ⚠️  [{current_time:.1f}s-'
                          f'{current_time + actual_duration:.1f}s] '
                          f'API 오류: {e}')

            except Exception as e:
                print(f'  ❌ 오디오 처리 오류: {e}')

            current_time += actual_duration

        if segments:
            csv_filename = self._save_transcription(audio_file, segments)
            print(f'\n📊 총 {len(segments)}개 구간 처리 완료')
            print(f"텍스트가 '{csv_filename}'에 저장되었습니다.")
            return csv_filename
        else:
            print('텍스트를 인식할 수 없습니다.')
            return None

    def _save_transcription(self, audio_file, segments):
        csv_filename = audio_file.replace('.wav', '.csv')
        csv_filepath = self.records_dir / csv_filename

        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['시간(초)', '인식된 텍스트'])

            for time_sec, text in segments:
                writer.writerow([f'{time_sec:.1f}', text])

        return csv_filename

    def transcribe_all_recordings(self):
        print('\n모든 녹음 파일을 텍스트로 변환합니다...')
        wav_files = list(self.records_dir.glob('*.wav'))

        if not wav_files:
            print('녹음 파일이 없습니다.')
            return

        for wav_file in wav_files:
            self.transcribe_audio(wav_file.name)

    def search_in_transcriptions(self, keyword):
        print(f"\n'{keyword}' 키워드를 검색 중...")
        print('-' * 70)

        csv_files = list(self.records_dir.glob('*.csv'))

        if not csv_files:
            print('CSV 파일이 없습니다. 먼저 음성을 텍스트로 변환하세요.')
            return

        results_found = False
        for csv_file in csv_files:
            found_in_file = False

            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader)

                    for row in reader:
                        if len(row) >= 2:
                            time_str, text = row[0], row[1]
                            if keyword.lower() in text.lower():
                                if not found_in_file:
                                    print(f'\n파일: {csv_file.name}')
                                    print('-' * 40)
                                    found_in_file = True
                                print(f'  [{time_str}초] {text}')
                                results_found = True
            except Exception as e:
                print(f'파일 읽기 오류 ({csv_file.name}): {e}')

        if not results_found:
            print(f"'{keyword}' 키워드를 찾을 수 없습니다.")

    def list_csv_files(self):
        print('\n변환된 텍스트 파일 목록:')
        print('-' * 70)

        csv_files = list(self.records_dir.glob('*.csv'))

        if csv_files:
            print(f'{'파일명':<40} {'생성 시간':<25}')
            print('-' * 70)
            for csv_file in sorted(csv_files):
                stat = csv_file.stat()
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                print(f'{csv_file.name:<40} '
                      f'{mod_time.strftime('%Y-%m-%d %H:%M:%S'):<25}')
        else:
            print('CSV 파일이 없습니다.')

    def close(self):
        if self.stream:
            self.stream.close()
        self.audio.terminate()


def main():
    recorder = AudioRecorder()

    try:
        while True:
            print('\n' + '=' * 50)
            print('음성 녹음 및 텍스트 변환 시스템')
            print('=' * 50)
            print('[ 녹음 기능 ]')
            print('1. 마이크 목록 보기')
            print('2. 녹음 시작')
            print('3. 녹음 파일 목록 보기')
            print('4. 날짜 범위로 녹음 파일 필터링')
            print('\n[ 텍스트 변환 기능 ]')
            print('5. 특정 녹음 파일을 텍스트로 변환')
            print('6. 모든 녹음 파일을 텍스트로 변환')
            print('7. 변환된 텍스트 파일 목록 보기')
            print('8. 텍스트에서 키워드 검색')
            print('\n9. 종료')
            print('-' * 50)

            choice = input('선택하세요 (1-9): ').strip()

            if choice == '1':
                recorder.list_microphones()

            elif choice == '2':
                device_index = recorder.select_microphone()
                if device_index is not None:
                    recorder.start_recording(device_index)
                    input()
                    recorder.stop_recording()

            elif choice == '3':
                recorder.list_recordings()

            elif choice == '4':
                recorder.filter_recordings_by_date()

            elif choice == '5':
                recordings = recorder.list_recordings()
                if recordings:
                    filename = input('\n변환할 음성 파일명을 입력하세요: ').strip()
                    if filename:
                        recorder.transcribe_audio(filename)

            elif choice == '6':
                recorder.transcribe_all_recordings()

            elif choice == '7':
                recorder.list_csv_files()

            elif choice == '8':
                keyword = input('\n검색할 키워드를 입력하세요: ').strip()
                if keyword:
                    recorder.search_in_transcriptions(keyword)

            elif choice == '9':
                print('\n프로그램을 종료합니다.')
                break

            else:
                print('올바른 선택지를 입력하세요.')

    except KeyboardInterrupt:
        print('\n\n프로그램을 종료합니다.')
    finally:
        recorder.close()


if __name__ == '__main__':
    main()
