# Algorithms

## Modular Inverse

Extended Euclidean algorithm (`field/modular.py`):

```
Input: a (mod p)
Output: x such that a·x ≡ 1 (mod p)

def inverse(a, p):
    if a == 0: raise ValueError
    lm, hm = 1, 0
    low, high = a % p, p
    while low > 1:
        ratio = high // low
        nm = hm - lm * ratio
        nm2 = high - low * ratio
        lm, low, hm, high = nm, nm2, lm, low
    return lm % p
```

A void-free, division-only variant. Runs in O(log min(a, p)) steps.

---

## Tonelli-Shanks Square Root (`field/sqrt.py`)

For primes p ≡ 3 (mod 4) — the secp256k1 field prime:

```
Input: a (quadratic residue mod p)
Output: sqrt(a) mod p

def sqrt(a, p):
    # p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    # p ≡ 3 (mod 4) → use exponentiation
    return pow_mod(a, (p + 1) // 4, p)
```

Simple exponentiation path since p ≡ 3 mod 4. O(log p) via modular exponentiation.

---

## Double-SHA256 (`hash256`)

```
hash256(data) = sha256(sha256(data))
```

Used in `sighash_legacy`, `sighash_segwit`, and for `tx.txid()` computation.

---

## BIP-143 SegWit v0 Sighash (`sighash/segwit.py`)

```
hashPrevouts  = hash256(prevout_n outpoint_n for each input)
hashSequence  = hash256(sequence_n for each input)
hashOutputs   = hash256(output_n for each output)

sighash = hash256(
    version (4) +
    hashPrevouts +
    hashSequence +
    outpoint (txid + vout) of current input +
    script_code (variable) +
    amount (8 bytes LE) +
    sequence (4 bytes) +
    hashOutputs +
    lock_time (4 bytes) +
    sighash_flag (4 bytes LE)
)
```

---

## BIP-341 Taproot Sighash (`sighash/taproot.py`)

```
epoch = 0x00
hash_type = sighash_flag (1 byte)
base_type = hash_type & 0x1f        # 0x00 is treated as SIGHASH_ALL
anyonecanpay = hash_type & 0x80
ext_flag = 1 if script-path spend else 0

if not anyonecanpay:                # computed over ALL inputs
    sha_prevouts      = sha256(outpoint_n for each input)    # 32
    sha_amounts       = sha256(amount_n for each input)      # 32
    sha_scriptpubkeys = sha256(scriptPubKey_n for each input) # 32
    sha_sequences     = sha256(sequence_n for each input)    # 32 (unconditional)

if base_type == SIGHASH_ALL:
    sha_outputs = sha256(txout_n for each output)            # 32

spend_type = (ext_flag << 1) | annex_present                 # 1 byte

if anyonecanpay:
    outpoint (36) || amount (8) || scriptPubKey || nSequence # this input only
else:
    input_index (4)

if annex present:
    sha_annex = sha256(compact_size(len(annex)) || annex)    # 32 (annex incl. 0x50)

if base_type == SIGHASH_SINGLE:
    sha_single_output = sha256(txout[input_index])           # 32

if ext_flag:                        # tapscript extension
    tapleaf_hash (32) + key_version (1) + codeseparator_position (4)

sighash = tagged_hash("TapSighash",
    0x00 (epoch) + hash_type (1) + version (4) + lock_time (4) +
    sha_prevouts || sha_amounts || sha_scriptpubkeys || sha_sequences +
    sha_outputs + spend_type (1) +
    outpoint || amount || scriptPubKey || sequence | input_index (4) +
    sha_annex + sha_single_output + tapleaf_hash + key_version + code_sep_pos
)
```

`sha_prevouts`/`sha_amounts`/`sha_scriptpubkeys`/`sha_sequences` commit to
**every** input (even under SIGHASH_NONE/SIGHASH_SINGLE). The valid
`hash_type` set is `{0x00, 0x01, 0x02, 0x03, 0x81, 0x82, 0x83}`.
`tapleaf_hash = tagged_hash("TapLeaf", version(1) || compact_size(len(script)) || script)`.
SIGHASH_SINGLE with no matching output is a validation failure (ValueError).

Uses BIP-340 tagged hash: `tagged_hash(tag, data) = sha256(sha256(tag) || sha256(tag) || data)`.

---

## ECDSA Verification (`signature/check.py`)

```
verify_sig(message_hash, der_sig, public_key):
    1. Parse DER to (r, s)
    2. Reject if r or s outside [1, n-1]
    3. z = bytes_to_int(message_hash)
    4. u1 = (z * s⁻¹) mod n
    5. u2 = (r * s⁻¹) mod n
    6. R = u1·G + u2·Q
    7. Valid if R.x ≡ r (mod n)
```

---

## Nonce Reuse Attack (`signature/attack.py`)

Given two signatures with same k (identical r):

```
Given: s₁ = k⁻¹(z₁ + r·d)  (mod n)
       s₂ = k⁻¹(z₂ + r·d)  (mod n)

Subtract: s₁ − s₂ = k⁻¹(z₁ − z₂)  (mod n)
     ⇒   k = (z₁ − z₂) · (s₁ − s₂)⁻¹  (mod n)
     ⇒   d = (s₁·k − z₁) · r⁻¹  (mod n)
```

Also recovers k via linear coefficient identity.

---

## Related Nonce Recovery (`signature/attack.py`)

When `k₂ = k₁ + δ` and δ is known:

```
Given: k₂ = k₁ + δ
       s₁ = k₁⁻¹(z₁ + r₁·d)
       s₂ = (k₁ + δ)⁻¹(z₂ + r₂·d)

Substitute and solve for k₁:
       k₁ = (z₁ − s₁·r₁·r₂⁻¹·z₂) · (s₁·r₁·r₂⁻¹ + s₂ − s₁·r₁·r₂⁻¹·δ)⁻¹
Then:  d = (s₁·k₁ − z₁) · r₁⁻¹
       k₂ = k₁ + δ
```

---

## Deterministic ECDSA Nonce (RFC 6979) (`signature/signer.py`)

Uses HMAC-SHA256 to generate k deterministically:

```
def generate_k(q, x, hash):
    # q = curve order, x = private key, hash = message hash
    V = 0x01 * 16
    K = 0x00 * 16
    x_hash = int_to_bytes(x, 32) + hash
    K = hmac_sha256(K, V + 0x00 + x_hash)
    V = hmac_sha256(K, V)
    K = hmac_sha256(K, V + 0x01 + x_hash)
    V = hmac_sha256(K, V)

    while True:
        V = hmac_sha256(K, V)
        k = bytes_to_int(V)
        if 1 <= k < q:
            return k
        K = hmac_sha256(K, V + 0x00)
        V = hmac_sha256(K, V)
```

Implements the "test" candidate generation (Section 3.2). This is HMAC-based and runs in expected O(1) rounds.

---

## Linear Coefficient Derivation (`signature/linearization/coefficients.py`)

```
Input: (r, s, z) from an ECDSA signature
Output: (α, β) such that d ≡ α·k − β (mod n)

α = s · r⁻¹  (mod n)
β = z · r⁻¹  (mod n)

Derived from:
    s ≡ k⁻¹(z + rd)
    s·k ≡ z + r·d
    d ≡ r⁻¹·s·k − r⁻¹·z
    d ≡ α·k − β
```
