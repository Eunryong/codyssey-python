import zipfile
import string
import multiprocessing as mp
import time
import os

def index_to_password(index, charset, length):
    base = len(charset)
    result = []
    
    for _ in range(length):
        result.append(charset[index % base])
        index //= base
    
    return ''.join(reversed(result))


def worker_process(zip_file, charset, start_idx, end_idx, file_name):
    try:
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            for idx in range(start_idx, end_idx):
                password = index_to_password(idx, charset, 6)
                
                try:
                    with zip_ref.open(file_name, pwd=password.encode()) as f:
                        f.read(1)
                    
                    return password
                    
                except:
                    pass
                
                if idx % 50000 == 0:
                    progress = ((idx - start_idx) / (end_idx - start_idx)) * 100
                    print(f"프로세스 {os.getpid()}: {progress:.1f}% | 현재: {password}")
    
    except Exception as e:
        print(f"워커 프로세스 오류: {e}")
    
    return None


def unlock_zip(zip_file):
    charset = string.ascii_lowercase + string.digits
    
    result_password = None
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        smallest_info = min(zip_ref.filelist, key=lambda x: x.file_size)
    
    num_processes = os.cpu_count()
    print(f"사용 프로세스 수: {num_processes}")

    start_time = time.time()
    print(f'시작 시간: {time.ctime()}')

    total_combinations = 36 ** 6
    chunk_size = total_combinations // num_processes


    work_ranges = []
    for i in range(num_processes):
        start_idx = i * chunk_size
        end_idx = start_idx + chunk_size if i < num_processes - 1 else total_combinations
        work_ranges.append((zip_file, charset, start_idx, end_idx, smallest_info.filename))
    
    found_password = None

    with mp.Pool(num_processes) as pool:
        try:
            results = pool.starmap_async(worker_process, work_ranges)
            
            print("\n모든 프로세스 완료!")
            
            all_results = results.get()
            
            for result in all_results:
                if result:
                    found_password = result
                    print(f"\n패스워드 발견: {result}")
                    
                    try:
                        with open('setting.txt', 'w', encoding='utf-8') as f:
                            f.write(f"발견된 패스워드: {result}\n")
                            f.write(f"발견 시간: {time.ctime()}\n")
                            f.write(f"소요 시간: {time.time() - start_time:.2f}초\n")
                        print("결과가 setting.txt에 저장되었습니다.")
                    except Exception as e:
                        print(f"파일 저장 오류: {e}")
                    
                    break
            
            if not found_password:
                print("모든 조합을 시도했지만 패스워드를 찾지 못했습니다.")
        
        
        except KeyboardInterrupt:
            print("\n사용자에 의해 중단되었습니다.")
            return None
        except Exception as e:
            print(f"오류 발생: {e}")
            return None


    elapsed = time.time() - start_time
    current_time = time.ctime()
    print(f"완료 시간: {current_time}")
    print(f"총 소요 시간: {elapsed:.2f}초")
    return result_password

def main():
    unlock_file_name = 'emergency_storage_key.zip'

    unlock_zip(unlock_file_name)

if __name__ == '__main__':
    main()