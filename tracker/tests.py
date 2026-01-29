from django.test import TestCase
from django.contrib.auth.models import User
from .models import Player, StatSession

class CS2TrackerTests(TestCase):
    def setUp(self):
        # Standardowy użytkownik Django
        self.user = User.objects.create_user(username="testuser", password="password123")
        # Profil Player
        self.player = Player.objects.create(
            user=self.user, 
            steam_id_64="76561198000000000"
        )
        # Sesja statystyk
        self.session = StatSession.objects.create(
            player=self.player,
            total_kills=100,
            total_deaths=50,
            total_headshots=40
        )

    def test_zero_deaths_kd_ratio(self):
        """Testuje czy system nie wywala się przy 0 zgonów (dzielenie przez zero)"""
        zero_deaths_session = StatSession.objects.create(
            player=self.player, 
            total_kills=10, 
            total_deaths=0, 
            total_headshots=5
        )
        # Powinno zwrócić wartość kills
        self.assertEqual(zero_deaths_session.kd_ratio, 10.0)

    def test_kd_ratio_calculation(self):
        """Testuje czy właściwość kd_ratio poprawnie oblicza stosunek K do D"""
        # Przy 100 kills i 50 deaths, KD powinno wynosić 2.0
        self.assertEqual(self.session.kd_ratio, 2.0)

    def test_headshot_percentage(self):
        """Testuje obliczanie procentu headshotów"""
        # Przy 100 kills i 40 headshots, HS% powinno wynosić 40.0
        self.assertEqual(self.session.headshot_percentage, 40.0)
