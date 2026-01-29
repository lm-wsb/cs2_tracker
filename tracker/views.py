from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Player, StatSession
from .steam_api import get_cs2_player_stats, map_raw_stats
from .llm_api import generate_performance_report

# Funkcja do ręcznego wyzwalania pobierania i zapisywania statystyk
@login_required
def update_stats_view(request):
    try:
        player = request.user.player
    except Player.DoesNotExist:
        return render(request, 'tracker/error.html', {'message': 'Brak przypisanego profilu Steam.'})
    # Pobieranie surowych danych
    raw_stats = get_cs2_player_stats(player.steam_id_64)
    
    if not raw_stats:
        # Pokaże błąd, jeśli API zawiodło
        return render(request, 'tracker/error.html', {'message': 'Błąd: Nie udało się pobrać danych z API.'})
    # Mapowanie danych
    mapped_data = map_raw_stats(raw_stats)
    # Zapisywanie nowej sesji do bazy
    try:
        StatSession.objects.create(
            player=player,
            total_kills=mapped_data['total_kills'],
            total_deaths=mapped_data['total_deaths'],
            total_time_played=mapped_data['total_time_played'],
            total_headshots=mapped_data['total_headshots'],
        )
        # Aktualizpwanie czasu w modelu Player
        player.last_updated = timezone.now()
        player.save()
        return redirect('tracker:dashboard') 
    except Exception as e:
        return render(request, 'tracker/error.html', {'message': f'Błąd zapisu do bazy danych: {e}'})

# Widok na dashboard
@login_required
def dashboard_view(request):
    try:
        player = request.user.player
        # Pobieranie wszystkich statystyk najstarsza-najnowsza
        all_sessions = StatSession.objects.filter(player=player).order_by('date_fetched')
        # Przygotowanie danych dla wykresu (Chart.js)
        labels = []  # Daty
        kd_data = [] # Wartości K/D Ratio
        for session in all_sessions:
            # Formatowanie daty do wyświetlenia na osi X
            labels.append(session.date_fetched.strftime("%Y-%m-%d %H:%M"))
            # Pobieranie obliczonej właściwość K/D
            kd_data.append(session.kd_ratio) 
        # Najnowsza sesja dla wyświetlenia w panelu
        last_session = all_sessions.last()
    except Player.DoesNotExist:
        last_session = None
        labels = []
        kd_data = []
        # Przekazywanie danych w formacie JSON, aby wkleić je do JavaScriptu
    context = {
        'last_session': last_session,
        'kd_labels': labels,
        'kd_data': kd_data,
    }
    return render(request, 'tracker/dashboard.html', context)

@login_required
def generate_report_view(request):
    try:
        player = request.user.player
        # Pobieranie ostatnich 5 sesji do analizy trendu
        recent_sessions = StatSession.objects.filter(player=player).order_by('-date_fetched')[:5]
        if not recent_sessions:
            return render(request, 'tracker/error.html', {'message': 'Brak wystarczających danych do analizy (potrzebna co najmniej jedna sesja).'})
        last_session = recent_sessions.first()
        history_data = [s.kd_ratio for s in reversed(recent_sessions)] # Odwracamy kolejność do analizy trendu
        # Generowanie raportu przez LLM
        report = generate_performance_report(
            player_username=request.user.username,
            last_session=last_session,
            history_data=history_data
        )
        return render(request, 'tracker/report.html', {'report': report})
        
    except Player.DoesNotExist:
        return render(request, 'tracker/error.html', {'message': 'Brak przypisanego profilu Steam.'})
    except Exception as e:
        return render(request, 'tracker/error.html', {'message': f'Ogólny błąd generowania raportu: {e}'})