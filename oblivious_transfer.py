############################################################
#### Description:
# Our implementation of Oblivious Transfer. 
# Follows Section 2.2 of https://github.com/0xPARC/0xparc-intro-book/releases/download/v1.1.1/easy.pdf .

# Author: Nikhil Vanjani
############################################################

from elgamal.elgamal import Elgamal, PublicKey, PrivateKey, CipherText
from copy import deepcopy


# This is a toy OT protocol and may not be fully secure.
# For OT protocol's security, it is essential that Bob does not know the secret key sk2 corresponding to the fake public key pk2.
# In Elgamal encryption, pk = g^{sk}. 
# To ensure full security, we need that ARITHMETIC_PROGRESSION_DIFF = random value, for example SHA(1). 
# This helps formally argue that pk2 is a random value and thus finding sk2 is no easier than breaking the discrete log assumption.
ARITHMETIC_PROGRESSION_DIFF = 1

# Creates a valid (pk, sk) pair. Also creates a fake public key pk2.
# Returns ((b_0, b_1), sk), where (b_bit, sk) are the valid pair and (b_0, b_1) follow an arithmetic progression
def bob_ot1(bit: bool) -> ((PublicKey, PublicKey), PrivateKey):
	pk, sk = Elgamal.newkeys(128)
	pk2 = deepcopy(pk)
	if bit:
		pk2.y -= ARITHMETIC_PROGRESSION_DIFF
		return ((pk2, pk), sk)
	else:
		pk2.y += ARITHMETIC_PROGRESSION_DIFF
		return ((pk, pk2), sk)

# Alice encrypts msg0 under public key b_0 and msg1 under b_1.
def alice_ot1(b_0: PublicKey, b_1: PublicKey, msg0: bytes, msg1: bytes) -> (CipherText, CipherText):
	if b_1.y != b_0.y + ARITHMETIC_PROGRESSION_DIFF:
		raise ValueError('alice_ot1: bob_keys must be an arithmetic progression with diff = {}'.format(ARITHMETIC_PROGRESSION_DIFF))

	ct_0 = Elgamal.encrypt(msg0, b_0)
	ct_1 = Elgamal.encrypt(msg1, b_1)
	return (ct_0, ct_1)

# Bob uses the secret key it knows to decrypt the corresponding ciphertext.
def bob_ot2(bit: bool, bob_sk: PrivateKey, alice_ct0: CipherText, alice_ct1: CipherText) -> bytes:
	if bit:
		return bytes(Elgamal.decrypt(alice_ct1, bob_sk))
	else:
		return bytes(Elgamal.decrypt(alice_ct0, bob_sk))


def test_elgamal():
	pk, sk = Elgamal.newkeys(128)
	msg = b"Hello"
	ct = Elgamal.encrypt(msg, pk)
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