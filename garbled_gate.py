############################################################
#### Description:
# Our implementation of Garbled Gate. 
# Follows Section 2.1 of https://github.com/0xPARC/0xparc-intro-book/releases/download/v1.1.1/easy.pdf .

# Author: Nikhil Vanjani
############################################################

from Crypto.Cipher import Salsa20
from Crypto.Hash import SHA256
import os

# Computes SHA256(P_left || P_right)
def hash_2_vals(P_left, P_right):
	P_concatenated = P_left + P_right
	h = SHA256.new(P_concatenated)
	hash_val = h.digest()
	return hash_val

class garbled_gate:
	# Garbled table is stored as a dict
	def __init__(self):
		self.table = {}

	# Inserts Enc(P_right, Enc(P_left, value)) at key = SHA256(P_left || P_right).
	# ASSUMPTION: value is a bytes object
	def insert(self, P_left: bytes, P_right: bytes, value: bytes):
		hash_val = hash_2_vals(P_left, P_right)

		cipher_left = Salsa20.new(P_left)
		nonce_left = cipher_left.nonce
		cipher_right = Salsa20.new(P_right)
		nonce_right = cipher_right.nonce
		ct_left = cipher_left.encrypt(value)
		ct_right = cipher_right.encrypt(ct_left)
		ct = nonce_left + nonce_right + ct_right

		self.table[hash_val] = ct

	# Looks up the value at key = SHA256(P_left || P_right) and decrypts it using keys P_left and P_right.
	# Returns a bytes object
	def lookup(self, P_left: bytes, P_right: bytes) -> bytes:
		hash_val = hash_2_vals(P_left, P_right)

		ct = self.table[hash_val]
		nonce_left = ct[:8]
		nonce_right = ct[8:16]
		ct_right = ct[16:]
		cipher_right = Salsa20.new(P_right, nonce_right)
		ct_left = cipher_right.decrypt(ct_right)
		cipher_left = Salsa20.new(P_left, nonce_left)
		value = cipher_left.decrypt(ct_left)
		return value

# Computes the garbled gate corresponding to the gate_truth_table. 
# Assumes the gate has 'left' and 'right' input wires and an 'out' output wire.
# For each of the three wires, it takes two keys as input, one each corresponding to bits 0 and 1 on that wire.
# ASSUMPTION: The values in the dict gate_truth_table are bytes object.
def garble(P_left_0, P_left_1, P_right_0, P_right_1, P_out_0, P_out_1, gate_truth_table: dict) -> garbled_gate:
	garbling = garbled_gate()
	garbling.insert(P_left_0, P_right_0, gate_truth_table[0][0])
	garbling.insert(P_left_0, P_right_1, gate_truth_table[0][1])
	garbling.insert(P_left_1, P_right_0, gate_truth_table[1][0])
	garbling.insert(P_left_1, P_right_1, gate_truth_table[1][1])
	return garbling

# Evaluates a garbled gate.
def evaluate(garbling: garbled_gate, P_left, P_right) -> bytes:
	return garbling.lookup(P_left, P_right)

val0 = 0
val1 = 1
zero_bytes = val0.to_bytes(length=2, byteorder='big')
one_bytes = val1.to_bytes(length=2, byteorder='big')

# Truth table for AND gate.
# plain = True indicates that this is a garbled gate in the output layer of the garbled circuit.
# plain = False indicates that this is an intemediate garbled gate in the garbled circuit.
# If plain = True, P_0 and P_1 are ignored.
# If plain = False, the truth table outputs are the keys P_0 / P_1 corresponding to the output bit 0 / 1.
def get_truth_table_and(plain: bool, P_0 = None, P_1 = None):
	truth_table = {}
	truth_table[0] = {}
	truth_table[1] = {}
	if plain:
		truth_table[0][0] = zero_bytes
		truth_table[0][1] = zero_bytes
		truth_table[1][0] = zero_bytes
		truth_table[1][1] = one_bytes
	else:
		truth_table[0][0] = P_0
		truth_table[0][1] = P_0
		truth_table[1][0] = P_0
		truth_table[1][1] = P_1
	return truth_table

# Truth table for OR gate.
def get_truth_table_or(plain: bool, P_0 = None, P_1 = None):
	truth_table = {}
	truth_table[0] = {}
	truth_table[1] = {}
	if plain:
		truth_table[0][0] = zero_bytes
		truth_table[0][1] = one_bytes
		truth_table[1][0] = one_bytes
		truth_table[1][1] = one_bytes
	else:
		truth_table[0][0] = P_0
		truth_table[0][1] = P_1
		truth_table[1][0] = P_1
		truth_table[1][1] = P_1
	return truth_table

# Truth table for (x >= y) gate.
def get_truth_table_geq(plain: bool, P_0 = None, P_1 = None):
	truth_table = {}
	truth_table[0] = {}
	truth_table[1] = {}
	if plain:
		truth_table[0][0] = one_bytes
		truth_table[0][1] = zero_bytes
		truth_table[1][0] = one_bytes
		truth_table[1][1] = one_bytes
	else:
		truth_table[0][0] = P_1
		truth_table[0][1] = P_0
		truth_table[1][0] = P_1
		truth_table[1][1] = P_1
	return truth_table

# Truth table for (x > y) gate.
def get_truth_table_gt(plain: bool, P_0 = None, P_1 = None):
	truth_table = {}
	truth_table[0] = {}
	truth_table[1] = {}
	if plain:
		truth_table[0][0] = zero_bytes
		truth_table[0][1] = zero_bytes
		truth_table[1][0] = one_bytes
		truth_table[1][1] = zero_bytes
	else:
		truth_table[0][0] = P_0
		truth_table[0][1] = P_0
		truth_table[1][0] = P_1
		truth_table[1][1] = P_0
	return truth_table

# Truth table for (x == y) gate.
def get_truth_table_eq(plain: bool, P_0 = None, P_1 = None):
	truth_table = {}
	truth_table[0] = {}
	truth_table[1] = {}
	if plain:
		truth_table[0][0] = one_bytes
		truth_table[0][1] = zero_bytes
		truth_table[1][0] = zero_bytes
		truth_table[1][1] = one_bytes
	else:
		truth_table[0][0] = P_1
		truth_table[0][1] = P_0
		truth_table[1][0] = P_0
		truth_table[1][1] = P_1
	return truth_table

def test_garbled_gate():
	P_left = {}
	P_left[0] = os.urandom(16)
	P_left[1] = os.urandom(16)
	P_right = {}
	P_right[0] = os.urandom(16)
	P_right[1] = os.urandom(16)
	P_out = {}
	P_out[0] = os.urandom(16)
	P_out[1] = os.urandom(16)

	truth_table_and = get_truth_table_and(True)
	truth_table_or = get_truth_table_or(True)
	truth_table_geq = get_truth_table_geq(True)
	truth_table_gt = get_truth_table_gt(True)
	truth_table_eq = get_truth_table_eq(True)
	truth_tables = (truth_table_and, truth_table_or, truth_table_geq, truth_table_gt, truth_table_eq)
	truth_tables_names = ("AND", "OR", "Greater Than Or Equal To", "Greater Than", "Equal")
	for truth_table, name in zip(truth_tables, truth_tables_names):
		garbling = garble(P_left[0], P_left[1], P_right[0], P_right[1], P_out[0], P_out[1], truth_table)
		for i in range(2):
			for j in range(2):
				val = evaluate(garbling, P_left[i], P_right[j])
				if val != truth_table[i][j]:
					print("Garbled Gate: Correctness for gate = {}: FAILED".format(name))
		print("Garbled Gate: Correctness for gate = {}: PASSED".format(name))

if __name__ == '__main__':
	test_garbled_gate()