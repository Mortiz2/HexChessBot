import pygame
import hexmath as hm
from board import Board
from pieces import create_piece, Move

pygame.init()
pygame.display.set_caption("Hex Chess")
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
font     = pygame.font.SysFont(None, 28)
font_med = pygame.font.SysFont(None, 42)
font_big = pygame.font.SysFont(None, 72)

pieces_setup = [
    (-5, 0, 5, "bishop", "black"),
    (-4, 0, 4, "bishop", "black"),
    (-3, 0, 3, "bishop", "black"),
    (-4, -1, 5, "king", "black"),
    (-5, 1, 4, "queen", "black"),
    (-5, 2, 3, "knight", "black"),
    (-3, -2, 5, "knight", "black"),
    (-5, 3, 2, "rook", "black"),
    (-2, -3, 5, "rook", "black"),
    (-5, 4, 1, "pawn", "black"),
    (-4, 3, 1, "pawn", "black"),
    (-3, 2, 1, "pawn", "black"),
    (-2, 1, 1, "pawn", "black"),
    (-1, 0, 1, "pawn", "black"),
    (-1, -1, 2, "pawn", "black"),
    (-1, -2, 3, "pawn", "black"),
    (-1, -3, 4, "pawn", "black"),
    (-1, -4, 5, "pawn", "black"),

    (5, 0, -5, "bishop", "white"),
    (4, 0, -4, "bishop", "white"),
    (3, 0, -3, "bishop", "white"),
    (4, 1, -5, "queen", "white"),
    (5, -1, -4, "king", "white"),
    (5, -2, -3, "knight", "white"),
    (3, 2, -5, "knight", "white"),
    (2, 3, -5, "rook", "white"),
    (5, -3, -2, "rook", "white"),
    (1, 4, -5, "pawn", "white"),
    (1, 3, -4, "pawn", "white"),
    (1, 2, -3, "pawn", "white"),
    (1, 1, -2, "pawn", "white"),
    (1, 0, -1, "pawn", "white"),
    (2, -1, -1, "pawn", "white"),
    (3, -2, -1, "pawn", "white"),
    (4, -3, -1, "pawn", "white"),
    (5, -4, -1, "pawn", "white"),

]

def setup_game():
    b = Board(radius=5, hex_size=30)
    for q, r, s, ptype, color in pieces_setup:
        pos = hm.Hex(q, r, s)
        piece = create_piece(pos, color, ptype)
        b.add_piece(piece)
    return b


def format_time(ms):
    s = ms // 1000
    return f"{s // 60:02d}:{s % 60:02d}"


board        = setup_game()
current_turn = "white"
selected_key = None
legal_moves  = []
last_move    = None
in_check     = False
game_over    = False
game_result  = None   # "checkmate" | "stalemate" | "king_captured"
winner       = None   # "white" | "black" | None (stalemate)
start_time   = pygame.time.get_ticks()
game_time    = 0

PLAY_AGAIN_RECT = pygame.Rect(300, 390, 200, 48)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_over:
                if PLAY_AGAIN_RECT.collidepoint(event.pos):
                    board        = setup_game()
                    current_turn = "white"
                    selected_key = None
                    legal_moves  = []
                    last_move    = None
                    in_check     = False
                    game_over    = False
                    game_result  = None
                    winner       = None
                    start_time   = pygame.time.get_ticks()
                    game_time    = 0
            else:
                clicked_hex = board.pixel_to_hex(*event.pos)
                clicked_key = (clicked_hex.q, clicked_hex.r, clicked_hex.s)
                on_board    = (clicked_hex.q, clicked_hex.r) in board.hex_coords

                if not on_board:
                    selected_key = None
                    legal_moves  = []
                elif selected_key is not None:
                    legal_keys = {(h.q, h.r, h.s) for h in legal_moves}
                    if clicked_key in legal_keys:
                        # Detect en passant before the move changes the board
                        moving_piece = board.pieces[selected_key]
                        att_dirs = [1, 5] if moving_piece.color == "white" else [2, 4]
                        att_targets = {
                            (hm.hex_neighbor(moving_piece.pos, d).q,
                             hm.hex_neighbor(moving_piece.pos, d).r,
                             hm.hex_neighbor(moving_piece.pos, d).s)
                            for d in att_dirs
                        }
                        is_ep = (
                            moving_piece.name == "Pawn"
                            and clicked_key in att_targets
                            and clicked_key not in board.pieces
                        )

                        from_pos = board.pieces[selected_key].pos
                        board.move_piece(selected_key, clicked_key)

                        # Remove the pawn captured via en passant
                        if is_ep and last_move:
                            ep_cap = (last_move.to_pos.q, last_move.to_pos.r, last_move.to_pos.s)
                            board.pieces.pop(ep_cap, None)

                        moved_piece = board.pieces[clicked_key]
                        last_move   = Move(moved_piece, from_pos, moved_piece.pos)
                        current_turn = "black" if current_turn == "white" else "white"
                        selected_key = None
                        legal_moves  = []
                        in_check     = False

                        # --- game-over detection ---
                        if board.find_king_key(current_turn) is None:
                            game_over   = True
                            game_result = "king_captured"
                            winner      = "black" if current_turn == "white" else "white"
                            game_time   = pygame.time.get_ticks() - start_time
                        else:
                            in_check = board.is_in_check(current_turn)
                            if not board.has_legal_moves(current_turn, last_move):
                                game_over   = True
                                game_result = "checkmate" if in_check else "stalemate"
                                winner      = None if game_result == "stalemate" else (
                                    "black" if current_turn == "white" else "white"
                                )
                                game_time = pygame.time.get_ticks() - start_time

                    elif clicked_key == selected_key:
                        selected_key = None
                        legal_moves  = []
                    elif clicked_key in board.pieces and board.pieces[clicked_key].color == current_turn:
                        selected_key = clicked_key
                        legal_moves  = board.get_legal_moves(board.pieces[clicked_key], last_move)
                    else:
                        selected_key = None
                        legal_moves  = []
                else:
                    if clicked_key in board.pieces and board.pieces[clicked_key].color == current_turn:
                        selected_key = clicked_key
                        legal_moves  = board.get_legal_moves(board.pieces[clicked_key], last_move)

    # ---- render ----
    elapsed   = pygame.time.get_ticks() - start_time if not game_over else game_time
    check_key = board.find_king_key(current_turn) if (in_check and not game_over) else None

    screen.fill((215, 200, 170))
    board.draw(screen, selected_key=selected_key, legal_moves=legal_moves, check_key=check_key)

    # timer – top right
    time_surf = font.render(format_time(elapsed), True, (30, 30, 30))
    screen.blit(time_surf, (800 - time_surf.get_width() - 10, 10))

    if not game_over:
        turn_label = font.render(f"{current_turn.capitalize()}'s turn", True, (30, 30, 30))
        screen.blit(turn_label, (10, 10))
        if in_check:
            check_surf = font_med.render("CHECK!", True, (200, 30, 30))
            screen.blit(check_surf, (400 - check_surf.get_width() // 2, 8))
    else:
        # semi-transparent overlay
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        if game_result == "checkmate":
            result_text = f"{winner.capitalize()} wins!"
            sub_text    = "by Checkmate"
        elif game_result == "stalemate":
            result_text = "Stalemate!"
            sub_text    = f"{current_turn.capitalize()} has no legal moves"
        else:
            result_text = f"{winner.capitalize()} wins!"
            sub_text    = "King captured"

        result_surf = font_big.render(result_text, True, (255, 255, 255))
        screen.blit(result_surf, (400 - result_surf.get_width() // 2, 160))

        sub_surf = font_med.render(sub_text, True, (210, 210, 210))
        screen.blit(sub_surf, (400 - sub_surf.get_width() // 2, 250))

        timer_surf = font_med.render(f"Game time: {format_time(game_time)}", True, (210, 210, 210))
        screen.blit(timer_surf, (400 - timer_surf.get_width() // 2, 300))

        pygame.draw.rect(screen, (70, 150, 70), PLAY_AGAIN_RECT, border_radius=8)
        btn_label = font_med.render("Play Again", True, (255, 255, 255))
        screen.blit(btn_label, (400 - btn_label.get_width() // 2, 403))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
