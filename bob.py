############################################################
#### Description:
# Our implementation of solving Millionaire's Problem using Garbled Circuits. 
# This implmentation contains Bob's algorithms.
# Follows Section 2.1 of https://github.com/0xPARC/0xparc-intro-book/releases/download/v1.1.1/easy.pdf .

# File names indicate who they belong to.
# Alice can only read files present in ./files/alice.
# Bob can only read files present in ./files/bob.
# When Alice writes files to ./files/alice, it indicates storing local state.
# When Alice writes files to ./files/bob, it indicates sending that file to Bob.
# When Bob writes files to ./files/bob, it indicates storing local state.
# When Bob writes files to ./files/alice, it indicates send ingthat file to Alice.

# Author: Nikhil Vanjani
############################################################

from garbled_gate import *
from oblivious_transfer import bob_ot1, bob_ot2
from alice_and_bob import evaluate_garbled_circuit, bit_decomposition

import os
import pickle


# Generates Bob's 1st message of OT protocol consisting of public and private keys. 
# Sends public keys to Alice.
# Stores own input and private keys locally. 
def generate_bob_ot1():
	os.makedirs("./files/alice", exist_ok=True)
	os.makedirs("./files/bob", exist_ok=True)

	# bob_input = 2
	bob_input = int(input("Enter Bob's input: "))
	bob_bits = bit_decomposition(bob_input)
	bits_bool = [True, True]
	if bob_bits[0] == 0:
		bits_bool[0] = False
	if bob_bits[1] == 0:
		bits_bool[1] = False
	with open("./files/bob/bob_input.pkl", "wb") as file:
		pickle.dump(bits_bool, file)

	bob_all_pk = {}
	bob_all_sk = {}
	count_per_bit = [2, 1]
	for i in range(2):
		bob_all_pk[i] = {}
		bob_all_sk[i] = {}
		for j in range(count_per_bit[i]):
			((b_0, b_1), bob_sk) = bob_ot1(bits_bool[i])
			bob_all_pk[i][j] = (b_0, b_1)
			bob_all_sk[i][j] = bob_sk
	with open("./files/alice/bob_all_pk.pkl", "wb") as file:
		pickle.dump(bob_all_pk, file)
	with open("./files/bob/bob_all_sk.pkl", "wb") as file:
		pickle.dump(bob_all_sk, file)

# Reads own input and private keys from local state and Alice's message of OT protocol, 
# computes and stores the OT output consisting of Bob's keys for the garbled circuit.
def generate_bob_ot2():
	os.makedirs("./files/bob", exist_ok=True)

	with open("./files/bob/alice_all_ct.pkl", "rb") as file:
		alice_all_ct = pickle.load(file)
	with open("./files/bob/bob_all_sk.pkl", "rb") as file:
		bob_all_sk = pickle.load(file)
	with open("./files/bob/bob_input.pkl", "rb") as file:
		bits_bool = pickle.load(file)

	bob_keys = {}
	count_per_bit = [2, 1]
	for i in range(2):
		bob_keys[i] = {}
		for j in range(count_per_bit[i]):
			(ct_0, ct_1) = alice_all_ct[i][j]
			msg = bob_ot2(bits_bool[i], bob_all_sk[i][j], ct_0, ct_1)
			bob_keys[i][j] = msg
	with open("./files/bob/bob_keys.pkl", "wb") as file:
		pickle.dump(bob_keys, file)

# Reads garbled circuit and alice's keys obtained from Alice, bob's keys from local state and 
# evaluates garbled circuit to compute the output for function (x >= y).
def generate_output():
	with open("./files/bob/garbled_circuit.pkl", "rb") as file:
		garbled_circuit = pickle.load(file)
	with open("./files/bob/alice_keys.pkl", "rb") as file:
		alice_keys = pickle.load(file)
	with open("./files/bob/bob_keys.pkl", "rb") as file:
		bob_keys = pickle.load(file)
	output = evaluate_garbled_circuit(garbled_circuit, alice_keys, bob_keys)
	output_bool = True
	if output == 0:
		output_bool = False
	if output_bool:
		print("Alice's value >= Bob's value")
	else:
		print("Alice's value < Bob's value")

def unknown_command():
    print("Unknown command. Try 'bob_ot1' or 'bob_ot2' or 'evaluate'.")

# Command mapping
commands = {
    "bob_ot1": generate_bob_ot1,
    "bob_ot2": generate_bob_ot2,
    "evaluate": generate_output,
}

while True:
    user_input = input("Enter a command ('exit' to quit): ").strip().lower()
    
    if user_input == "exit":
        print("Exiting program.")
        break

    # Execute the corresponding function if the command exists
    commands.get(user_input, unknown_command)()