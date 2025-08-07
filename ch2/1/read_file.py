import csv
import pickle


def read_csv(path):
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        data = [row for row in reader]

    print('전체 목록:')
    for row in data:
        print(row)

    return header, data


def save_csv(path, header, data):
    with open(path, 'w', newline='', encoding='utf-8') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(header)
        writer.writerows(data)


def save_bin(path, header, data):
    with open(path, 'wb') as f:
        pickle.dump((header, data), f)


def open_bin(path):
    with open(path, 'rb') as f:
        loaded_header, loaded_data = pickle.load(f)

    return loaded_header, loaded_data


def main():
    try:
        input_file = 'mars_base/Mars_Base_Inventory_List.csv'
        output_file = 'mars_base/Mars_Base_Inventory_danger.csv'
        bin_file = 'mars_base/Mars_Base_Inventory_List.bin'

        header, data = read_csv(input_file)

        flammability_index_col = header.index('Flammability')
        data.sort(key=lambda row:
                  float(row[flammability_index_col]), reverse=True)

        print('\n내림차순 정렬:')
        for row in data:
            print(row)

        danger_items = [row for row in data
                        if float(row[flammability_index_col]) >= 0.7]

        print('\n인화성 지수 0.7 이상 위험 항목:')
        for row in danger_items:
            print(row)

        save_csv(output_file, header, danger_items)

        save_bin(bin_file, header, data)

        bin_header, bin_data = open_bin(bin_file)

        print('\nbin 파일 데이터:')
        print(bin_header)
        for row in bin_data:
            print(row)

    except FileNotFoundError as e:
        print(e)

    except ValueError:
        print('invalid file')


if __name__ == '__main__':
    main()
