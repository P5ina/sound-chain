import asyncio
import json
import time
from typing import Optional

import websockets
from websockets.server import WebSocketServerProtocol

from blockchain import Blockchain
from audio import AudioAnalyzer, Buzzer
from config import (
    WEBSOCKET_HOST,
    WEBSOCKET_PORT,
    TICK_RATE,
    INITIAL_TOLERANCE,
    MIN_TOLERANCE,
    MAX_TOLERANCE,
    TOLERANCE_STEP,
    FAST_BLOCK_THRESHOLD,
    SLOW_BLOCK_THRESHOLD,
    BUZZER_PIN,
)


class SoundChainServer:
    def __init__(self):
        self.blockchain = Blockchain()
        self.audio = AudioAnalyzer()
        self.buzzer = Buzzer(BUZZER_PIN)
        self.connections: dict[str, WebSocketServerProtocol] = {}
        self.tolerance = INITIAL_TOLERANCE
        self._running = False

    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.connections:
            try:
                await self.connections[user_id].send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                pass

    async def broadcast(self, message: dict, exclude: Optional[str] = None):
        payload = json.dumps(message)
        for user_id, ws in list(self.connections.items()):
            if user_id != exclude:
                try:
                    await ws.send(payload)
                except websockets.exceptions.ConnectionClosed:
                    pass

    async def handle_join(self, ws: WebSocketServerProtocol, data: dict) -> Optional[str]:
        name = data.get("name", "Anonymous")
        user = self.blockchain.create_user(name)
        self.connections[user.user_id] = ws

        await self.send_to_user(
            user.user_id,
            {
                "type": "joined",
                "user_id": user.user_id,
                "role": "user",
                "wallet": user.wallet.to_dict(),
            },
        )

        # Broadcast updated state
        await self.broadcast_state()
        return user.user_id

    async def handle_become_miner(self, user_id: str):
        result = self.blockchain.assign_miner_slot(user_id)
        if result:
            slot, frequency = result
            await self.send_to_user(
                user_id,
                {"type": "became_miner", "frequency": frequency, "slot": slot},
            )
            await self.broadcast_state()
        else:
            await self.send_to_user(
                user_id,
                {"type": "error", "message": "No miner slots available"},
            )

    async def handle_leave_mining(self, user_id: str):
        if self.blockchain.release_miner_slot(user_id):
            await self.send_to_user(user_id, {"type": "left_mining"})
            await self.broadcast_state()

    async def handle_transfer(self, user_id: str, data: dict):
        to_id = data.get("to")
        amount = data.get("amount", 0)
        fee = data.get("fee", 0)

        tx, error = self.blockchain.add_transaction(user_id, to_id, amount, fee)
        if tx:
            await self.send_to_user(
                user_id,
                {"type": "transaction_pending", "tx": tx.to_dict()},
            )
            await self.broadcast_state()
        else:
            await self.send_to_user(
                user_id,
                {"type": "error", "message": f"Transaction failed: {error}"},
            )

    async def handle_message(self, ws: WebSocketServerProtocol, user_id: Optional[str], message: str) -> Optional[str]:
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "join":
                return await self.handle_join(ws, data)
            elif user_id is None:
                await ws.send(json.dumps({"type": "error", "message": "Not joined"}))
                return None

            if msg_type == "become_miner":
                await self.handle_become_miner(user_id)
            elif msg_type == "leave_mining":
                await self.handle_leave_mining(user_id)
            elif msg_type == "transfer":
                await self.handle_transfer(user_id, data)
            elif msg_type == "get_state":
                await self.send_to_user(user_id, {"type": "state", **self.blockchain.get_state()})
            elif msg_type == "get_leaderboard":
                await self.send_to_user(
                    user_id,
                    {"type": "leaderboard", "entries": self.blockchain.get_leaderboard()},
                )

        except json.JSONDecodeError:
            await ws.send(json.dumps({"type": "error", "message": "Invalid JSON"}))
        except Exception as e:
            print(f"Error handling message: {e}")
            await ws.send(json.dumps({"type": "error", "message": str(e)}))

        return user_id

    async def broadcast_state(self):
        state = {"type": "state", **self.blockchain.get_state()}
        await self.broadcast(state)

    async def broadcast_mining_status(self):
        miners = self.blockchain.get_miners()
        if not miners:
            return

        # Get target from pending transactions
        target = self.blockchain.get_target_from_transactions()

        # Get active miners mapping (user_id -> frequency)
        active_miners = {m.user_id: m.frequency for m in miners if m.frequency}
        contributions = self.audio.get_contributions(active_miners)

        # Current level is sum of active miners' contributions
        current_level = sum(contributions.values())

        status = {
            "type": "mining_status",
            "contributions": contributions,
            "target": target,  # None if no pending transactions
            "current": current_level,
            "tolerance": self.tolerance,
            "pending_tx": len(self.blockchain.pending_transactions),
        }

        # Send to all miners
        for miner in miners:
            await self.send_to_user(miner.user_id, status)

    def check_block_mined(self) -> bool:
        # Must have pending transactions to mine
        target = self.blockchain.get_target_from_transactions()
        if target is None:
            return False

        miners = self.blockchain.get_miners()
        if not miners:
            return False

        active_miners = {m.user_id: m.frequency for m in miners if m.frequency}
        contributions = self.audio.get_contributions(active_miners)
        current = sum(contributions.values())
        return abs(current - target) <= self.tolerance

    def adjust_difficulty(self, block_time: float):
        if block_time < FAST_BLOCK_THRESHOLD:
            self.tolerance = max(MIN_TOLERANCE, self.tolerance - TOLERANCE_STEP)
        elif block_time > SLOW_BLOCK_THRESHOLD:
            self.tolerance = min(MAX_TOLERANCE, self.tolerance + TOLERANCE_STEP)

    async def mine_block_if_ready(self):
        miners = self.blockchain.get_miners()
        if not miners:
            return

        if not self.check_block_mined():
            return

        # Get contributions
        active_miners = {m.user_id: m.frequency for m in miners if m.frequency}
        contributions = self.audio.get_contributions(active_miners)

        # Only mine if there's actual contribution
        if sum(contributions.values()) < 0.1:
            return

        block = self.blockchain.mine_block(contributions)
        if block:
            block_time = time.time() - self.blockchain.block_start_time
            self.adjust_difficulty(block_time)

            # Buzz!
            self.buzzer.beep()

            # Calculate rewards per miner
            rewards = {}
            for miner_id, share in block.miner_contributions.items():
                rewards[miner_id] = block.total_reward * share

            # Broadcast block mined
            await self.broadcast(
                {
                    "type": "block_mined",
                    "block": block.to_dict(),
                    "rewards": rewards,
                    "block_time": block_time,
                }
            )

            # Notify confirmed transactions
            for tx in block.transactions:
                await self.send_to_user(
                    tx.from_address,
                    {"type": "transaction_confirmed", "tx": tx.to_dict()},
                )
                await self.send_to_user(
                    tx.to_address,
                    {"type": "transaction_confirmed", "tx": tx.to_dict()},
                )

            await self.broadcast_state()

    async def mining_loop(self):
        while self._running:
            await self.broadcast_mining_status()
            await self.mine_block_if_ready()
            await asyncio.sleep(TICK_RATE)

    async def handle_connection(self, ws: WebSocketServerProtocol):
        user_id: Optional[str] = None
        try:
            async for message in ws:
                user_id = await self.handle_message(ws, user_id, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            if user_id:
                self.blockchain.remove_user(user_id)
                if user_id in self.connections:
                    del self.connections[user_id]
                await self.broadcast_state()

    async def start(self):
        self._running = True
        self.audio.start()

        mining_task = asyncio.create_task(self.mining_loop())

        print(f"SoundChain server starting on ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
        async with websockets.serve(self.handle_connection, WEBSOCKET_HOST, WEBSOCKET_PORT):
            await asyncio.Future()  # Run forever

        mining_task.cancel()
        self.audio.stop()
        self.buzzer.cleanup()


async def main():
    server = SoundChainServer()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
