import random
import time
import os
import sys
from threading import Thread, Event
import msvcrt
import keyboard

class Tetris:
    def __init__(self):
        self.width = 10
        self.height = 20
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_time = 1.0
        self.game_over = False
        
        # 테트리스 블록 정의 (7가지)
        self.tetrominoes = {
            'I': [
                [[1, 1, 1, 1]],
                [[1], [1], [1], [1]]
            ],
            'O': [
                [[1, 1], [1, 1]]
            ],
            'T': [
                [[0, 1, 0], [1, 1, 1]],
                [[1, 0], [1, 1], [1, 0]],
                [[1, 1, 1], [0, 1, 0]],
                [[0, 1], [1, 1], [0, 1]]
            ],
            'S': [
                [[0, 1, 1], [1, 1, 0]],
                [[1, 0], [1, 1], [0, 1]]
            ],
            'Z': [
                [[1, 1, 0], [0, 1, 1]],
                [[0, 1], [1, 1], [1, 0]]
            ],
            'J': [
                [[1, 0, 0], [1, 1, 1]],
                [[1, 1], [1, 0], [1, 0]],
                [[1, 1, 1], [0, 0, 1]],
                [[0, 1], [0, 1], [1, 1]]
            ],
            'L': [
                [[0, 0, 1], [1, 1, 1]],
                [[1, 0], [1, 0], [1, 1]],
                [[1, 1, 1], [1, 0, 0]],
                [[1, 1], [0, 1], [0, 1]]
            ]
        }
        
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_rotation = 0
        
        self.next_piece = self.get_random_piece()
        self.spawn_piece()
        
        # 입력 처리를 위한 이벤트
        self.input_event = Event()
        self.quit_event = Event()
        self.pause_event = Event()
        
    def get_piece_preview(self, piece_type):
        """블록 모양을 미리보기로 보여주는 함수"""
        shapes = {
            'I': ["ㅁㅁㅁㅁ"],
            'O': ["ㅁㅁ", "ㅁㅁ"],
            'T': [" ㅁ ", "ㅁㅁㅁ"],
            'S': [" ㅁㅁ", "ㅁㅁ "],
            'Z': ["ㅁㅁ ", " ㅁㅁ"],
            'J': ["ㅁ  ", "ㅁㅁㅁ"],
            'L': ["  ㅁ", "ㅁㅁㅁ"]
        }
        return shapes.get(piece_type, [piece_type])
    
    def get_random_piece(self):
        return random.choice(list(self.tetrominoes.keys()))
    def reset_game(self):
        """게임을 초기화하는 함수"""
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_time = 1.0
        self.game_over = False
        self.pause_event.clear()
        self.quit_event.clear()
        
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_rotation = 0
        
        self.next_piece = self.get_random_piece()
        self.spawn_piece()
        return random.choice(list(self.tetrominoes.keys()))
    
    def spawn_piece(self):
        self.current_piece = self.next_piece
        self.next_piece = self.get_random_piece()
        self.current_rotation = 0
        self.current_x = self.width // 2 - 1
        self.current_y = 0
        
        # 게임 오버 체크
        if not self.is_valid_position():
            self.game_over = True
    
    def get_piece_shape(self):
        return self.tetrominoes[self.current_piece][self.current_rotation]
    
    def is_valid_position(self, x=None, y=None, rotation=None):
        if x is None:
            x = self.current_x
        if y is None:
            y = self.current_y
        if rotation is None:
            rotation = self.current_rotation
            
        shape = self.tetrominoes[self.current_piece][rotation]
        
        for py, row in enumerate(shape):
            for px, cell in enumerate(row):
                if cell:
                    new_x = x + px
                    new_y = y + py
                    
                    # 경계 체크
                    if new_x < 0 or new_x >= self.width or new_y >= self.height:
                        return False
                    
                    # 보드의 기존 블록과 충돌 체크
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return False
        
        return True
    
    def place_piece(self):
        shape = self.get_piece_shape()
        for py, row in enumerate(shape):
            for px, cell in enumerate(row):
                if cell:
                    board_x = self.current_x + px
                    board_y = self.current_y + py
                    if 0 <= board_y < self.height and 0 <= board_x < self.width:
                        self.board[board_y][board_x] = 1
        
        # 완성된 라인 제거
        self.clear_lines()
        self.spawn_piece()
    
    def clear_lines(self):
        lines_to_clear = []
        for y in range(self.height):
            if all(self.board[y]):
                lines_to_clear.append(y)
        
        for y in lines_to_clear:
            del self.board[y]
            self.board.insert(0, [0 for _ in range(self.width)])
        
        lines_cleared = len(lines_to_clear)
        if lines_cleared > 0:
            self.lines_cleared += lines_cleared
            # 점수 계산 (테트리스 스코어링)
            line_scores = [0, 40, 100, 300, 1200]
            self.score += line_scores[min(lines_cleared, 4)] * self.level
            
            # 레벨 업 (10라인마다)
            self.level = self.lines_cleared // 10 + 1
            self.fall_time = max(0.1, 1.0 - (self.level - 1) * 0.1)
    
    def move_left(self):
        if self.is_valid_position(self.current_x - 1):
            self.current_x -= 1
    
    def move_right(self):
        if self.is_valid_position(self.current_x + 1):
            self.current_x += 1
    
    def move_down(self):
        if self.is_valid_position(y=self.current_y + 1):
            self.current_y += 1
            return True
        else:
            self.place_piece()
            return False
    
    def rotate(self):
        new_rotation = (self.current_rotation + 1) % len(self.tetrominoes[self.current_piece])
        if self.is_valid_position(rotation=new_rotation):
            self.current_rotation = new_rotation
        elif self.is_valid_position(self.current_x - 1, rotation=new_rotation):
            self.current_x -= 1
            self.current_rotation = new_rotation
        elif self.is_valid_position(self.current_x + 1, rotation=new_rotation):
            self.current_x += 1
            self.current_rotation = new_rotation
    
    def get_display_board(self):
        # 현재 보드 복사
        display = [row[:] for row in self.board]
        
        # 현재 피스 추가
        shape = self.get_piece_shape()
        for py, row in enumerate(shape):
            for px, cell in enumerate(row):
                if cell:
                    board_x = self.current_x + px
                    board_y = self.current_y + py
                    if 0 <= board_y < self.height and 0 <= board_x < self.width:
                        display[board_y][board_x] = 2  # 현재 피스는 2로 표시
        
        return display
    
    def print_board(self):
        # 커서를 화면 맨 위로 이동 (화면 지우기 대신)
        print("\033[H", end="")
        display = self.get_display_board()
        
        print("=" * 32)
        print(f"TEXTRIS - 레벨: {self.level} | 점수: {self.score} | 라인: {self.lines_cleared}")
        print("=" * 32)
        print("조작법: ←→(이동) ↓(낙하) ↑/스페이스(회전) ESC(종료)")
        print("       엔터(일시정지/재개) R(재시작)")
        print("-" * 22)
        
        for row in display:
            print("|", end="")
            for cell in row:
                if cell == 0:
                    print(" ", end=" ")
                elif cell == 1:
                    print("ㅁ", end="")  # 고정된 블록
                else:
                    print("ㅁ", end="")  # 현재 피스
            print("|")
        
        print("-" * 22)
        
        # 다음 피스를 실제 모양으로 표시
        preview = self.get_piece_preview(self.next_piece)
        print("다음 피스:")
        for line in preview:
            print(f"  {line}")
        
        if self.pause_event.is_set():
            print("\n⏸️  게임 일시정지 - 엔터를 눌러 계속하세요")
        elif self.game_over:
            print("\n💀 게임 오버! R(재시작) 또는 ESC(종료)")
        
        # 나머지 줄들을 지우기 위해 빈 줄들 출력
        for _ in range(3):
            print(" " * 30)
    
    def input_handler(self):
        while not self.quit_event.is_set():
            try:
                if keyboard.is_pressed('enter'):
                    if self.pause_event.is_set():
                        self.pause_event.clear()
                    else:
                        self.pause_event.set()
                    self.print_board()
                    time.sleep(0.3)  # 연속 입력 방지
                elif keyboard.is_pressed('r'):
                    if self.game_over:
                        self.reset_game()
                        self.print_board()
                    time.sleep(0.3)
                elif keyboard.is_pressed('esc'):
                    self.quit_event.set()
                    break
                elif not self.pause_event.is_set() and not self.game_over:
                    if keyboard.is_pressed('left'):
                        self.move_left()
                        self.print_board()
                        time.sleep(0.15)  # 연속 입력 방지
                    elif keyboard.is_pressed('right'):
                        self.move_right()
                        self.print_board()
                        time.sleep(0.15)
                    elif keyboard.is_pressed('down'):
                        self.move_down()
                        self.print_board()
                        time.sleep(0.1)
                    elif keyboard.is_pressed('up') or keyboard.is_pressed('space'):
                        self.rotate()
                        self.print_board()
                        time.sleep(0.2)
            except:
                pass  # 키보드 오류 무시
            
            time.sleep(0.05)  # CPU 사용량 줄이기
    
    def run(self):
        # 화면 초기화
        os.system('cls' if os.name == 'nt' else 'clear')
        print("텍스트 테트리스 게임을 시작합니다!")
        print("잠시 후 게임이 시작됩니다...")
        time.sleep(2)
        
        # 화면 지우고 커서 숨기기
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\033[?25l", end="")  # 커서 숨기기
        
        self.print_board()
        
        # 입력 처리 스레드 시작
        input_thread = Thread(target=self.input_handler, daemon=True)
        input_thread.start()
        
        last_fall = time.time()
        
        while not self.quit_event.is_set():
            if self.game_over:
                time.sleep(0.1)
                continue
                
            if self.pause_event.is_set():
                time.sleep(0.1)
                continue
                
            current_time = time.time()
            
            # 자동 낙하
            if current_time - last_fall >= self.fall_time:
                self.move_down()
                if not self.game_over:
                    self.print_board()
                last_fall = current_time
            
            time.sleep(0.05)  # 부드러운 게임플레이
        
        # 커서 다시 보이기
        print("\033[?25h", end="")
        
        if self.game_over and not self.quit_event.is_set():
            self.print_board()
            print(f"\n🎯 최종 점수: {self.score}")
            print(f"📊 클리어한 라인: {self.lines_cleared}")
            print(f"⭐ 달성한 레벨: {self.level}")
            print("\nR키로 재시작하거나 ESC로 종료하세요.")
        else:
            print("\n게임이 종료되었습니다.")

if __name__ == "__main__":
    try:
        game = Tetris()
        game.run()
    except KeyboardInterrupt:
        print("\033[?25h")  # 커서 다시 보이기
        print("\n게임이 중단되었습니다.")
    except Exception as e:
        print("\033[?25h")  # 커서 다시 보이기
        print(f"오류 발생: {e}")
        input("엔터를 눌러 종료...")
