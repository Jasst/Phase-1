"""Полный цикл main() без окна: сценарий ввода, проверка памяти и отрисовки.
Запуск из папки проекта:  python tests/test_e2e_headless.py
Файлы episodes.json / brain_state.json создаются в папке проекта — удалите после теста."""
import os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
os.environ["SDL_VIDEODRIVER"] = "dummy"; os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["BRAIN_LM_PATH"] = "/nonexistent/model.gguf"   # режим без LM
sys.path.insert(0, ROOT); os.chdir(ROOT)
import pygame
import brain_chat as bc

def text(t): return pygame.event.Event(pygame.TEXTINPUT, text=t)
def enter(): return pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, mod=0, unicode="\r", scancode=0)
script = {1: [text("что такое нейрон")], 2: [enter()],
          6: [text("/teach нейрон это клетка мозга")], 7: [enter()],
          12: [text("что такое нейрон")], 13: [enter()],
          18: [text("/recall нейрон")], 19: [enter()], 24: [text("/mind")], 25: [enter()],
          30: [text("/sleep")], 31: [enter()], 36: [text("/good")], 37: [enter()]}
state = {"frame": 0, "chat": [], "overlay": 0}
real_get = pygame.event.get
def fake_get(*a, **k):
    real_get(); state["frame"] += 1
    return [pygame.event.Event(pygame.QUIT)] if state["frame"] > 60 else script.get(state["frame"], [])
pygame.event.get = fake_get
real_chat, real_ov = bc.draw_chat, bc.draw_overlay
def rec_chat(screen, thoughts, chat, *a, **k):
    state["chat"] = [list(x) for x in chat]; return real_chat(screen, thoughts, chat, *a, **k)
def rec_ov(*a, **k):
    state["overlay"] += 1; return real_ov(*a, **k)
bc.draw_chat, bc.draw_overlay = rec_chat, rec_ov
bc.main()
msgs = [m for _, m in state["chat"]]
assert any("Вспомнила похожий вопрос" in m for m in msgs), "память не вспомнила эпизод"
assert state["overlay"] >= 60, "оверлей не рисуется каждый кадр"
print("e2e OK: эпизод вспомнен, оверлей отрисован", state["overlay"], "раз")
