import numpy as np
import csv


def read_all_csv_files():
    try:
        csv_files = [
            'mars_base/mars_base_main_parts-001.csv',
            'mars_base/mars_base_main_parts-002.csv',
            'mars_base/mars_base_main_parts-003.csv'
        ]

        strength_arrays = []
        common_parts = None

        for i in range(len(csv_files)):

            with open(csv_files[i], 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)

                parts = []
                strengths = []
                for row in reader:
                    part, strength = row[0], float(row[1])
                    parts.append(part)
                    strengths.append(strength)

                if common_parts is None:
                    common_parts = parts
                else:
                    if parts != common_parts:
                        raise ValueError(f'{csv_files[i]}\
                                         의 parts 열이 다른 파일과 다릅니다!')

            strength_arrays.append(np.array(strengths).reshape(-1, 1))

        merged_strengths = np.concatenate(strength_arrays, axis=1)

        return header, common_parts, merged_strengths

    except Exception:
        raise


def filter_strength(header, parts, strengths):
    outfile = 'mars_base/parts_to_work_on.csv'

    with open(outfile, 'w', newline='', encoding='utf-8') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(header)
        writer.writerows([part, strengths[i]] for i, part
                         in enumerate(parts) if strengths[i] < 50)


def read_bonus_file():
    outfile = 'mars_base/parts_to_work_on.csv'

    with open(outfile, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        data = [row for row in reader]

    return data


def main():
    try:
        header, parts, merged_strengths = read_all_csv_files()
        print(merged_strengths)

        arr1, arr2, arr3 = [merged_strengths[0:len(merged_strengths), i].
                            tolist() for i in range(merged_strengths.shape[1])]

        row_means = merged_strengths.mean(axis=1)
        print(row_means)

        filter_strength(header, parts, row_means)

        bonus_arr = read_bonus_file()
        bonus_arr = np.array(bonus_arr)
        print(bonus_arr, "\n\n")
        transpose_arr = bonus_arr.transpose()

        print(transpose_arr)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
