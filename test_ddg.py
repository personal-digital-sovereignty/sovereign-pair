from src.web_search import search_web
import traceback

def run():
    print("Test DDG:")
    try:
        r = search_web("Previsao tempo amanha Jandira", None)
        print("Tamanho:", len(r))
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    run()
