from Crypto.Hash import SHA256

h = SHA256.new(data=b"Hello")
hash_val = h.digest()
hash_len = len(hash_val)
print("hash_val: {}".format(hash_val))
print("hash_len: {} bytes".format(hash_len))
