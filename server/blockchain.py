import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional

from config import INITIAL_REWARD, HALVING_INTERVAL, MIN_FEE, INITIAL_BALANCE, DEFAULT_MINER_FREQUENCY

# Path for persisting user data
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")


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
    device_id: Optional[str] = None
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

    def to_persist_dict(self) -> dict:
        """Data to persist (excludes transient state like miner status)"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "device_id": self.device_id,
            "balance": self.wallet.balance,
        }


class Blockchain:
    def __init__(self):
        self.chain: list[Block] = []
        self.pending_transactions: list[Transaction] = []
        self.users: dict[str, User] = {}  # Active users by user_id
        self.persisted_users: dict[str, dict] = {}  # Persisted users by device_id
        self.miner_slots: list[Optional[str]] = [None] * 4
        self.block_start_time: float = time.time()
        self._create_genesis_block()
        self._load_persisted_users()

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

    def _load_persisted_users(self):
        """Load persisted user data from disk"""
        if os.path.exists(USERS_FILE):
            try:
                with open(USERS_FILE, "r") as f:
                    data = json.load(f)
                    self.persisted_users = {u["device_id"]: u for u in data if u.get("device_id")}
                    print(f"Loaded {len(self.persisted_users)} persisted users")
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading users: {e}")
                self.persisted_users = {}

    def _save_persisted_users(self):
        """Save user data to disk"""
        os.makedirs(DATA_DIR, exist_ok=True)
        try:
            # Merge active users into persisted data
            for user in self.users.values():
                if user.device_id:
                    self.persisted_users[user.device_id] = user.to_persist_dict()

            data = list(self.persisted_users.values())
            with open(USERS_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            print(f"Error saving users: {e}")

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def get_block_reward(self) -> float:
        halvings = len(self.chain) // HALVING_INTERVAL
        return INITIAL_REWARD / (2**halvings)

    def get_total_fees(self) -> float:
        return sum(tx.fee for tx in self.pending_transactions)

    def get_target_from_transactions(self) -> Optional[float]:
        """Calculate mining target (0.05-0.95) from pending transaction hashes.

        Uses full range to require both very quiet and very loud sounds,
        making it much harder to hit the target precisely.
        """
        if not self.pending_transactions:
            return None

        # Combine all transaction IDs
        combined = "".join(tx.tx_id for tx in self.pending_transactions)
        hash_bytes = hashlib.sha256(combined.encode()).digest()

        # Use first 4 bytes to get a number 0-1
        value = int.from_bytes(hash_bytes[:4], 'big') / (2**32)

        # Scale to 0.05-0.95 range (full range, very challenging)
        return 0.05 + value * 0.9

    def create_user(self, name: str, device_id: Optional[str] = None) -> User:
        """Create or restore a user. If device_id is provided and exists, restore the user."""
        # Check if we have persisted data for this device
        if device_id and device_id in self.persisted_users:
            persisted = self.persisted_users[device_id]
            user_id = persisted["user_id"]
            balance = persisted.get("balance", INITIAL_BALANCE)
            # Update name if changed
            wallet = Wallet(address=user_id, balance=balance)
            user = User(user_id=user_id, name=name, wallet=wallet, device_id=device_id)
            self.users[user_id] = user
            print(f"Restored user {name} (device: {device_id[:8]}...) with balance {balance}")
            return user

        # Create new user
        user_id = str(uuid.uuid4())
        wallet = Wallet(address=user_id, balance=INITIAL_BALANCE)
        user = User(user_id=user_id, name=name, wallet=wallet, device_id=device_id)
        self.users[user_id] = user

        # Persist immediately if we have a device_id
        if device_id:
            self._save_persisted_users()
            print(f"Created new user {name} (device: {device_id[:8]}...)")

        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def get_free_miner_slot(self) -> Optional[int]:
        for i, slot in enumerate(self.miner_slots):
            if slot is None:
                return i
        return None

    def assign_miner_slot(self, user_id: str) -> Optional[tuple[int, float]]:
        """Assign a miner slot to a user. Returns (slot, default_frequency)."""
        user = self.get_user(user_id)
        if not user or user.is_miner:
            return None

        slot = self.get_free_miner_slot()
        if slot is None:
            return None

        user.is_miner = True
        user.miner_slot = slot
        user.frequency = DEFAULT_MINER_FREQUENCY  # Miner controls their own frequency now
        self.miner_slots[slot] = user_id
        return (slot, user.frequency)

    def set_miner_frequency(self, user_id: str, frequency: float):
        """Update a miner's current frequency (from their slider control)."""
        user = self.get_user(user_id)
        if user and user.is_miner:
            user.frequency = frequency

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
            # Save user data before removing
            self._save_persisted_users()
            self.release_miner_slot(user_id)
            del self.users[user_id]

    def add_transaction(self, from_id: str, to_id: str, amount: float, fee: float) -> tuple[Optional[Transaction], Optional[str]]:
        sender = self.get_user(from_id)
        receiver = self.get_user(to_id)

        if not sender:
            return None, "Sender not found"

        if not receiver:
            return None, "Recipient not found"

        if amount <= 0:
            return None, "Amount must be positive"

        if fee < MIN_FEE:
            return None, f"Fee too low (minimum: {MIN_FEE})"

        total = amount + fee
        if sender.wallet.balance < total:
            return None, f"Insufficient funds (need {total:.2f}, have {sender.wallet.balance:.2f})"

        tx = Transaction.create(from_id, to_id, amount, fee)

        # Deduct immediately (pending state)
        sender.wallet.balance -= total

        self.pending_transactions.append(tx)
        return tx, None

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

        # Persist user balances after mining
        self._save_persisted_users()

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
