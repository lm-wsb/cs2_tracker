from django.db import models
from django.contrib.auth.models import User

# Model Gracza - przechowuje podstawowe informacje i Steam ID
class Player(models.Model):
    # Relacja Jeden do Jednego z domyślnym modelem User
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # 17-cyfrowe ID wymagane przez Steam API
    steam_id_64 = models.CharField(max_length=17, unique=True, verbose_name="Steam ID 64")
    
    # Ostatnia aktualizacja profilu
    last_updated = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Gracz: {self.user.username} ({self.steam_id_64})"

# Model Sesji Statystyk - przechowuje historyczne statystyki z konkretnej daty
class StatSession(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    
    # Data i czas pobrania tych statystyk
    date_fetched = models.DateTimeField(auto_now_add=True)
    
    # Kluczowe statystyki z API
    total_kills = models.IntegerField(default=0)
    total_deaths = models.IntegerField(default=0)
    total_time_played = models.IntegerField(default=0) 
    
    # POLO DLA HS%
    total_headshots = models.IntegerField(default=0) # Potrzebne do HS%
    
    # Właściwości Obliczeniowe
    @property
    def kd_ratio(self):
        """Oblicza K/D ratio (Zabójstwa / Śmierci)."""
        if self.total_deaths > 0:
            # Wartość zaokrąglona do dwóch miejsc po przecinku
            return round(self.total_kills / self.total_deaths, 2) 
        # Zabezpieczenie przed dzieleniem przez zeroS
        return self.total_kills

    @property
    def headshot_percentage(self):
        """Oblicza procent headshotów (HS%) ((Headshots / Kills) * 100)."""
        if self.total_kills > 0:
            return round((self.total_headshots / self.total_kills) * 100, 2)
        return 0.0

    def __str__(self):
        return f"Statystyki z {self.date_fetched.strftime('%Y-%m-%d')} dla {self.player.user.username}"