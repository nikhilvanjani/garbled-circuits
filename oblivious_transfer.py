from elgamal.elgamal import Elgamal, PublicKey, PrivateKey, CipherText
from copy import deepcopy


ARITHMETIC_PROGRESSION_DIFF = 1

def bob_ot1(bit: bool) -> ((PublicKey, PublicKey), PrivateKey):
	pk, sk = Elgamal.newkeys(128)
	pk2 = deepcopy(pk)
	if bit:
		pk2.y -= ARITHMETIC_PROGRESSION_DIFF
		return ((pk2, pk), sk)
	else:
		pk2.y += ARITHMETIC_PROGRESSION_DIFF
		return ((pk, pk2), sk)

def alice_ot1(b_0: PublicKey, b_1: PublicKey, msg0: bytes, msg1: bytes) -> (CipherText, CipherText):
	if b_1.y != b_0.y + ARITHMETIC_PROGRESSION_DIFF:
		raise ValueError('alice_ot1: bob_keys must be an arithmetic progression with diff = {}'.format(ARITHMETIC_PROGRESSION_DIFF))

	ct_0 = Elgamal.encrypt(msg0, b_0)
	ct_1 = Elgamal.encrypt(msg1, b_1)
	return (ct_0, ct_1)

def bob_ot2(bit: bool, bob_sk: PrivateKey, alice_ct0: CipherText, alice_ct1: CipherText) -> bytes:
	if bit:
		return bytes(Elgamal.decrypt(alice_ct1, bob_sk))
	else:
		return bytes(Elgamal.decrypt(alice_ct0, bob_sk))


def test_elgamal():
	pk, sk = Elgamal.newkeys(128)
	print("pk: {}".format(pk))
	print("sk: {}".format(sk))

	msg = b"Hello"
	ct = Elgamal.encrypt(msg, pk)
	print("ct: {}".format(ct))
	plaintext = Elgamal.decrypt(ct, sk)
	if msg == plaintext:
		print("Elgamal Correctness: PASSED")
	else:
		print("Elgamal Correctness: FAILED")

def test_ot():
	bob_bits = (True, False)
	msg0 = b"message_0"
	msg1 = b"message_1"

	for bob_bit in bob_bits:
		((b_0, b_1), bob_sk) = bob_ot1(bob_bit)
		(ct_0, ct_1) = alice_ot1(b_0, b_1, msg0, msg1)
		msg = bob_ot2(bob_bit, bob_sk, ct_0, ct_1)
		if bob_bit:
			if msg != msg1:
				print("Oblivious Transfer: Correctness with bob_bit = {}: FAILED, expected message: {}, found: {}".format(bob_bit, msg1, msg))
		else:
			if msg != msg0:
				print("Oblivious Transfer: Correctness with bob_bit = {}: FAILED, expected message: {}, found: {}".format(bob_bit, msg0, msg))
		print("Oblivious Transfer: Correctness with bob_bit = {}: PASSED".format(bob_bit))

if __name__ == '__main__':
	# test_elgamal()
	test_ot()