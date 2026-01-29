import requests
import os
from dotenv import load_dotenv
from pathlib import Path

# Zbudowanie ścieżki do pliku .env, który znajduje się w katalogu cs2_tracker/
try:
    dotenv_path = Path(__file__).resolve().parent.parent / 'cs2_tracker' / '.env'
    load_dotenv(dotenv_path=dotenv_path)
except Exception as e:
    print(f"Ostrzeżenie: Nie udało się załadować .env w steam_api.py: {e}")

STEAM_API_KEY = os.getenv('STEAM_API_KEY')
CSGO_APP_ID = 730

def get_cs2_player_stats(steam_id_64):
    """
    Pobiera surowe statystyki Counter-Strike 2 dla danego Steam ID 64.
    
    Args:
        steam_id_64 (str): 17-cyfrowe ID gracza Steam.
        
    Returns:
        dict or None: Słownik z danymi statystycznymi lub None w przypadku błędu.
    """
    if not STEAM_API_KEY:
        print("Błąd: STEAM_API_KEY nie został załadowany. Sprawdź plik .env i settings.py")
        return None
    # Endpoint do pobierania statystyk dla określonej gry
    base_url = "http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/"
    params = {
        'appid': CSGO_APP_ID,
        'key': STEAM_API_KEY,
        'steamid': steam_id_64,
        'format': 'json'
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()  # Sprawdza błędy http
        data = response.json()
        # Sprawdzanie struktury odpowiedzi
        if 'playerstats' not in data or 'stats' not in data['playerstats']:
            print(f"Błąd: Nie znaleziono statystyk CS2 dla Steam ID: {steam_id_64}. Profil może być prywatny.")
            return None
        # Zwracanie listy statystyk
        return data['playerstats']['stats']
    except requests.exceptions.HTTPError as e:
        print(f"Błąd HTTP ({response.status_code}) podczas pobierania danych: {e}")
        print("Upewnij się, że klucz API jest poprawny i profil Steam jest PUBLICZNY.")
        return None
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")
        return None
def map_raw_stats(raw_stats):
    """
    Mapuje surową listę statystyk z API na słownik z kluczami, 
    które pasują do naszego modelu Django, używając 0 dla brakujących pól.
    """
    # Tworzenie słownika {nazwa_statystyki: wartość}
    stats_dict = {item['name']: item['value'] for item in raw_stats}
    # Mapowanie na klucze modelu StatSession
    # .get(klucz, 0) - jeśli klucz nie istnieje, zwraca 0
    mapped_data = {
        'total_kills': stats_dict.get('total_kills', 0),
        'total_deaths': stats_dict.get('total_deaths', 0),
        'total_time_played': stats_dict.get('total_time_played', 0),
        'total_headshots': stats_dict.get('total_headshots', 0), 
    }
    return mapped_data

# TEST FUNKCJI
if __name__ == '__main__':
    TEST_ID = '76561198134553187' 
    stats = get_cs2_player_stats(TEST_ID)
    
    if stats:
        mapped_stats = map_raw_stats(stats)
        print("\n--- Zmapowane statystyki (Gotowe do zapisu w Django) ---")
        print(mapped_stats)
    else:
        print("Nie udało się pobrać statystyk.")