# -------------- MAIN WINDOW --------------

WINDOW_CAPTION = 'Solitaire 2.0'
COLOR_BG2 = '#007000'
COLOR_BG = '#008000'
T_COLOR = '#EEFFEE'
FONT = 'COURIER'
TEXT_SIZE = 17
FPS = 60

WIN_WIDTH = 543
WIN_HEIGHT = 470
LEFT_MARGIN = 30
TOP_MARGIN = 40

# -------------- GAME BOARD --------------

# Card dimensions
CARD_WIDTH = 63
CARD_HEIGHT = 90
STACK_LIMIT = 5

# Board positions
FACE_UP_STOCK = 'current_stock'
FOUNDATION = 'foundation'
TABLEAU = 'tableau'
STOCK = 'stock'

# Tableau dimensions
T_ROWS = range(28)
T_COLS = range(7)
T_X = LEFT_MARGIN
T_Y = 150

# Tableau cell dimensions
CELL_HEIGHT = 11
CELL_WIDTH = 70

FACE_UP_STOCK_DIM = (380, TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)
STOCK_DIM = (450, TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)
WASTE_DIM = (379, TOP_MARGIN, CARD_WIDTH, CARD_HEIGHT)
TABLEAU_DIM = (T_X, T_Y, 483, 300)
FOUNDATION_DIM = (0, 0, 350, 150)

# -------------- SOUND EFFECTS --------------

# Effect
WAV_MOVE = 'sfx_move.wav'
WAV_RESTOCK = 'sfx_error.wav'
WAV_INSERT = 'sfx_insert.wav'
WAV_ERROR = 'sfx_recycle.wav'
WAV_NEW_GAME = 'sfx_new_game.wav'

# Volume
VOL_MOVE = 0.5
VOL_RESTOCK = 0.5
VOL_INSERT = 1
VOL_ERROR = 1
VOL_NEW_GAME = 0.7

# -------------- BUTTON IMAGES --------------

SOUND_OFF_IMG = 'img_sound_off.png'
SOUND_ON_IMG = 'img_sound_on.png'
RESTOCK_IMG = 'img_recycle.png'
AUTO_IMG = 'img_auto.png'
INFO_IMG = 'img_info.png'

BTN_SFX_DIM = (520, 448, 15, 15)
