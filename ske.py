from Crypto.Cipher import Salsa20

def test_ske():
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

def test_ske_twice():
	key = b"must be 16 bytes"

	msg = b"test_message"
	cipher = Salsa20.new(key)
	nonce = cipher.nonce
	print("nonce : {}".format(nonce))
	cipher2 = Salsa20.new(key)
	nonce2 = cipher2.nonce
	print("nonce2: {}".format(nonce2))

	ct = cipher.encrypt(msg)
	print("ct: {}".format(ct))
	ct2 = cipher2.encrypt(ct)
	print("ct2: {}".format(ct2))

	cipher2_d = Salsa20.new(key, nonce2)
	cipher_d = Salsa20.new(key, nonce)
	plaintex2 = cipher2_d.decrypt(ct2)
	if ct != plaintex2:
		print("SKE Correctness: FAILED")
	plaintext = cipher_d.decrypt(plaintex2)
	if msg != plaintext:
		print("SKE Correctness: FAILED")
	else:
		print("SKE Correctness: PASSED")

# test_ske()
test_ske_twice()