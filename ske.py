from Crypto.Cipher import Salsa20

key = b"must be 16 bytes"

msg = b"test_message"
cipher = Salsa20.new(key)
ct = cipher.encrypt(msg)
nonce = cipher.nonce

cipher2 = Salsa20.new(key, nonce)
plaintext = cipher2.decrypt(ct)
if msg == plaintext:
	print("SKE Correctness: PASSED")
else:
	print("SKE Correctness: FAILED")
