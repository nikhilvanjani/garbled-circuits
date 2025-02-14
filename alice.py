############################################################
#### Description:
# Our implementation of solving Millionaire's Problem using Garbled Circuits. 
# This implmentation contains Alice's algorithms.
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
from oblivious_transfer import alice_ot1
from alice_and_bob import garbled_circuit_2bits, get_alice_keys, bit_decomposition

import pickle


# Generates the garbled circuit and the keys corresponding to inputs x and y.
# Sends garbled_circuit to Bob and stores x_keys and y_keys as local state.
def generate_garbled_circuit():
	os.makedirs("./files/alice", exist_ok=True)
	os.makedirs("./files/bob", exist_ok=True)

	(garbled_circuit, x_keys, y_keys) = garbled_circuit_2bits()
	with open("./files/bob/garbled_circuit.pkl", "wb") as file:
		pickle.dump(garbled_circuit, file)
	with open("./files/alice/x_keys.pkl", "wb") as file:
		pickle.dump(x_keys, file)
	with open("./files/alice/y_keys.pkl", "wb") as file:
		pickle.dump(y_keys, file)

# Reads x_keys from local state and sends keys correponding to alice's input to Bob.
def generate_alice_keys():
	os.makedirs("./files/bob", exist_ok=True)

	# alice_input = 1
	alice_input = int(input("Enter Alice's input: "))
	alice_bits = bit_decomposition(alice_input)

	with open("./files/alice/x_keys.pkl", "rb") as file:
		x_keys = pickle.load(file)

	alice_keys = get_alice_keys(x_keys, alice_bits[0], alice_bits[1])
	with open("./files/bob/alice_keys.pkl", "wb") as file:
		pickle.dump(alice_keys, file)

# Reads y_keys from local state, bob_all_pk obtained from Bob's 1st message of OT protocol
# and computes encryptions of y_keys and sends all the ciphertexts to Bob.
def generate_alice_ot1():
	os.makedirs("./files/bob", exist_ok=True)

	with open("./files/alice/y_keys.pkl", "rb") as file:
		y_keys = pickle.load(file)

	with open("./files/alice/bob_all_pk.pkl", "rb") as file:
		bob_all_pk = pickle.load(file)
		# print("bob_all_pk: {}".format(bob_all_pk))

	# indicates that the first input feeds into 2 gates and second input feeds into one gate.
	count_per_bit = [2, 1]
	alice_all_ct = {}
	for i in range(2):
		yi_keys = y_keys[i]
		alice_all_ct[i] = {}
		for j in range(count_per_bit[i]):
			(b_0, b_1) = bob_all_pk[i][j]
			(ct_0, ct_1) = alice_ot1(b_0, b_1, yi_keys[0][j], yi_keys[1][j])
			alice_all_ct[i][j] = (ct_0, ct_1)

	with open("./files/bob/alice_all_ct.pkl", "wb") as file:
		pickle.dump(alice_all_ct, file)

def unknown_command():
    print("Unknown command. Try 'garble' or 'alice_keys' or 'alice_ot1'.")

# Command mapping
commands = {
    "garble": generate_garbled_circuit,
    "alice_keys": generate_alice_keys,
    "alice_ot1": generate_alice_ot1,
}

while True:
    user_input = input("Enter a command ('exit' to quit): ").strip().lower()
    
    if user_input == "exit":
        print("Exiting program.")
        break

    # Execute the corresponding function if the command exists
    commands.get(user_input, unknown_command)()