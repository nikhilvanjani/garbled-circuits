from garbled_gate import *
from oblivious_transfer import bob_ot1, alice_ot1, bob_ot2
import time

def init_wire_keys():
	wire_keys_dict = {}
	wire_keys_dict[0] = {}
	wire_keys_dict[1] = {}
	return wire_keys_dict

def garbled_table_2bits():
	# x is alice's inputs.
	# y is bob's inputs.
	# Suppose x = (x0, x1), y = (y0, y1).
	# x >= y is equivalent to: 
	# (x0 > y0) OR ((x0 = y0) AND (x1 >= y1))
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
	garbled_gt = garble(P_gt_left[0], P_gt_left[1], P_gt_right[0], P_gt_right[1], P_or_left[0], P_or_left[1], truth_table_gt)

	# AND gate
	P_and_left = {}
	P_and_left[0] = os.urandom(16)
	P_and_left[1] = os.urandom(16)
	P_and_right = {}
	P_and_right[0] = os.urandom(16)
	P_and_right[1] = os.urandom(16)
	truth_table_and = get_truth_table_and(False, P_or_right[0], P_or_right[1])
	garbled_and = garble(P_and_left[0], P_and_left[1], P_and_right[0], P_and_right[1], P_or_right[0], P_or_right[1], truth_table_and)

	# x0 = y0
	P_eq_left = {}
	P_eq_left[0] = os.urandom(16)
	P_eq_left[1] = os.urandom(16)
	P_eq_right = {}
	P_eq_right[0] = os.urandom(16)
	P_eq_right[1] = os.urandom(16)
	truth_table_eq = get_truth_table_eq(False, P_and_left[0], P_and_left[1])
	garbled_eq = garble(P_eq_left[0], P_eq_left[1], P_eq_right[0], P_eq_right[1], P_and_left[0], P_and_left[1], truth_table_eq)

	# x1 >= y1
	P_geq_left = {}
	P_geq_left[0] = os.urandom(16)
	P_geq_left[1] = os.urandom(16)
	P_geq_right = {}
	P_geq_right[0] = os.urandom(16)
	P_geq_right[1] = os.urandom(16)
	truth_table_geq = get_truth_table_geq(False, P_and_right[0], P_and_right[1])
	garbled_geq = garble(P_geq_left[0], P_geq_left[1], P_geq_right[0], P_geq_right[1], P_and_right[0], P_and_right[1], truth_table_geq)

	garbled_circuit = (garbled_geq, garbled_eq, garbled_and, garbled_gt, garbled_or)

	x_keys = {}
	y_keys = {}
	x_keys[0] = init_wire_keys()
	y_keys[0] = init_wire_keys()
	x_keys[1] = init_wire_keys()
	y_keys[1] = init_wire_keys()

	x_keys[0][0][0] = P_gt_left[0]
	x_keys[0][1][0] = P_gt_left[1]

	x_keys[0][0][1] = P_eq_left[0]
	x_keys[0][1][1] = P_eq_left[1]

	x_keys[1][0][0] = P_geq_left[0]
	x_keys[1][1][0] = P_geq_left[1]

	y_keys[0][0][0] = P_gt_right[0]
	y_keys[0][1][0] = P_gt_right[1]

	y_keys[0][0][1] = P_eq_right[0]
	y_keys[0][1][1] = P_eq_right[1]

	y_keys[1][0][0] = P_geq_right[0]
	y_keys[1][1][0] = P_geq_right[1]

	return (garbled_circuit, x_keys, y_keys)

def get_alice_keys(x_keys, bit_0, bit_1):
	# print("get_alice_keys: x_keys: {}".format(x_keys))
	alice_keys = {}
	alice_keys[0] = x_keys[0][bit_0]
	alice_keys[1] = x_keys[1][bit_1]
	return alice_keys

def get_bob_keys(y_keys, bit_0, bit_1):
	# print("get_bob_keys: y_keys: {}".format(y_keys))
	# print("get_bob_keys: bit_0: {}".format(bit_0))
	# print("get_bob_keys: bit_1: {}".format(bit_1))
	bits_bool = [True, True]
	if bit_0 == 0:
		bits_bool[0] = False
	if bit_1 == 0:
		bits_bool[1] = False
	bob_keys = {}
	bob_keys[0] = {}
	bob_keys[1] = {}
	for i in range(2):
		yi_keys = y_keys[i]
		# print("get_bob_keys: y{}_keys: {}".format(i, yi_keys))
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
	# print("get_bob_keys: bob_keys: {}".format(bob_keys))
	return bob_keys

def evaluate_garbled_circuit(garbled_circuit, alice_keys, bob_keys):
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
	return int.from_bytes(val_or, byteorder='big')

def bit_decomposition(val):
	bit_string = format(val, '02b')
	bit_list = [int(b) for b in bit_string]
	return bit_list

def test_garbled_circuits():
	# Alice computes this and sends garbled_circuit to Bob
	garble_st = time.time()
	(garbled_circuit, x_keys, y_keys) = garbled_table_2bits()
	garble_et = time.time()
	garble_time = garble_et - garble_st
	print("Garbling time: {}".format(garble_time))

	# alice_inputs = (0, 1, 2, 3)
	alice_inputs = (0, 1)
	# bob_inputs = (0, 1, 2, 3)
	bob_inputs = (0, 1)
	for alice_input in alice_inputs:
		for bob_input in bob_inputs:
			alice_bits = bit_decomposition(alice_input)
			# print("alice_bits[0] = {}".format(alice_bits[0]))
			# print("alice_bits[1] = {}".format(alice_bits[1]))
			bob_bits = bit_decomposition(bob_input)
			# print("bob_bits[0] = {}".format(bob_bits[0]))
			# print("bob_bits[1] = {}".format(bob_bits[1]))

			# Alice computes her keys and sends them to Bob
			alice_keys_st = time.time()
			alice_keys = get_alice_keys(x_keys, alice_bits[0], alice_bits[1])
			alice_keys_et = time.time()
			alice_keys_time = alice_keys_et - alice_keys_st
			print("alice_keys time: {}".format(alice_keys_time))
			# print("alice_keys: {}".format(alice_keys))
	
			# Bob engages with Alice in OT protocol to obtain his keys
			bob_keys_st = time.time()
			bob_keys = get_bob_keys(y_keys, bob_bits[0], bob_bits[1])
			bob_keys_et = time.time()
			bob_keys_time = bob_keys_et - bob_keys_st
			print("bob_keys time: {}".format(bob_keys_time))
			# print("bob_keys: {}".format(bob_keys))

			# Bob evaluate the garbled circuit
			evaluate_st = time.time()
			output = evaluate_garbled_circuit(garbled_circuit, alice_keys, bob_keys)
			evaluate_et = time.time()
			evaluate_time = evaluate_et - evaluate_st
			print("Evaluate Garbled Circuit time: {}".format(evaluate_time))
			# print("output: {}".format(output))

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

test_garbled_circuits()