import json

LOG_FILE = 'mission_computer_main.log'
OUTPUT_FILE = 'mission_computer_main.json'


def read_log_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print('[전체 로그 내용]:')
            for line in lines:
                print(line.strip())
            return lines

    except FileNotFoundError:
        print(f'파일을 찾을 수 없습니다: {filename}')
        return []

    except UnicodeDecodeError:
        print('디코딩 오류: UTF-8 형식이 아닐 수 있습니다.')
        return []

    except Exception as e:
        print(f'알 수 없는 오류 발생: {e}')
        return []


def filter_danger_logs(log_list, output_file='filter_danger_logs.log'):
    try:
        danger_keywords = ('폭발', '누출', '고온', 'oxygen', 'unstable', 'explosion')
        danger_lines = []
        for line in log_list:
            if any(keyword.lower() in line[2].lower()
                   for keyword in danger_keywords):
                danger_lines.append(line)

        if danger_lines:
            with open(output_file, 'w', encoding='utf-8') as f:
                for d_line in danger_lines:
                    f.write(', '.join(map(str, d_line)) + '\n')

            print(f'위험 로그 {len(danger_lines)}개 저장 완료: {output_file}')
        else:
            print('위험 키워드를 포함한 로그가 없습니다.')

    except Exception as e:
        print(f'오류 발생: {e}')


def parse_log_lines(lines):
    parsed = []
    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.lower().startswith('timestamp,event,message'):
            continue

        try:
            timestamp, events, message = line.split(',', 2)
            parsed.append([timestamp.strip(), events.strip(), message.strip()])

        except ValueError:
            print(f'구문 오류 (구분자 누락 또는 필드 부족): {line}')

    return parsed


def sort_logs_by_time(logs):
    return sorted(logs, key=lambda x: x[0], reverse=True)


def convert_to_dict_by_time(logs):
    result = {}
    for log in logs:
        timestamp, events, message = log

        if timestamp in result:
            print(f'중복 타임스탬프 감지: {timestamp}, 기존 메시지가 덮어쓰기 됩니다.')
        result[timestamp] = {
            'events': events,
            'message': message
        }
    return result


def save_to_json(data, filename, keyword):
    try:
        if keyword:
            search_data = {
                k: v for k, v in data.items()
                if keyword[0] in v.get('events', '')
                or keyword[0] in v.get('message', '')
            }
            print('\n[검색 결과]:')
            print(search_data)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f'JSON 파일로 저장 완료: {filename}')

    except Exception as e:
        print(f'JSON 저장 오류: {e}')


def main():
    try:
        keyword = input('Search: ').strip().split()
        if len(keyword) > 1:
            raise ValueError
        lines = read_log_file(LOG_FILE)

        if not lines:
            return

        log_list = parse_log_lines(lines)
        print('\n[리스트 객체]:')
        print(log_list)

        filter_danger_logs(log_list)

        sorted_logs = sort_logs_by_time(log_list)
        print('\n[시간 역순 정렬 리스트]:')
        print(sorted_logs)

        print('\n[보너스]:')
        for log in sorted_logs:
            print(log)

        log_dict = convert_to_dict_by_time(sorted_logs)
        print('\n[사전 객체]:')
        print(log_dict)

        save_to_json(log_dict, OUTPUT_FILE, keyword)

    except ValueError:
        print('invalid input.')


if __name__ == '__main__':
    main()
