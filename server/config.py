# Miner frequency range (Hz) - each miner picks a frequency in this range
MIN_MINER_FREQUENCY = 300  # Hz
MAX_MINER_FREQUENCY = 1200  # Hz
DEFAULT_MINER_FREQUENCY = 440  # Hz - starting position for slider
MAX_MINERS = 4

# Mining
INITIAL_REWARD = 50.0
HALVING_INTERVAL = 100

# Target frequency (Hz) - this is what miners try to match
TARGET_BASE_FREQUENCY = 600  # Hz - base target frequency
TARGET_DRIFT_SPEED = 0.05  # How fast target drifts per second (Hz per tick)
TARGET_DRIFT_RANGE = 150  # Hz - max drift from base target

# Difficulty (Hz tolerance for frequency matching)
INITIAL_TOLERANCE_HZ = 30  # Hz - starting tolerance
MIN_TOLERANCE_HZ = 10      # Hz - hardest difficulty
MAX_TOLERANCE_HZ = 80      # Hz - easiest difficulty
TOLERANCE_STEP_HZ = 5      # Hz

# Difficulty adjustment
FAST_BLOCK_THRESHOLD = 5.0  # seconds
SLOW_BLOCK_THRESHOLD = 30.0  # seconds

# Contribution threshold (0-1, need this average contribution to mine)
MIN_CONTRIBUTION_THRESHOLD = 0.3

# Transactions
MIN_FEE = 0.01
INITIAL_BALANCE = 100.0  # Starting balance for new users

# Server
WEBSOCKET_HOST = "0.0.0.0"
WEBSOCKET_PORT = 8765
TICK_RATE = 0.1  # 10 updates/sec

# Audio
SAMPLE_RATE = 44100
CHUNK_SIZE = 4096
FFT_WINDOW = 2048
AUDIO_DEVICE = 0  # Fifine microphone (use None for default, or device index)

# GPIO (Raspberry Pi buzzer)
BUZZER_PIN = 18
