import base64
import codecs
from Crypto.Cipher import AES

asm = "fc74aa22c4930872b0adc27a2ad8fe4e49cbe003ef09418e0dad03ba5e2132f8" # flash AWLDcrp
encrypt_these_chars = '1234567890ABCDEFGHIJKLMNOPQRTSUVWXYZabcdefghijklmnopqrstuvwxyz.,/?!@$%^&*()_+-=:;~{}<>'
secret_key = "ClickaMatchtoViewMatchStatistics,ClickaMatchtoReturn,ClickonaDaytoViewResultsforThatDay,NomatchescurrentlyonCourt,Nomatchescompletedtoday"
secret_key_encoded = "436C69636B614D61746368746F566965774D61746368537461746973746963732C436C69636B614D61746368746F52657475726E2C436C69636B6F6E61446179746F56696577526573756C7473666F72546861744461792C4E6F6D61746368657363757272656E746C796F6E436F7572742C4E6F6D617463686573636F6D706C65746564746F646179"



def decrypt_apk(data):
    k = secret_key
    t = data.decode('utf-8')
    r = r''
    key_length = len(k)
    text_length = len(t)
    modulo = len(encrypt_these_chars)
    ti = 0
    ki = 0
    for substr in t:
        if ki >= key_length:
            ki = 0
        # special character are not encoded, for example whitespace or quotes
        try:
            c = encrypt_these_chars.index(substr)
        except ValueError:
            r += substr
            ti += 1
            ki += 1
            continue

        if c >= 0:
            c = ((c - encrypt_these_chars.index(k[ki])) + modulo) % modulo
            r += encrypt_these_chars[c]
        else:
            r += t[ti]

        ti += 1
        ki += 1
    return r

def decrypt_flash(data):
    data = base64.b64decode(data)
    iv = data[:16] # IV is prepended
    key = codecs.decode(asm, 'hex_codec')
    aes = AES.new(key, AES.MODE_CBC, iv)
    # now decrypt
    dec = aes.decrypt(data)
    dec = dec[16:] # cut off IV

    # remove PKCS#7 padding
    nl = len(dec)
    val = dec[-1]
    if val > 0x16:
        return dec # padding is fucked
    l = nl - val
    return dec[:l]

