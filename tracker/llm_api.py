import os
import requests
import json

LLM_API_KEY = os.getenv('LLM_API_KEY')
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions" 
OPENAI_MODEL = "gpt-3.5-turbo" 

def generate_performance_report(player_username, last_session, history_data):
    """
    Generuje raport analityczny na podstawie statystyk gracza za pomocą LLM.
    W przypadku braku dostępu do API (błąd 429), uruchamia zaawansowany silnik analityczny (Fallback).
    """
    if not LLM_API_KEY:
        return "Błąd: Brak klucza LLM API. Nie można wygenerować raportu."
    # Przygotowanie kontekstu dla modelu
    prompt = f"""
    Jesteś analitykiem gier CS2 i musisz wygenerować krótki raport na temat wydajności gracza.
    Gracz: {player_username}
    Statystyki: K/D: {last_session.kd_ratio}, HS%: {last_session.headshot_percentage}%
    Historia K/D: {history_data}
    Analiza musi być krótka (3 zdania).
    """
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": "Jesteś ekspertem CS2 analitykiem."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }
    try:
        # Próba połączenia z OpenAI
        response = requests.post(OPENAI_ENDPOINT, headers=headers, data=json.dumps(payload), timeout=15)
        response.raise_for_status() 
        result = response.json()
        return result['choices'][0]['message']['content'].strip() 
    except Exception as e:
        # Logika ta uruchamia się, gdy API OpenAI zwraca błąd 429 lub inny
        kd = last_session.kd_ratio
        hs = last_session.headshot_percentage
        # Zaawansowana analiza trendu na podstawie historii
        if len(history_data) >= 3:
            # Obliczana zmiana między ostatnim a pierwszym pomiarem w historii
            change = history_data[-1] - history_data[0]
            if change > 0.1:
                trend_str = "wyraźny wzrost formy"
            elif change < -0.1:
                trend_str = "niepokojący spadek formy"
            else:
                trend_str = "stabilizacja wyników"
        else:
            trend_str = "brak wystarczających danych do określenia trendu"
        # Algorytm dobierania sugestii na podstawie progów matematycznych
        sugestie = []
        # K/D
        if kd < 1.0:
            sugestie.append("Twoja przeżywalność jest niska; skup się na grze defensywnej i unikaniu niepotrzebnych starć.")
        elif kd >= 1.2 and hs >= 50:
            sugestie.append("Twoja mechanika gry jest na bardzo wysokim poziomie; rozważ grę w bardziej wymagających ligach.")  
        # HS%
        if hs < 40:
            sugestie.append("Niski procent HS sugeruje problemy z kontrolą odrzutu (spray control) lub celowaniem na wysokości głowy.")
        elif hs > 55:
            sugestie.append("Twoja precyzja jest imponująca; skup się teraz na taktycznym wykorzystaniu granatów.")
        # Finalna rekomendacja
        final_rekomendacja = " ".join(sugestie) if sugestie else "Utrzymuj obecne tempo treningowe i analizuj swoje pozycjonowanie na mapie."
        # Sformatowany raport generowany lokalnie
        local_report = (
            f"Analiza wydajności dla gracza {player_username}: "
            f"Obecne K/D wynosi {kd:.2f} ({trend_str}). "
            f"Skuteczność Headshotów na poziomie {hs:.1f}%. "
            f"Rekomendacja: {final_rekomendacja}"
        )     
        return f"[SYSTEM ANALITYCZNY FALLBACK] {local_report}"