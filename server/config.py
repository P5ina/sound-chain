# Miner frequencies (Hz)
MINER_FREQUENCIES = [440, 587, 784, 1047]
MAX_MINERS = 4

# Mining
INITIAL_REWARD = 50.0
HALVING_INTERVAL = 100
INITIAL_TOLERANCE = 0.03  # Very tight tolerance to start
MIN_TOLERANCE = 0.01      # Extremely precise required
MAX_TOLERANCE = 0.08      # Even max is challenging

# Target drift (moving target)
TARGET_DRIFT_SPEED = 0.02  # How fast target drifts per second
TARGET_DRIFT_RANGE = 0.15  # Max drift from base target

# Difficulty adjustment
FAST_BLOCK_THRESHOLD = 5.0  # seconds
SLOW_BLOCK_THRESHOLD = 30.0  # seconds
TOLERANCE_STEP = 0.01

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
