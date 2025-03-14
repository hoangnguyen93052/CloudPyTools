import random
import hashlib
from functools import reduce

class ZeroKnowledgeProof:
    def __init__(self, secret):
        self.secret = secret
        self.nonce = None

    def commit(self):
        self.nonce = random.randint(1, 10000)
        commitment = self.hash_commitment()
        return commitment

    def hash_commitment(self):
        data = f"{self.secret}{self.nonce}".encode()
        return hashlib.sha256(data).hexdigest()

    def verify(self, commitment, response):
        verification_commitment = self.hash_commitment_with_response(response)
        return verification_commitment == commitment

    def hash_commitment_with_response(self, response):
        data = f"{self.secret}{self.nonce}{response}".encode()
        return hashlib.sha256(data).hexdigest()


class Prover:
    def __init__(self, secret):
        self.zk_proof = ZeroKnowledgeProof(secret)

    def create_commitment(self):
        commitment = self.zk_proof.commit()
        return commitment

    def generate_response(self):
        # For simplicity, the response is the secret itself in this example
        return self.zk_proof.secret


class Verifier:
    def __init__(self):
        pass

    def check_commitment(self, commitment, response, prover):
        return prover.zk_proof.verify(commitment, response)


def main():
    secret = "super_secret_password"
    prover = Prover(secret)
    verifier = Verifier()

    commitment = prover.create_commitment()
    response = prover.generate_response()

    print(f"Commitment: {commitment}")
    print(f"Response: {response}")

    is_valid = verifier.check_commitment(commitment, response, prover)
    print(f"Is the proof valid? {is_valid}")


if __name__ == "__main__":
    main()


# Additional Protocols
class SchnorrZeroKnowledgeProof:
    def __init__(self, private_key):
        self.private_key = private_key
        self.public_key = self.generate_public_key()

    def generate_public_key(self):
        # Simplistic public key generation using modular exponentiation
        g = 2  # Generating base
        p = 23  # A prime number (in reality, much larger)
        return pow(g, self.private_key, p)

    def create_commitment(self):
        self.nonce = random.randint(1, 10000)
        g = 2
        p = 23
        commitment = pow(g, self.nonce, p)
        return commitment

    def generate_response(self, commitment):
        challenge = self.challenge(commitment)
        response = (self.nonce + self.private_key * challenge) % (p - 1)
        return response

    def challenge(self, commitment):
        return random.randint(1, 10000) % 2  # Simple random challenge

    def verify_proof(self, commitment, response):
        g = 2
        p = 23
        challenge = self.challenge(commitment)
        left_side = pow(g, response, p)
        right_side = (commitment * pow(self.public_key, challenge, p)) % p
        return left_side == right_side


def schnorr_example():
    private_key = random.randint(1, 20)  # Simulate a private key
    schnorr_prover = SchnorrZeroKnowledgeProof(private_key)
    commitment = schnorr_prover.create_commitment()
    response = schnorr_prover.generate_response(commitment)

    schnorr_verifier = Verifier()
    is_valid = schnorr_verifier.check_commitment(commitment, response, schnorr_prover)
    print(f"Schnorr Commitment: {commitment}")
    print(f"Schnorr Response: {response}")
    print(f"Is Schnorr proof valid? {is_valid}")


if __name__ == "__main__":
    schnorr_example()


# Performance Testing
import time

def performance_test_ZK():
    start_time = time.time()
    secret = "performance_secret"
    prover = Prover(secret)
    
    iterations = 10000  # Number of iterations
    
    for i in range(iterations):
        commitment = prover.create_commitment()
        response = prover.generate_response()
        verifier = Verifier()
        verifier.check_commitment(commitment, response, prover)
    
    end_time = time.time()
    print(f"Performance test for {iterations} iterations took {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    performance_test_ZK()


# Advanced Features
class EnhancedZeroKnowledgeProof:
    def __init__(self, secret):
        self.secret = secret
        self.nonce = random.randint(1, 10000)
        self.commitment = self.hash_commitment()

    def hash_commitment(self):
        return hashlib.sha256(f"{self.secret}{self.nonce}".encode()).hexdigest()

    def prove(self):
        return self.secret

    def verify(self, response):
        expected_commitment = self.hash_commitment_with_response(response)
        return expected_commitment == self.commitment

    def hash_commitment_with_response(self, response):
        return hashlib.sha256(f"{self.secret}{self.nonce}{response}".encode()).hexdigest()

def enhanced_example():
    secret = "advanced_secret"
    enhanced_prover = EnhancedZeroKnowledgeProof(secret)
    
    response = enhanced_prover.prove()
    is_valid = enhanced_prover.verify(response)

    print(f"Enhanced Commitment: {enhanced_prover.commitment}")
    print(f"Response: {response}")
    print(f"Is Enhanced proof valid? {is_valid}")

if __name__ == "__main__":
    enhanced_example()