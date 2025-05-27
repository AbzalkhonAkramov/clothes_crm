import sys
import re
import requests
import urllib.parse

def validate_url(url):
    """URL to'gr'i formatda ekanligini va parametr borligini tekshirish"""
    if not url.startwith(("http://", "https://")):
        return False, "URL http yoki https bilan boshlanishi kerak!"
    if not re.search(r'\?.*=', url):
        return False, "URLda paramter (masalan, ?id= yoki ?username=) bo'lsihi kerak"
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200, "URL mavjud va ishlaydi."
    except requests.exceptions.RequestException:
        return False, "URLga ulanib bo'lmadi!"


def run_sqlmap(url, options="--batch --level=3 --risk=2"):
    """SQLMapni ishga tushurish va natijalarni tahlil qilish"""
    print(f"[*] {url} uchun SQLmap sinovi boshlandi...")
    # SQLMap buyruqni tayyorlash
    sqlmap_cmd = f"sqlmap -u \"{url}\" {options}"
    try:
        # SQLMapni ishga tushurish
        process = subprocess.Popen(sqlmap_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output, error = process.communicate()
        # Natijalarni tahlil qilish
        if "sqlmap identified the following injection point(s)" in output:
            print("[+] Muvaffiqiyat! SQL infeksiyasi zaifligi topildi!")
            # Injektsiya nuqtalarini chiqarish
            injection_points = re.findall(r"Parameter:.*?\n.*?Type:.*?\n.*? Title:.*?\n.*?Payload:.*?\n", output,
                                          re.DOTALL)
            for point in injection_points:
                print(f"[*] Injektsiya nuqtasi: \n{point}")
        elif "no parametr(s) found" in output:
            print("[-] Hech qanday injeksiya topilmadi.")
        else:
            print("[-] Zaiflik topilmadi yoki xato yuz berdi. ")
            print(f"[*] SQLMap xabari:\n{output[:500]}...")  # Qisqa natija
        if error:
            print(f"[-] Xato xabari:\n{error[:500]}...")
    except Exception as e:
        print(f"[-] SQLMap ishga tushurishda xato: {e}")


def main():
    if len(sys.argv) != 2:
        print("Foydalanish: python sqlmap_script.py <URL>")
        print("Misol: python script_nomi.py http://localhost/dvwa/vulnerablities/sqli/?id=")
        sys.exit(1)
    target_url = sys.argv[1]
    # URLni tekshirish
    is_valid, message = validate_url(target_url)
    if not is_valid:
        print(f"[-] Xato: {message}")
        sys.exit(1)
    print(f"[+] {message}")
    # SQL Cappuccinoni ishga tushurish
    run_sqlmap(target_url)


if __name__ == "__main__":
    main()