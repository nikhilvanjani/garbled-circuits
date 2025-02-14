Suppose Alice and Bob are millionaire's with net worth $x$ and $y$ respectively. 
They want to learn who among the two has higher net worth, but crucially they don't want to reveal their net worth to each other or to anyone else.
This is called the Millionaire's problem in cryptography and can be solved using Garbled Circuits.

This repository implements Garbled Circuits for solving Millionaire's problem.
Specifically, it implements garbled circuits for $f(x, y) := (x >= y)$, where x and y are of length 2 bits.
The implementation follows this [blog post](https://hackmd.io/@aardvark/BJYYcR1N1g) and Section 2 of 0xPARC's book on [Three Easy Peices in Programmable Cryptography](https://github.com/0xPARC/0xparc-intro-book/releases/download/v1.1.1/easy.pdf).

Instructions for running the code:
1. Download dependencies: `conda install pycryptodome`, `pip install pycryptodomex`, `pip install elgamal`.
2. Open two separate terminal windows and run `python alice.py` and `python bob.py` in them respectively.
3. In `alice.py`, on typing `garble`, it will generate the garbled circuit on Alice's behalf and send it to Bob. Next, on typing `alice_keys`, it will ask for Alice's input $x$ in range $\{0, 1, 2, 3\}$. Based on the choice, it will send to Bob the corresponding Alice's keys for evaluating the garbled circuit. At this point Bob has the garbled circuit and Alice's keys. All that remains for evaluating the garbled circuit is for Bob to obtain the keys corresponding to his inputs. We do this next by using Oblivious Transfer (OT).
4. In `bob.py`, on typing `bob_ot1`, it will ask for Bob's input $y$ in range $\{0, 1, 2, 3\}$. Based on this choice, it will generate and send Bob's OT protocol message to Alice.
5. In `alice.py`, on typing `alice_ot1`, it will generate and send Alice's OT protocol message to Bob.
6. In `bob.py`, on typing `bob_ot2`, it will compute Bob's OT output based on Alice's OT message. Next, on typing `evaluate`, it will evaluate the garbled circuit using Alice's and Bob's keys and output $f(x, y)$ to Bob.
