def caesar_cipher_decode(target_text):
    result = {}
    eng_dict = ["love", "Mars"]
    for shift in range(26):
        decoded = []
        text = target_text.strip().split()
        for s in text:
            decoded_str = ""
            for char in s:
                if char.isalpha():
                    is_upper = s.isupper()
                    char_lower = char.lower()

                    position_shift = shift

                    char_code = ord(char_lower) - ord("a")
                    shifted_code = (char_code + position_shift) % 26

                    decoded_char = chr(shifted_code + ord("a"))
                    decoded_str += decoded_char.upper() if is_upper else decoded_char
                else:
                    decoded_str += char

            decoded.append(decoded_str)

        result[shift] = " ".join(decoded)

        print(f"{shift:2d}: {' '.join(decoded)}")

        for s in eng_dict:
            if s in decoded:
                return

    try:
        number = int(input())

        if not number:
            raise ValueError

        with open("result.txt", "w", encoding="utf-8") as f:
            print(result)
            f.write(result[number])

    except ValueError:
        print("invalid number")


def main():
    with open("password.txt", "r", encoding="utf-8") as f:
        secret = f.read()

    caesar_cipher_decode(secret)


if __name__ == "__main__":
    main()
