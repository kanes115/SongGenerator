Treść zadania 1. na laboratorium z Pythona:

# Programowanie w jezyku Python 2016/2017 zadanie 1

Uporczywe narkotyczne melodie potrafią czasem na długo przylgnąć do umysłu.
Napisz program, który generuje narkotyczne melodie. Program powinien generować różne melodie w zależności od tego, jakie użytkownik poda opcje. Użytkownik będzie tak długo modyfikował opcje programu aż wygenerowana melodia utkwi mu na stałe w głowie.

Melodie te powinny być generowane w postaci plików midi i zapisywane na dysku twardym, przy czym użytkownik powinien mieć możliwość podania lokalizacji. Obsługa karty dźwiękowej w celu odtworzenia wygenerowanej melodii nie jest konieczna. Można użyć dowolnej biblioteki do obslugi formatu midi, przykladowo https://pypi.python.org/pypi/miditime


Program ten powinien wykorzystywać następujące elementy:
 - klasy
 - funkcje
 - parsowanie argumentów linii poleceń za pomocą modułu argparse ze standardowej biblioteki
 - zewnętrzna biblioteka do obsługi formatu midi

Tresc zadania w Google Drive: https://goo.gl/dbfwo3

Termin oddania zadania: 3 kwietnia 2017, 20:00


-----------------------

Running a program:

./NarcoticMelodies path --start number_of_songs length_of_each_song X-dur

path is a path where you want your melodies to be stored (new folder is made)

--start means it is a first run of a program - creates new random songs in a scale X

and later, to mark output songs and generate new ones:

./NarcoticMelodies path generate mark0 mark1 ... mark n

mark should be in range of 0 to 10
