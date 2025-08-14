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

    return "".join(reversed(result))


def worker_process(
    zip_file, charset, start_idx, end_idx, file_name, result_queue, stop_event
):
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        count = 0
        last_report = time.time()

        for idx in range(start_idx, end_idx):
            if stop_event.is_set():
                return None

            if idx % 100 == 0 and stop_event.is_set():
                print(f"프로세스 {os.getpid()}: 종료 신호 받음")
                return None

            password = index_to_password(idx, charset, 6)
            count += 1

            try:
                with zip_ref.open(file_name, pwd=password.encode()) as f:
                    f.read(1)

                result_queue.put(password)
                stop_event.set()
                return password

            except Exception:
                pass

            current_time = time.time()
            if current_time - last_report >= 10:
                progress = ((idx - start_idx) / (end_idx - start_idx)) * 100
                print(
                    f"프로세스 {os.getpid()}: {progress:.1f}% | "
                    f"현재: {password} | 시도: {count:,}번"
                )
                last_report = current_time

    return None


def unlock_zip(zip_file):
    charset = string.ascii_lowercase + string.digits

    result_password = None
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        smallest_info = min(zip_ref.filelist, key=lambda x: x.file_size)

    num_processes = os.cpu_count()
    print(f"사용 프로세스 수: {num_processes}")
    print(f"테스트 파일: {smallest_info.filename}" f"({smallest_info.file_size} bytes)")

    manager = mp.Manager()
    result_queue = manager.Queue()
    stop_event = manager.Event()

    start_time = time.time()
    print(f"시작 시간: {time.ctime()}")

    total_combinations = 36**6
    chunk_size = total_combinations // num_processes

    with mp.Pool(num_processes) as pool:
        try:
            tasks = []

            for i in range(num_processes):
                start_idx = i * chunk_size
                end_idx = start_idx + (
                    chunk_size if i < num_processes - 1 else total_combinations
                )

                task = pool.apply_async(
                    worker_process,
                    (
                        zip_file,
                        charset,
                        start_idx,
                        end_idx,
                        smallest_info.filename,
                        result_queue,
                        stop_event,
                    ),
                )
                tasks.append(task)

            result_password = None
            password_found = False

            while True:
                try:
                    result = result_queue.get(timeout=1)
                    if result:
                        result_password = result
                        password_found = True
                        print(f"패스워드 발견: {result}")

                        try:
                            file_exists = os.path.exists("password.txt")
                            print(result)
                            with zipfile.ZipFile(zip_file, "r") as new_zip_ref:
                                with new_zip_ref.open(
                                    smallest_info.filename, pwd=result_password.encode()
                                ) as zf:
                                    with open(
                                        "password.txt", "w", encoding="utf-8"
                                    ) as f:
                                        tmp = zf.read().decode("utf-8")
                                        f.write(tmp)

                            if file_exists:
                                print("결과가 password.txt에 업데이트되었습니다.")
                            else:
                                print(
                                    "password.txt 파일을 새로 생성하여 결과를 저장했습니다."
                                )

                        except Exception as e:
                            print(f"파일 저장 오류: {e}")

                        stop_event.set()
                        pool.terminate()
                        pool.join()
                        break

                except Exception:
                    if password_found:
                        break

                    if all(task.ready() for task in tasks):
                        try:
                            final_result = result_queue.get_nowait()
                            if final_result:
                                result_password = final_result
                                password_found = True
                                print(f"패스워드 발견: {final_result}")

                                try:
                                    with open(
                                        "password.txt", "w", encoding="utf-8"
                                    ) as f:
                                        f.write(f"발견된 패스워드: {final_result}\n")
                                        f.write(f"발견 시간: {time.ctime()}\n")
                                    print("결과가 password.txt에 저장되었습니다.")
                                except Exception as e:
                                    print(f"파일 저장 오류: {e}")
                                break
                        except:
                            pass

                        if not password_found:
                            print("모든 조합을 시도했지만 패스워드를 찾지 못했습니다.")
                        break
                    continue

        except KeyboardInterrupt:
            print("\n사용자에 의해 중단되었습니다.")
            stop_event.set()
            pool.terminate()
            pool.join()
            return None

        except Exception as e:
            print(f"오류 발생: {e}")
            stop_event.set()
            pool.terminate()
            pool.join()
            return None

    try:
        if any(not task.ready() for task in tasks):
            print("남은 프로세스 정리 중...")
            stop_event.set()
            pool.terminate()
            pool.join()

        remaining_tasks = [task for task in tasks if not task.ready()]
        if remaining_tasks:
            print(f"{len(remaining_tasks)}개 작업이 완전히 종료되지 않았습니다.")
        else:
            print("모든 프로세스 정리 완료")

    except Exception as cleanup_error:
        print(f"정리 중 오류: {cleanup_error}")

    elapsed = time.time() - start_time
    current_time = time.ctime()
    print(f"완료 시간: {current_time}")
    print(f"총 소요 시간: {elapsed:.2f}초")

    return result_password


def main():
    unlock_file_name = "emergency_storage_key.zip"

    unlock_zip(unlock_file_name)


if __name__ == "__main__":
    main()
