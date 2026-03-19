import asyncio
import pygame
import hexmath as hm
from board import Board
from pieces import create_piece, Move
from ai import AIWorker

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


def execute_board_move(gs, from_key, to_key):
    """Execute a move (from_key→to_key) on gs, handle en passant, update turn + game-over."""
    board = gs["board"]
    moving_piece = board.pieces[from_key]

    # En passant detection
    att_dirs = [1, 5] if moving_piece.color == "white" else [2, 4]
    att_targets = {
        (hm.hex_neighbor(moving_piece.pos, d).q,
         hm.hex_neighbor(moving_piece.pos, d).r,
         hm.hex_neighbor(moving_piece.pos, d).s)
        for d in att_dirs
    }
    is_ep = (
        moving_piece.name == "Pawn"
        and to_key in att_targets
        and to_key not in board.pieces
    )

    from_pos = moving_piece.pos
    board.move_piece(from_key, to_key)

    if is_ep and gs["last_move"]:
        ep_cap = (gs["last_move"].to_pos.q,
                  gs["last_move"].to_pos.r,
                  gs["last_move"].to_pos.s)
        board.pieces.pop(ep_cap, None)

    moved_piece = board.pieces[to_key]
    gs["last_move"]    = Move(moved_piece, from_pos, moved_piece.pos)
    gs["current_turn"] = "black" if gs["current_turn"] == "white" else "white"
    gs["selected_key"] = None
    gs["legal_moves"]  = []
    gs["in_check"]     = False

    if board.find_king_key(gs["current_turn"]) is None:
        gs["game_over"]   = True
        gs["game_result"] = "king_captured"
        gs["winner"]      = "black" if gs["current_turn"] == "white" else "white"
        gs["game_time"]   = pygame.time.get_ticks() - gs["start_time"]
    else:
        gs["in_check"] = board.is_in_check(gs["current_turn"])
        if not board.has_legal_moves(gs["current_turn"], gs["last_move"]):
            gs["game_over"]   = True
            gs["game_result"] = "checkmate" if gs["in_check"] else "stalemate"
            gs["winner"]      = (None if gs["game_result"] == "stalemate"
                                 else ("black" if gs["current_turn"] == "white" else "white"))
            gs["game_time"]   = pygame.time.get_ticks() - gs["start_time"]


def execute_player_move(gs, clicked_key):
    execute_board_move(gs, gs["selected_key"], clicked_key)


def reset_game_state():
    return dict(
        board        = setup_game(),
        current_turn = "white",
        selected_key = None,
        legal_moves  = [],
        last_move    = None,
        in_check     = False,
        game_over    = False,
        game_result  = None,
        winner       = None,
        start_time   = pygame.time.get_ticks(),
        game_time    = 0,
    )


def draw_menu(screen, font_big, font_med, font, depth_sel, vs_ai):
    screen.fill((40, 40, 60))

    title = font_big.render("Hex Chess", True, (255, 215, 0))
    screen.blit(title, (400 - title.get_width() // 2, 60))

    mode_label = font_med.render("Mode:", True, (200, 200, 200))
    screen.blit(mode_label, (160, 170))

    human_rect = pygame.Rect(260, 162, 130, 40)
    ai_rect    = pygame.Rect(410, 162, 130, 40)
    pygame.draw.rect(screen, (70, 130, 70) if not vs_ai else (60, 60, 80), human_rect, border_radius=6)
    pygame.draw.rect(screen, (70, 130, 70) if vs_ai  else (60, 60, 80), ai_rect,    border_radius=6)
    hl = font.render("Human vs Human", True, (255,255,255))
    al = font.render("vs AI (black)",  True, (255,255,255))
    screen.blit(hl, (human_rect.x + human_rect.w//2 - hl.get_width()//2,
                     human_rect.y + 10))
    screen.blit(al, (ai_rect.x + ai_rect.w//2 - al.get_width()//2,
                     ai_rect.y + 10))

    depth_label = font_med.render("AI Depth:", True, (200, 200, 200))
    screen.blit(depth_label, (160, 250))

    depth_rects = []
    for i, d in enumerate(range(1, 6)):
        r = pygame.Rect(280 + i * 62, 242, 54, 40)
        depth_rects.append(r)
        active = (d == depth_sel)
        pygame.draw.rect(screen, (70, 130, 180) if active else (60, 60, 80), r, border_radius=6)
        dl = font_med.render(str(d), True, (255, 255, 255))
        screen.blit(dl, (r.x + r.w//2 - dl.get_width()//2, r.y + 7))

    if not vs_ai:
        note = font.render("Depth only matters in vs-AI mode", True, (130, 130, 130))
        screen.blit(note, (400 - note.get_width()//2, 295))

    start_rect = pygame.Rect(300, 360, 200, 52)
    pygame.draw.rect(screen, (180, 80, 50), start_rect, border_radius=8)
    sl = font_med.render("Start Game", True, (255, 255, 255))
    screen.blit(sl, (400 - sl.get_width()//2, 374))

    hint_depth = {
        1: "Instant  – very easy",
        2: "Fast     – easy",
        3: "~1-2s    – medium",
        4: "~5-10s   – hard",
        5: "~30s+    – very hard",
    }
    if vs_ai:
        hint = font.render(hint_depth[depth_sel], True, (150, 180, 150))
        screen.blit(hint, (400 - hint.get_width()//2, 430))

    return human_rect, ai_rect, depth_rects, start_rect


async def main():
    pygame.init()
    pygame.display.set_caption("Hex Chess")
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    font     = pygame.font.SysFont(None, 28)
    font_med = pygame.font.SysFont(None, 42)
    font_big = pygame.font.SysFont(None, 72)

    # ---- menu state ----
    in_menu    = True
    vs_ai      = True
    ai_depth   = 3
    ai_worker  = AIWorker()
    ai_color   = "black"

    # ---- game state ----
    gs = reset_game_state()

    PLAY_AGAIN_RECT = pygame.Rect(300, 390, 200, 48)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if in_menu:
                    human_rect, ai_rect, depth_rects, start_rect = draw_menu(
                        screen, font_big, font_med, font, ai_depth, vs_ai)
                    if human_rect.collidepoint(event.pos):
                        vs_ai = False
                    elif ai_rect.collidepoint(event.pos):
                        vs_ai = True
                    elif start_rect.collidepoint(event.pos):
                        gs = reset_game_state()
                        in_menu = False
                    else:
                        for i, r in enumerate(depth_rects):
                            if r.collidepoint(event.pos):
                                ai_depth = i + 1

                elif gs["game_over"]:
                    if PLAY_AGAIN_RECT.collidepoint(event.pos):
                        in_menu = True

                else:
                    # Block clicks while AI is thinking
                    if vs_ai and ai_worker.thinking:
                        pass
                    else:
                        clicked_hex = gs["board"].pixel_to_hex(*event.pos)
                        clicked_key = (clicked_hex.q, clicked_hex.r, clicked_hex.s)
                        on_board    = (clicked_hex.q, clicked_hex.r) in gs["board"].hex_coords

                        if not on_board:
                            gs["selected_key"] = None
                            gs["legal_moves"]  = []
                        elif gs["selected_key"] is not None:
                            legal_keys = {(h.q, h.r, h.s) for h in gs["legal_moves"]}
                            if clicked_key in legal_keys:
                                execute_player_move(gs, clicked_key)
                            elif clicked_key == gs["selected_key"]:
                                gs["selected_key"] = None
                                gs["legal_moves"]  = []
                            elif (clicked_key in gs["board"].pieces and
                                  gs["board"].pieces[clicked_key].color == gs["current_turn"]):
                                gs["selected_key"] = clicked_key
                                gs["legal_moves"]  = gs["board"].get_legal_moves(
                                    gs["board"].pieces[clicked_key], gs["last_move"])
                            else:
                                gs["selected_key"] = None
                                gs["legal_moves"]  = []
                        else:
                            if (clicked_key in gs["board"].pieces and
                                    gs["board"].pieces[clicked_key].color == gs["current_turn"]):
                                gs["selected_key"] = clicked_key
                                gs["legal_moves"]  = gs["board"].get_legal_moves(
                                    gs["board"].pieces[clicked_key], gs["last_move"])

        # ---- AI move trigger ----
        if (not in_menu and not gs["game_over"] and vs_ai
                and gs["current_turn"] == ai_color
                and not ai_worker.thinking
                and ai_worker.result is None):
            ai_worker.start(gs["board"], ai_color, ai_depth, gs["last_move"])

        # ---- AI move apply ----
        if (not in_menu and not gs["game_over"] and vs_ai
                and gs["current_turn"] == ai_color
                and not ai_worker.thinking
                and ai_worker.result is not None):
            from_key, to_key = ai_worker.result
            ai_worker.result = None
            if from_key in gs["board"].pieces:
                execute_board_move(gs, from_key, to_key)

        # ---- render ----
        if in_menu:
            draw_menu(screen, font_big, font_med, font, ai_depth, vs_ai)
        else:
            elapsed   = (pygame.time.get_ticks() - gs["start_time"]
                         if not gs["game_over"] else gs["game_time"])
            check_key = (gs["board"].find_king_key(gs["current_turn"])
                         if gs["in_check"] and not gs["game_over"] else None)

            screen.fill((215, 200, 170))
            gs["board"].draw(screen,
                             selected_key=gs["selected_key"],
                             legal_moves=gs["legal_moves"],
                             check_key=check_key)

            time_surf = font.render(format_time(elapsed), True, (30, 30, 30))
            screen.blit(time_surf, (800 - time_surf.get_width() - 10, 10))

            if not gs["game_over"]:
                if vs_ai and ai_worker.thinking and gs["current_turn"] == ai_color:
                    thinking_surf = font.render("AI is thinking...", True, (80, 80, 180))
                    screen.blit(thinking_surf, (10, 10))
                else:
                    turn_label = font.render(f"{gs['current_turn'].capitalize()}'s turn",
                                             True, (30, 30, 30))
                    screen.blit(turn_label, (10, 10))
                if gs["in_check"]:
                    check_surf = font_med.render("CHECK!", True, (200, 30, 30))
                    screen.blit(check_surf, (400 - check_surf.get_width() // 2, 8))
            else:
                overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                screen.blit(overlay, (0, 0))

                if gs["game_result"] == "checkmate":
                    result_text = f"{gs['winner'].capitalize()} wins!"
                    sub_text    = "by Checkmate"
                elif gs["game_result"] == "stalemate":
                    result_text = "Stalemate!"
                    sub_text    = f"{gs['current_turn'].capitalize()} has no legal moves"
                else:
                    result_text = f"{gs['winner'].capitalize()} wins!"
                    sub_text    = "King captured"

                result_surf = font_big.render(result_text, True, (255, 255, 255))
                screen.blit(result_surf, (400 - result_surf.get_width() // 2, 160))

                sub_surf = font_med.render(sub_text, True, (210, 210, 210))
                screen.blit(sub_surf, (400 - sub_surf.get_width() // 2, 250))

                timer_surf = font_med.render(f"Game time: {format_time(gs['game_time'])}",
                                             True, (210, 210, 210))
                screen.blit(timer_surf, (400 - timer_surf.get_width() // 2, 300))

                pygame.draw.rect(screen, (70, 150, 70), PLAY_AGAIN_RECT, border_radius=8)
                btn_label = font_med.render("Back to Menu", True, (255, 255, 255))
                screen.blit(btn_label, (400 - btn_label.get_width() // 2, 403))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
