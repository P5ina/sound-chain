import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional

from config import INITIAL_REWARD, HALVING_INTERVAL, MIN_FEE, INITIAL_BALANCE


@dataclass
class Transaction:
    tx_id: str
    from_address: str
    to_address: str
    amount: float
    fee: float
    timestamp: float

    def to_dict(self) -> dict:
        return asdict(self)

    def validate(self) -> bool:
        return self.amount > 0 and self.fee >= MIN_FEE

    @staticmethod
    def create(from_address: str, to_address: str, amount: float, fee: float) -> "Transaction":
        return Transaction(
            tx_id=str(uuid.uuid4()),
            from_address=from_address,
            to_address=to_address,
            amount=amount,
            fee=fee,
            timestamp=time.time(),
        )


@dataclass
class Block:
    index: int
    timestamp: float
    transactions: list[Transaction]
    previous_hash: str
    miner_contributions: dict[str, float]
    total_reward: float
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "miner_contributions": self.miner_contributions,
            "total_reward": self.total_reward,
        }
        block_string = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "miner_contributions": self.miner_contributions,
            "total_reward": self.total_reward,
            "hash": self.hash,
        }


@dataclass
class Wallet:
    address: str
    balance: float = 0.0

    def to_dict(self) -> dict:
        return {"address": self.address, "balance": self.balance}


@dataclass
class User:
    user_id: str
    name: str
    wallet: Wallet
    is_miner: bool = False
    miner_slot: Optional[int] = None
    frequency: Optional[int] = None

    def to_dict(self) -> dict:
        data = {
            "user_id": self.user_id,
            "name": self.name,
            "wallet": self.wallet.to_dict(),
            "is_miner": self.is_miner,
        }
        if self.is_miner:
            data["miner_slot"] = self.miner_slot
            data["frequency"] = self.frequency
        return data


class Blockchain:
    def __init__(self):
        self.chain: list[Block] = []
        self.pending_transactions: list[Transaction] = []
        self.users: dict[str, User] = {}
        self.miner_slots: list[Optional[str]] = [None] * 4
        self.block_start_time: float = time.time()
        self._create_genesis_block()

    def _create_genesis_block(self):
        genesis = Block(
            index=0,
            timestamp=time.time(),
            transactions=[],
            previous_hash="0" * 64,
            miner_contributions={},
            total_reward=0.0,
        )
        self.chain.append(genesis)

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def get_block_reward(self) -> float:
        halvings = len(self.chain) // HALVING_INTERVAL
        return INITIAL_REWARD / (2**halvings)

    def get_total_fees(self) -> float:
        return sum(tx.fee for tx in self.pending_transactions)

    def get_target_from_transactions(self) -> Optional[float]:
        """Calculate mining target (0.3-0.7) from pending transaction hashes"""
        if not self.pending_transactions:
            return None

        # Combine all transaction IDs
        combined = "".join(tx.tx_id for tx in self.pending_transactions)
        hash_bytes = hashlib.sha256(combined.encode()).digest()

        # Use first 4 bytes to get a number 0-1
        value = int.from_bytes(hash_bytes[:4], 'big') / (2**32)

        # Scale to 0.3-0.7 range
        return 0.3 + value * 0.4

    def create_user(self, name: str) -> User:
        user_id = str(uuid.uuid4())
        wallet = Wallet(address=user_id, balance=INITIAL_BALANCE)
        user = User(user_id=user_id, name=name, wallet=wallet)
        self.users[user_id] = user
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def get_free_miner_slot(self) -> Optional[int]:
        for i, slot in enumerate(self.miner_slots):
            if slot is None:
                return i
        return None

    def assign_miner_slot(self, user_id: str) -> Optional[tuple[int, int]]:
        from config import MINER_FREQUENCIES

        user = self.get_user(user_id)
        if not user or user.is_miner:
            return None

        slot = self.get_free_miner_slot()
        if slot is None:
            return None

        user.is_miner = True
        user.miner_slot = slot
        user.frequency = MINER_FREQUENCIES[slot]
        self.miner_slots[slot] = user_id
        return (slot, user.frequency)

    def release_miner_slot(self, user_id: str) -> bool:
        user = self.get_user(user_id)
        if not user or not user.is_miner:
            return False

        slot = user.miner_slot
        if slot is not None:
            self.miner_slots[slot] = None
        user.is_miner = False
        user.miner_slot = None
        user.frequency = None
        return True

    def remove_user(self, user_id: str):
        if user_id in self.users:
            self.release_miner_slot(user_id)
            del self.users[user_id]

    def add_transaction(self, from_id: str, to_id: str, amount: float, fee: float) -> Optional[Transaction]:
        sender = self.get_user(from_id)
        receiver = self.get_user(to_id)

        if not sender or not receiver:
            return None

        if sender.wallet.balance < amount + fee:
            return None

        if fee < MIN_FEE:
            return None

        tx = Transaction.create(from_id, to_id, amount, fee)

        # Deduct immediately (pending state)
        sender.wallet.balance -= amount + fee

        self.pending_transactions.append(tx)
        return tx

    def mine_block(self, contributions: dict[str, float]) -> Optional[Block]:
        if not contributions:
            return None

        total_contribution = sum(contributions.values())
        if total_contribution == 0:
            return None

        # Normalize contributions
        normalized = {k: v / total_contribution for k, v in contributions.items()}

        # Calculate rewards
        block_reward = self.get_block_reward()
        total_fees = self.get_total_fees()
        total_reward = block_reward + total_fees

        # Distribute rewards to miners
        rewards = {}
        for miner_id, share in normalized.items():
            user = self.get_user(miner_id)
            if user:
                reward = total_reward * share
                user.wallet.balance += reward
                rewards[miner_id] = reward

        # Credit receivers for pending transactions
        for tx in self.pending_transactions:
            receiver = self.get_user(tx.to_address)
            if receiver:
                receiver.wallet.balance += tx.amount

        # Create block
        block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=self.pending_transactions.copy(),
            previous_hash=self.last_block.hash,
            miner_contributions=normalized,
            total_reward=total_reward,
        )

        self.chain.append(block)
        self.pending_transactions = []
        self.block_start_time = time.time()

        return block

    def get_miners(self) -> list[User]:
        return [self.users[uid] for uid in self.miner_slots if uid is not None]

    def get_state(self) -> dict:
        return {
            "chain_length": len(self.chain),
            "pending_tx": len(self.pending_transactions),
            "miners": [self.users[uid].to_dict() for uid in self.miner_slots if uid is not None],
            "users": [u.to_dict() for u in self.users.values() if not u.is_miner],
            "block_reward": self.get_block_reward(),
            "pending_fees": self.get_total_fees(),
        }

    def get_leaderboard(self) -> list[dict]:
        sorted_users = sorted(self.users.values(), key=lambda u: u.wallet.balance, reverse=True)
        return [
            {"rank": i + 1, "name": u.name, "balance": u.wallet.balance, "is_miner": u.is_miner}
            for i, u in enumerate(sorted_users)
        ]
