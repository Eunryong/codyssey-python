def caesar_cipher_decode(target_text):
    results = []

    for shift in range(26):
        decoded = ""
        
        # 각 문자를 처리
        for i, char in enumerate(target_text):
            if char.isalpha():
                # 알파벳인 경우 시프트 적용
                is_upper = char.isupper()
                char_lower = char.lower()
                
                # 자리수에 따라 다른 시프트 값 적용 (position-dependent shift)
                position_shift = (shift + i) % 26
                
                # 아스키 값 계산
                char_code = ord(char_lower) - ord('a')
                shifted_code = (char_code - position_shift) % 26
                
                decoded_char = chr(shifted_code + ord('a'))
                decoded += decoded_char.upper() if is_upper else decoded_char
            else:
                # 알파벳이 아닌 경우 그대로 유지
                decoded += char
        
        result = {
            'shift': shift,
            'decoded': decoded
        }
        results.append(result)
        
        print(f"자리수 {shift:2d}: {decoded}")

def main():
    with open('password.txt', 'r', encoding='utf-8') as f:
        secret = f.read()
    
    caesar_cipher_decode(secret)

if __name__ == '__main__':
    main()