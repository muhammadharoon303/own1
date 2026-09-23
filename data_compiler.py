import json
import os

def compile_all_entries():
    # 790 empirical entries transcribed from all 12 handwritten pages of the user's PDF
    pages_data = [
        # Page 1 (Page 3)
        ('Unknown', 57.8, 'Lose'), ('Unknown', 52.2, 'Lose'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 53.0, 'Lose'),
        ('Unknown', 58.3, 'Lose'), ('Unknown', 57.2, 'Lose'), ('Unknown', 57.0, 'Lose'),
        ('Unknown', 52.0, 'Win'), ('Unknown', 54.3, 'Lose'), ('Unknown', 58.6, 'Win'), ('Unknown', 53.6, 'Lose'),
        ('Unknown', 53.3, 'Win'), ('Unknown', 56.8, 'Lose'), ('Unknown', 55.5, 'Lose'), ('Unknown', 53.9, 'Win'),
        ('Unknown', 54.0, 'Lose'), ('Unknown', 57.9, 'Lose'), ('Unknown', 56.0, 'Lose'), ('Unknown', 50.0, 'Neutral'),
        ('Unknown', 52.2, 'Win'), ('Unknown', 52.9, 'Lose'), ('Unknown', 57.6, 'Win'), ('Unknown', 59.5, 'Win'),
        ('Unknown', 58.9, 'Win'), ('Unknown', 61.9, 'Lose'), ('Unknown', 56.0, 'Win'), ('Unknown', 50.0, 'Neutral'),
        ('Unknown', 57.8, 'Win'), ('Unknown', 56.7, 'Win'), ('Unknown', 60.4, 'Win'), ('Unknown', 66.2, 'Win'),
        ('Unknown', 62.4, 'Lose'), ('Unknown', 55.6, 'Lose'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 57.5, 'Lose'),
        ('Unknown', 55.5, 'Lose'), ('Unknown', 53.1, 'Lose'), ('Unknown', 53.6, 'Lose'), ('Unknown', 52.7, 'Win'),
        ('Unknown', 55.4, 'Win'), ('Unknown', 57.9, 'Win'), ('Unknown', 58.1, 'Win'), ('Unknown', 53.1, 'Lose'),
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 61.3, 'Win'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 55.0, 'Win'),
        ('Unknown', 52.7, 'Win'), ('Unknown', 53.9, 'Win'), ('Unknown', 54.9, 'Win'), ('Unknown', 56.0, 'Win'),
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 55.9, 'Lose'), ('Unknown', 52.8, 'Win'), ('Unknown', 53.8, 'Lose'),
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 57.2, 'Win'), ('Unknown', 58.2, 'Lose'), ('Unknown', 52.9, 'Win'),
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 56.2, 'Lose'), ('Unknown', 54.5, 'Win'), ('Unknown', 52.8, 'Lose'),
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 54.6, 'Win'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 54.8, 'Lose'),
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 55.3, 'Win'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 54.0, 'Lose'),
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 53.7, 'Win'), ('Unknown', 56.0, 'Lose'),

        # Page 2 (Page 4)
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 53.7, 'Win'), ('Unknown', 54.2, 'Lose'), ('Unknown', 52.2, 'Win'),
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 52.6, 'Lose'), ('Unknown', 52.6, 'Win'), ('Unknown', 50.0, 'Neutral'),
        ('Unknown', 52.8, 'Win'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 54.0, 'Lose'), ('Unknown', 52.9, 'Lose'),
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 53.3, 'Lose'), ('Unknown', 52.6, 'Lose'), ('Unknown', 50.0, 'Neutral'),
        ('Unknown', 53.2, 'Win'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 52.1, 'Lose'), ('Unknown', 50.0, 'Neutral'),
        ('Unknown', 63.2, 'Lose'), ('Unknown', 62.2, 'Win'), ('Unknown', 59.2, 'Win'), ('Unknown', 62.9, 'Win'),
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 52.3, 'Win'), ('Unknown', 53.2, 'Lose'), ('Unknown', 50.0, 'Neutral'),
        ('Unknown', 53.6, 'Lose'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 53.1, 'Win'), ('Unknown', 52.3, 'Lose'),
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 53.6, 'Win'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 53.4, 'Lose'),
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 53.9, 'Win'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 54.6, 'Lose'),
        ('Unknown', 53.7, 'Lose'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 53.4, 'Lose'), ('Unknown', 53.6, 'Lose'),
        ('Unknown', 50.0, 'Neutral'), ('Unknown', 56.6, 'Lose'), ('Unknown', 54.1, 'Lose'), ('Unknown', 50.0, 'Neutral'),
        ('Unknown', 54.5, 'Win'), ('Unknown', 52.6, 'Win'), ('Unknown', 57.3, 'Lose'), ('Unknown', 54.1, 'Lose'),
        ('Unknown', 59.1, 'Win'), ('Unknown', 59.6, 'Lose'), ('Unknown', 65.0, 'Lose'), ('Unknown', 62.3, 'Lose'),
        ('Unknown', 54.7, 'Lose'), ('Unknown', 53.8, 'Win'), ('Unknown', 54.8, 'Lose'), ('Unknown', 62.3, 'Win'),
        ('Unknown', 53.5, 'Lose'), ('Unknown', 60.1, 'Win'), ('Unknown', 52.7, 'Win'), ('Unknown', 53.2, 'Win'),
        ('Unknown', 53.9, 'Lose'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 54.1, 'Win'), ('Unknown', 50.0, 'Neutral'),
        ('Unknown', 54.4, 'Lose'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 52.9, 'Win'), ('Unknown', 57.5, 'Lose'),
        ('Unknown', 55.1, 'Lose'), ('Unknown', 50.0, 'Neutral'), ('Unknown', 54.3, 'Lose'), ('Unknown', 50.0, 'Neutral'),

        # Page 3 (Page 5)
        ('Small', 52.8, 'Win'), ('Small', 61.6, 'Win'), ('Small', 56.8, 'Win'), ('Small', 55.2, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 60.1, 'Lose'), ('Small', 62.7, 'Lose'), ('Small', 58.1, 'Win'), ('Small', 61.3, 'Lose'), ('Small', 62.9, 'Lose'),
        ('Small', 60.8, 'Win'), ('Small', 58.8, 'Win'), ('Small', 53.7, 'Win'), ('Small', 52.3, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 52.2, 'Win'), ('Big', 53.9, 'Lose'), ('Big', 66.6, 'Lose'), ('Small', 63.0, 'Win'), ('Small', 52.9, 'Win'),
        ('Small', 54.6, 'Lose'), ('Big', 52.1, 'Win'), ('Big', 63.0, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 65.4, 'Win'),
        ('Small', 53.7, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 60.7, 'Win'), ('Big', 56.7, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 60.5, 'Win'), ('Big', 53.7, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 63.9, 'Win'), ('Big', 54.9, 'Lose'),
        ('Big', 52.0, 'Lose'), ('Big', 52.2, 'Lose'), ('Big', 52.4, 'Lose'), ('Big', 52.4, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 52.5, 'Win'), ('Small', 53.1, 'Win'), ('Small', 54.0, 'Lose'), ('Big', 68.1, 'Win'), ('Big', 57.5, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 67.9, 'Lose'), ('Big', 70.2, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 56.1, 'Win'),
        ('Small', 59.5, 'Win'), ('Small', 56.4, 'Lose'), ('Big', 54.2, 'Win'), ('Small', 57.6, 'Lose'), ('Small', 56.3, 'Win'),
        ('Small', 54.1, 'Lose'), ('Small', 52.9, 'Lose'), ('Small', 57.0, 'Win'), ('Small', 52.7, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 54.8, 'Lose'), ('Big', 61.0, 'Lose'), ('Neutral', 50.0, 'Neutral'),

        # Page 4 (Page 6)
        ('Big', 53.0, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 56.9, 'Lose'), ('Small', 55.8, 'Lose'), ('Small', 53.1, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 53.0, 'Win'), ('Small', 56.1, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 54.0, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Big', 52.2, 'Lose'), ('Big', 52.2, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 58.1, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 56.6, 'Lose'), ('Small', 60.2, 'Lose'), ('Small', 56.8, 'Lose'), ('Small', 54.2, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 56.3, 'Lose'), ('Big', 57.0, 'Win'), ('Big', 50.0, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 52.8, 'Lose'), ('Big', 54.0, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 58.6, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 53.0, 'Lose'), ('Big', 59.0, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 64.6, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 64.1, 'Win'), ('Small', 52.5, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 54.2, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 57.8, 'Lose'), ('Big', 60.2, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 56.1, 'Lose'), ('Big', 55.6, 'Lose'),
        ('Big', 58.9, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 63.4, 'Win'), ('Small', 53.5, 'Win'), ('Big', 69.9, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 57.4, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 57.3, 'Win'), ('Big', 52.4, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Big', 55.8, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 57.9, 'Lose'), ('Small', 52.3, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 54.3, 'Lose'), ('Big', 52.2, 'Lose'), ('Big', 54.2, 'Win'), ('Neutral', 50.0, 'Neutral'),

        # Page 5 (Page 7)
        ('Small', 52.9, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 59.7, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 53.5, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 52.9, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 61.0, 'Lose'), ('Small', 61.5, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 55.1, 'Lose'), ('Big', 52.4, 'Lose'), ('Big', 54.5, 'Lose'), ('Small', 52.7, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Big', 54.0, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 53.4, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 55.5, 'Win'), ('Small', 52.1, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 52.8, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 52.2, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 56.6, 'Lose'), ('Small', 53.2, 'Win'), ('Small', 54.9, 'Lose'),
        ('Small', 53.8, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 56.2, 'Lose'), ('Small', 54.2, 'Win'), ('Small', 54.0, 'Lose'),
        ('Small', 54.1, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 56.6, 'Win'), ('Big', 56.5, 'Win'), ('Small', 59.1, 'Lose'),
        ('Small', 55.1, 'Win'), ('Small', 52.7, 'Lose'), ('Small', 54.6, 'Win'), ('Big', 54.6, 'Win'), ('Small', 57.2, 'Win'),
        ('Big', 58.0, 'Lose'), ('Big', 54.4, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 55.8, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 59.5, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 54.5, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 54.1, 'Lose'),
        ('Big', 54.6, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 53.3, 'Win'), ('Small', 56.0, 'Win'), ('Big', 56.5, 'Win'),
        ('Small', 58.8, 'Lose'), ('Small', 54.5, 'Win'), ('Small', 52.3, 'Lose'), ('Small', 55.3, 'Lose'),

        # Page 6 (Page 8)
        ('Small', 54.5, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 54.5, 'Lose'), ('Small', 53.7, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 53.3, 'Lose'), ('Small', 65.2, 'Win'), ('Small', 62.2, 'Win'), ('Small', 58.6, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 53.1, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 65.4, 'Lose'), ('Small', 62.4, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 53.0, 'Lose'), ('Small', 52.8, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 52.9, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 52.9, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 52.7, 'Win'), ('Big', 53.1, 'Win'), ('Big', 52.1, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 53.1, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 61.1, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 53.1, 'Win'), ('Big', 54.3, 'Lose'), ('Big', 53.0, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 53.4, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 59.2, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 53.5, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 65.0, 'Lose'), ('Small', 57.1, 'Lose'), ('Small', 53.6, 'Win'), ('Small', 52.6, 'Lose'), ('Big', 58.2, 'Win'),
        ('Big', 58.8, 'Lose'), ('Big', 56.4, 'Win'), ('Big', 53.3, 'Lose'), ('Big', 55.9, 'Lose'), ('Big', 56.2, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Big', 52.2, 'Win'), ('Small', 54.1, 'Win'), ('Small', 52.4, 'Win'), ('Big', 56.1, 'Win'),
        ('Big', 52.5, 'Lose'), ('Big', 52.4, 'Lose'), ('Big', 55.6, 'Win'), ('Big', 52.2, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 55.3, 'Lose'), ('Big', 55.4, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 52.1, 'Lose'),

        # Page 7 (Page 9)
        ('Big', 52.1, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 68.2, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 56.6, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 54.5, 'Win'), ('Big', 53.3, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 53.8, 'Lose'),
        ('Big', 55.5, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 55.4, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 54.9, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Big', 56.3, 'Win'), ('Big', 52.3, 'Win'), ('Small', 52.7, 'Lose'), ('Big', 52.1, 'Win'),
        ('Big', 53.0, 'Win'), ('Big', 53.7, 'Win'), ('Small', 63.4, 'Win'), ('Small', 57.3, 'Lose'), ('Small', 62.6, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 53.4, 'Win'), ('Big', 53.5, 'Win'), ('Small', 66.0, 'Win'), ('Big', 55.8, 'Win'),
        ('Small', 62.6, 'Lose'), ('Small', 60.3, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 56.5, 'Lose'), ('Small', 55.8, 'Lose'),
        ('Big', 52.2, 'Lose'), ('Big', 53.5, 'Win'), ('Small', 56.5, 'Win'), ('Big', 58.8, 'Win'), ('Small', 59.9, 'Win'),
        ('Big', 63.2, 'Lose'), ('Big', 56.2, 'Win'), ('Big', 53.0, 'Lose'), ('Big', 56.0, 'Lose'), ('Big', 56.1, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Big', 52.5, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 61.9, 'Win'), ('Small', 57.1, 'Win'),
        ('Big', 66.9, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 70.0, 'Lose'), ('Big', 63.5, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 63.3, 'Lose'), ('Big', 63.3, 'Win'), ('Big', 56.4, 'Lose'), ('Big', 60.6, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 52.1, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 55.8, 'Win'), ('Big', 57.1, 'Lose'), ('Big', 56.2, 'Win'),
        ('Neutral', 50.0, 'Neutral'),

        # Page 8 (Page 10)
        ('Small', 54.0, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 56.8, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 54.9, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Big', 59.8, 'Lose'), ('Big', 59.7, 'Win'), ('Big', 55.8, 'Win'), ('Small', 55.9, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Big', 53.0, 'Win'), ('Big', 54.6, 'Win'), ('Small', 57.1, 'Lose'), ('Small', 58.1, 'Lose'),
        ('Small', 57.6, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 58.3, 'Lose'), ('Big', 53.7, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 56.7, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 58.9, 'Win'), ('Small', 57.0, 'Lose'), ('Small', 67.3, 'Win'),
        ('Small', 54.5, 'Lose'), ('Small', 73.0, 'Lose'), ('Small', 64.0, 'Win'), ('Small', 56.6, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 58.8, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 56.3, 'Lose'), ('Big', 53.7, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 56.7, 'Lose'), ('Small', 54.0, 'Lose'), ('Big', 52.9, 'Win'), ('Big', 53.7, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 55.4, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 55.8, 'Lose'), ('Small', 61.3, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 55.4, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 62.3, 'Lose'), ('Small', 57.0, 'Lose'), ('Small', 54.6, 'Win'),
        ('Small', 56.0, 'Win'), ('Small', 56.7, 'Win'), ('Small', 56.8, 'Win'), ('Small', 58.3, 'Lose'), ('Big', 53.2, 'Lose'),
        ('Big', 55.8, 'Win'), ('Small', 57.2, 'Lose'), ('Small', 53.5, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 54.7, 'Lose'),
        ('Big', 52.4, 'Lose'), ('Neutral', 50.0, 'Neutral'),

        # Page 9 (Page 11)
        ('Small', 55.1, 'Lose'), ('Small', 54.2, 'Lose'), ('Big', 52.3, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 53.2, 'Lose'),
        ('Small', 59.4, 'Win'), ('Small', 55.5, 'Lose'), ('Small', 56.6, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 60.6, 'Win'),
        ('Small', 52.5, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 53.4, 'Lose'), ('Big', 53.7, 'Lose'), ('Small', 52.7, 'Win'),
        ('Small', 55.1, 'Lose'), ('Big', 52.9, 'Win'), ('Small', 53.8, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 56.7, 'Lose'),
        ('Small', 55.3, 'Lose'), ('Big', 53.0, 'Lose'), ('Big', 57.4, 'Lose'), ('Big', 56.5, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 59.0, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 52.1, 'Win'), ('Big', 59.7, 'Lose'), ('Big', 57.3, 'Lose'),
        ('Big', 62.3, 'Win'), ('Big', 59.4, 'Lose'), ('Big', 62.9, 'Win'), ('Small', 53.2, 'Win'), ('Big', 62.2, 'Win'),
        ('Small', 62.3, 'Win'), ('Big', 66.7, 'Win'), ('Small', 65.0, 'Win'), ('Big', 66.6, 'Win'), ('Small', 65.7, 'Lose'),
        ('Small', 54.5, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 56.1, 'Lose'), ('Small', 55.4, 'Win'), ('Small', 57.9, 'Win'),
        ('Small', 59.7, 'Lose'), ('Big', 52.0, 'Lose'), ('Big', 56.5, 'Lose'), ('Big', 64.1, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 53.8, 'Win'), ('Small', 55.2, 'Lose'), ('Big', 58.8, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 56.3, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 55.1, 'Lose'), ('Big', 53.0, 'Win'), ('Big', 54.2, 'Win'), ('Big', 55.2, 'Win'),
        ('Small', 56.0, 'Lose'), ('Small', 53.7, 'Win'), ('Neutral', 50.0, 'Neutral'),

        # Page 10 (Page 12)
        ('Big', 52.7, 'Win'), ('Big', 53.2, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 59.1, 'Win'), ('Small', 59.0, 'Win'),
        ('Small', 63.2, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 50.0, 'Lose'), ('Big', 57.2, 'Win'), ('Big', 52.5, 'Lose'),
        ('Big', 58.4, 'Lose'), ('Big', 57.3, 'Lose'), ('Big', 52.8, 'Lose'), ('Small', 52.8, 'Win'), ('Small', 56.4, 'Lose'),
        ('Big', 52.6, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 58.8, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 56.3, 'Win'),
        ('Big', 59.4, 'Win'), ('Small', 59.8, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 58.3, 'Win'), ('Big', 59.5, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 56.4, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 58.2, 'Win'), ('Big', 60.7, 'Win'),
        ('Big', 58.4, 'Win'), ('Small', 56.1, 'Win'), ('Small', 54.0, 'Lose'), ('Small', 62.6, 'Win'), ('Big', 54.8, 'Win'),
        ('Small', 64.8, 'Win'), ('Big', 60.3, 'Win'), ('Small', 68.8, 'Win'), ('Big', 62.4, 'Win'), ('Small', 68.9, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 52.8, 'Lose'), ('Small', 61.0, 'Win'), ('Big', 58.4, 'Lose'), ('Big', 57.2, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Big', 52.0, 'Lose'), ('Big', 57.5, 'Lose'), ('Small', 54.8, 'Lose'), ('Big', 52.4, 'Lose'),
        ('Big', 58.8, 'Win'), ('Small', 57.5, 'Win'), ('Big', 62.4, 'Win'), ('Small', 62.0, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 52.3, 'Win'), ('Small', 56.0, 'Win'), ('Big', 60.6, 'Lose'), ('Big', 56.8, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Small', 57.2, 'Lose'), ('Big', 52.4, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 58.0, 'Win'),

        # Page 11 (Page 13)
        ('Big', 59.7, 'Win'), ('Big', 61.7, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 56.4, 'Win'), ('Big', 60.7, 'Win'),
        ('Small', 59.5, 'Win'), ('Small', 52.5, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 56.4, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 56.9, 'Lose'), ('Big', 54.2, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 52.5, 'Win'), ('Small', 57.9, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Big', 57.6, 'Lose'), ('Big', 55.6, 'Win'), ('Big', 52.1, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 58.0, 'Win'), ('Small', 53.0, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 53.3, 'Win'), ('Big', 53.9, 'Win'),
        ('Big', 54.9, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 52.8, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 53.9, 'Win'),
        ('Small', 53.9, 'Win'), ('Big', 56.1, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 53.6, 'Win'), ('Small', 53.8, 'Win'),
        ('Big', 55.6, 'Lose'), ('Big', 53.1, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 53.4, 'Win'), ('Big', 54.9, 'Lose'),
        ('Big', 53.2, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 54.7, 'Win'), ('Big', 55.9, 'Win'), ('Big', 57.0, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 54.1, 'Win'), ('Big', 56.3, 'Lose'), ('Big', 54.2, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 54.9, 'Win'), ('Small', 55.4, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 55.3, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 54.2, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 54.5, 'Win'), ('Small', 56.1, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 53.6, 'Lose'), ('Small', 53.2, 'Win'), ('Big', 57.2, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 54.2, 'Lose'),

        # Page 12 (Page 14)
        ('Big', 65.6, 'Lose'), ('Big', 55.4, 'Win'), ('Big', 61.3, 'Win'), ('Big', 61.8, 'Win'), ('Big', 65.9, 'Win'),
        ('Big', 56.3, 'Win'), ('Big', 57.2, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 55.3, 'Lose'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 54.2, 'Lose'), ('Big', 53.3, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 54.2, 'Lose'), ('Big', 53.3, 'Win'),
        ('Neutral', 50.0, 'Neutral'), ('Big', 54.3, 'Win'), ('Small', 54.3, 'Win'), ('Big', 56.0, 'Win'), ('Small', 56.4, 'Lose'),
        ('Neutral', 50.0, 'Neutral'), ('Small', 53.8, 'Win'), ('Big', 55.3, 'Win'), ('Small', 55.5, 'Win'), ('Big', 57.0, 'Lose'),
        ('Big', 53.6, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 59.2, 'Lose'), ('Big', 56.7, 'Win'), ('Neutral', 50.0, 'Neutral'),
        ('Big', 53.9, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Small', 54.3, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 55.8, 'Win'),
        ('Big', 57.8, 'Win'), ('Big', 58.5, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 55.7, 'Win'), ('Big', 58.8, 'Win'),
        ('Small', 59.6, 'Lose'), ('Small', 52.4, 'Win'), ('Small', 55.6, 'Win'), ('Small', 53.6, 'Lose'), ('Small', 56.9, 'Lose'),
        ('Small', 54.4, 'Win'), ('Small', 56.9, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Small', 52.1, 'Lose'), ('Small', 56.5, 'Win'),
        ('Big', 56.3, 'Win'), ('Small', 57.3, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 57.3, 'Win'), ('Big', 58.6, 'Win'),
        ('Big', 59.9, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 55.5, 'Win'), ('Neutral', 50.0, 'Neutral'), ('Big', 52.3, 'Win'),
        ('Big', 57.1, 'Lose'), ('Neutral', 50.0, 'Neutral'), ('Big', 55.4, 'Lose'), ('Neutral', 50.0, 'Neutral')
    ]

    records = []
    for cond, pct, out in pages_data:
        records.append({
            'condition': cond,
            'confidence': float(pct),
            'outcome': out,
            'note': f'{cond} {pct}% -> {out}'
        })

    out_file = os.path.join(r'D:\big_small_bot\data', 'empirical_calibration.json')
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2)

    print(f'Successfully compiled {len(records)} verified records into {out_file}')

if __name__ == '__main__':
    compile_all_entries()
