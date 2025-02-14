############################################################
#### Description:
# Our implementation of solving Millionaire's Problem using Garbled Circuits. 
# This implmentation contains both Alice and Bob's algorithms for simplicity.
# Follows Section 2.1 of https://github.com/0xPARC/0xparc-intro-book/releases/download/v1.1.1/easy.pdf .

# Author: Nikhil Vanjani
############################################################

from garbled_gate import *
from oblivious_transfer import bob_ot1, alice_ot1, bob_ot2
import time

# Helper function
def init_wire_keys():
	wire_keys_dict = {}
	wire_keys_dict[0] = {}
	wire_keys_dict[1] = {}
	return wire_keys_dict

# Generates Garbled circuit for x >= y, where x and y are both of length 2 bits.
# x is alice's inputs.
# y is bob's inputs.
# Suppose x = (x0, x1), y = (y0, y1).
# x >= y is equivalent to: 
# (x0 > y0) OR ((x0 = y0) AND (x1 >= y1))
def garbled_circuit_2bits():
	# We sample gate keys in reverse order as follows
	# OR 
	# 	x0 > y0
	# 	AND 
	# 		x0 = y0
	# 		x1 >= y1

	# OR gate
	P_or_left = {}
	P_or_left[0] = os.urandom(16)
	P_or_left[1] = os.urandom(16)
	P_or_right = {}
	P_or_right[0] = os.urandom(16)
	P_or_right[1] = os.urandom(16)
	P_or_out = {}
	P_or_out[0] = os.urandom(16)
	P_or_out[1] = os.urandom(16)
	truth_table_or = get_truth_table_or(plain=True)
	garbled_or = garble(P_or_left[0], P_or_left[1], P_or_right[0], P_or_right[1], P_or_out[0], P_or_out[1], truth_table_or)

	# x0 > y0
	P_gt_left = {}
	P_gt_left[0] = os.urandom(16)
	P_gt_left[1] = os.urandom(16)
	P_gt_right = {}
	P_gt_right[0] = os.urandom(16)
	P_gt_right[1] = os.urandom(16)
	truth_table_gt = get_truth_table_gt(False, P_or_left[0], P_or_left[1])
	# The output wire of this gate is the left input wire of OR gate.
	garbled_gt = garble(P_gt_left[0], P_gt_left[1], P_gt_right[0], P_gt_right[1], P_or_left[0], P_or_left[1], truth_table_gt)

	# AND gate
	P_and_left = {}
	P_and_left[0] = os.urandom(16)
	P_and_left[1] = os.urandom(16)
	P_and_right = {}
	P_and_right[0] = os.urandom(16)
	P_and_right[1] = os.urandom(16)
	truth_table_and = get_truth_table_and(False, P_or_right[0], P_or_right[1])
	# The output wire of this gate is the right input wire of OR gate.
	garbled_and = garble(P_and_left[0], P_and_left[1], P_and_right[0], P_and_right[1], P_or_right[0], P_or_right[1], truth_table_and)

	# x0 = y0
	P_eq_left = {}
	P_eq_left[0] = os.urandom(16)
	P_eq_left[1] = os.urandom(16)
	P_eq_right = {}
	P_eq_right[0] = os.urandom(16)
	P_eq_right[1] = os.urandom(16)
	truth_table_eq = get_truth_table_eq(False, P_and_left[0], P_and_left[1])
	# The output wire of this gate is the left input wire of AND gate.
	garbled_eq = garble(P_eq_left[0], P_eq_left[1], P_eq_right[0], P_eq_right[1], P_and_left[0], P_and_left[1], truth_table_eq)

	# x1 >= y1
	P_geq_left = {}
	P_geq_left[0] = os.urandom(16)
	P_geq_left[1] = os.urandom(16)
	P_geq_right = {}
	P_geq_right[0] = os.urandom(16)
	P_geq_right[1] = os.urandom(16)
	truth_table_geq = get_truth_table_geq(False, P_and_right[0], P_and_right[1])
	# The output wire of this gate is the right input wire of AND gate.
	garbled_geq = garble(P_geq_left[0], P_geq_left[1], P_geq_right[0], P_geq_right[1], P_and_right[0], P_and_right[1], truth_table_geq)

	garbled_circuit = (garbled_geq, garbled_eq, garbled_and, garbled_gt, garbled_or)

	# keys for input x
	x_keys = {}
	# keys for bit x0
	x_keys[0] = init_wire_keys()
	# x0 feeds as input to two gates: gt, eq
	# inputs for gate: gt
	x_keys[0][0][0] = P_gt_left[0]
	x_keys[0][1][0] = P_gt_left[1]
	# inputs for gate: eq
	x_keys[0][0][1] = P_eq_left[0]
	x_keys[0][1][1] = P_eq_left[1]
	# keys for bit x1
	x_keys[1] = init_wire_keys()
	# x1 feeds as input to one gates: geq
	x_keys[1][0][0] = P_geq_left[0]
	x_keys[1][1][0] = P_geq_left[1]

	# keys for input y
	y_keys = {}
	# keys for bit y0
	y_keys[0] = init_wire_keys()
	# y0 feeds as input to two gates: gt, eq
	# inputs for gate: gt
	y_keys[0][0][0] = P_gt_right[0]
	y_keys[0][1][0] = P_gt_right[1]
	# inputs for gate: eq
	y_keys[0][0][1] = P_eq_right[0]
	y_keys[0][1][1] = P_eq_right[1]
	# keys for bit y1
	y_keys[1] = init_wire_keys()
	# x1 feeds as input to one gates: geq
	y_keys[1][0][0] = P_geq_right[0]
	y_keys[1][1][0] = P_geq_right[1]

	return (garbled_circuit, x_keys, y_keys)

# Returns the keys corresponding to alice's input x
def get_alice_keys(x_keys, bit_0, bit_1) -> dict:
	alice_keys = {}
	alice_keys[0] = x_keys[0][bit_0]
	alice_keys[1] = x_keys[1][bit_1]
	return alice_keys

# Returns the keys corresponding to bob's input y. This is done via OT.
def get_bob_keys(y_keys, bit_0, bit_1) -> dict:
	bits_bool = [True, True]
	if bit_0 == 0:
		bits_bool[0] = False
	if bit_1 == 0:
		bits_bool[1] = False
	bob_keys = {}
	bob_keys[0] = {}
	bob_keys[1] = {}
	#  Get keys for all the input bits
	for i in range(2):
		yi_keys = y_keys[i]
		#  For each input bit, get the keys for each time it feeds as input into a gate
		for j in range(len(yi_keys[0])):
			bob_ot1_st = time.time()
			((b_0, b_1), bob_sk) = bob_ot1(bits_bool[i])
			bob_ot1_et = time.time()
			bob_ot1_time = bob_ot1_et - bob_ot1_st
			print("bob_ot1_time: {}".format(bob_ot1_time))

			alice_ot1_st = time.time()
			(ct_0, ct_1) = alice_ot1(b_0, b_1, yi_keys[0][j], yi_keys[1][j])
			alice_ot1_et = time.time()
			alice_ot1_time = alice_ot1_et - alice_ot1_st
			print("alice_ot1_time: {}".format(alice_ot1_time))

			bob_ot2_st = time.time()
			msg = bob_ot2(bits_bool[i], bob_sk, ct_0, ct_1)
			bob_ot2_et = time.time()
			bob_ot2_time = bob_ot2_et - bob_ot2_st
			print("bob_ot2_time: {}".format(bob_ot2_time))

			bob_keys[i][j] = msg

	return bob_keys

# Evaluate the garbled circuit sequentially from input layer to output layer.
def evaluate_garbled_circuit(garbled_circuit, alice_keys, bob_keys) -> int:
	(garbled_geq, garbled_eq, garbled_and, garbled_gt, garbled_or) = garbled_circuit

	# evaluate x2 >= y2
	val_geq = evaluate(garbled_geq, alice_keys[1][0], bob_keys[1][0])
	# evaluate x1 = y1
	val_eq = evaluate(garbled_eq, alice_keys[0][1], bob_keys[0][1])
	# evaluate AND gate
	val_and = evaluate(garbled_and, val_eq, val_geq)
	# evaluate x1 > y1
	val_gt = evaluate(garbled_gt, alice_keys[0][0], bob_keys[0][0])
	# evaluate OR gate
	val_or = evaluate(garbled_or, val_gt, val_and)
	# Return the integer value corresponding to the bytes object val_or
	return int.from_bytes(val_or, byteorder='big')

# helper function for bit bit_decomposition
def bit_decomposition(val):
	bit_string = format(val, '02b')
	bit_list = [int(b) for b in bit_string]
	return bit_list

def test_garbled_circuits_full():
	# Alice computes this and sends garbled_circuit to Bob
	garble_st = time.time()
	(garbled_circuit, x_keys, y_keys) = garbled_circuit_2bits()
	garble_et = time.time()
	garble_time = garble_et - garble_st
	print("Garbling time: {}".format(garble_time))

	alice_inputs = (0, 1, 2, 3)
	# alice_inputs = (0, 1)
	bob_inputs = (0, 1, 2, 3)
	# bob_inputs = (0, 1)
	for alice_input in alice_inputs:
		for bob_input in bob_inputs:
			alice_bits = bit_decomposition(alice_input)
			bob_bits = bit_decomposition(bob_input)

			# Alice computes her keys and sends them to Bob
			alice_keys_st = time.time()
			alice_keys = get_alice_keys(x_keys, alice_bits[0], alice_bits[1])
			alice_keys_et = time.time()
			alice_keys_time = alice_keys_et - alice_keys_st
			print("alice_keys time: {}".format(alice_keys_time))
	
			# Bob engages with Alice in OT protocol to obtain his keys
			bob_keys_st = time.time()
			bob_keys = get_bob_keys(y_keys, bob_bits[0], bob_bits[1])
			bob_keys_et = time.time()
			bob_keys_time = bob_keys_et - bob_keys_st
			print("bob_keys time: {}".format(bob_keys_time))

			# Bob evaluate the garbled circuit
			evaluate_st = time.time()
			output = evaluate_garbled_circuit(garbled_circuit, alice_keys, bob_keys)
			evaluate_et = time.time()
			evaluate_time = evaluate_et - evaluate_st
			print("Evaluate Garbled Circuit time: {}".format(evaluate_time))

			output_bool = True
			if output == 0:
				output_bool = False
			expected_output = False
			if alice_input >= bob_input:
				expected_output = True
			if output_bool != expected_output:
				print("Garbled Circuit: Correctness for {} >= {}: FAILED".format(alice_input, bob_input))
			else:
				print("Garbled Circuit: Correctness for {} >= {}: PASSED".format(alice_input, bob_input))

def test_garbled_circuits_once():
	# Alice computes this and sends garbled_circuit to Bob
	garble_st = time.time()
	(garbled_circuit, x_keys, y_keys) = garbled_circuit_2bits()
	garble_et = time.time()
	garble_time = garble_et - garble_st
	print("Garbling time: {}".format(garble_time))

	alice_input = 1
	bob_input = 2
	alice_bits = bit_decomposition(alice_input)
	bob_bits = bit_decomposition(bob_input)

	# Alice computes her keys and sends them to Bob
	alice_keys_st = time.time()
	alice_keys = get_alice_keys(x_keys, alice_bits[0], alice_bits[1])
	alice_keys_et = time.time()
	alice_keys_time = alice_keys_et - alice_keys_st
	print("alice_keys time: {}".format(alice_keys_time))

	# Bob engages with Alice in OT protocol to obtain his keys
	bob_keys_st = time.time()
	bob_keys = get_bob_keys(y_keys, bob_bits[0], bob_bits[1])
	bob_keys_et = time.time()
	bob_keys_time = bob_keys_et - bob_keys_st
	print("bob_keys time: {}".format(bob_keys_time))

	# Bob evaluate the garbled circuit
	evaluate_st = time.time()
	output = evaluate_garbled_circuit(garbled_circuit, alice_keys, bob_keys)
	evaluate_et = time.time()
	evaluate_time = evaluate_et - evaluate_st
	print("Evaluate Garbled Circuit time: {}".format(evaluate_time))

	output_bool = True
	if output == 0:
		output_bool = False
	expected_output = False
	if alice_input >= bob_input:
		expected_output = True
	if output_bool != expected_output:
		print("Garbled Circuit: Correctness for {} >= {}: FAILED".format(alice_input, bob_input))
	else:
		print("Garbled Circuit: Correctness for {} >= {}: PASSED".format(alice_input, bob_input))

if __name__ == '__main__':
	# test_garbled_circuits_full()
	test_garbled_circuits_once()