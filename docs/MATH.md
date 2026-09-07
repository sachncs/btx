# Mathematics

## Secp256k1 Parameters

### Field Prime

```
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
```

### Curve Order

```
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
```

### Curve Equation

```
y² = x³ + 7  (mod p)
```

Coefficient `a = 0`, coefficient `b = 7`. Koblitz curve.

### Generator Point

```
G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
     0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8)
```

## ECDSA Signature

```
k = random nonce in [1, n−1]
R = k × G
r = R.x mod n
z = hash(m)  (truncated to curve order bit length)
s = k⁻¹ × (z + r × d) mod n
```

## Extracted Values

| Variable | Source | Description |
|----------|--------|-------------|
| `r` | DER signature | First integer |
| `s` | DER signature | Second integer |
| `z` | Reconstructed sighash | Computed via `sighash_legacy`/`sighash_segwit`/`sighash_taproot` |
| `sighash_flag` | Last byte of raw signature | Determines coverage |

## Linearization

From `s ≡ k⁻¹ × (z + r × d) (mod n)`:

```
d ≡ (s × r⁻¹) × k − (z × r⁻¹)  (mod n)
```

Define `α ≡ s·r⁻¹`, `β ≡ z·r⁻¹`. Then:

```
d + β ≡ α·k  (mod n)
```

Scalar relation: `d' ≡ α·k (mod n)` where `d' = d + β`.

## Point-Space Relation

```
D' = d' × G = α × (k × G) = α × K
```

Where `D = d·G` is the public key, `K = k·G` is the nonce point:

```
D' = D + βG = αK
```

## Modular Inverse (Extended Euclidean Algorithm)

```
old_r, r = modulus, value
old_t, t = 0, 1
while r ≠ 0:
    q = old_r // r
    old_r, r = r, old_r − q·r
    old_t, t = t, old_t − q·t
if old_r ≠ 1: raise ValueError
return old_t mod modulus
```

## Field Square Root (p ≡ 3 mod 4 specialization)

```
√v = v^((p+1)/4) mod p
```
