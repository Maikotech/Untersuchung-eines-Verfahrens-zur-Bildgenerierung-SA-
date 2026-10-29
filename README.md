# Untersuchung eines Verfahrens zur Bildgenerierung (SA)

## -Tiefes Neuronales Netz (DNN) auf einem Edge Device 
### -ControlNet als DNN mit einer Stable Diffsuion Pipeline
### -Nachgeschalteter VAE zum entrauschen der Bilder im latenten Raum 
## -Minimalstudie zu einer Anpassung von Datentypen der Modellgewichte
## -Evaluierung von Rechenzeit, Speicherverbrauch und Bildqualität des Ouputs

## Vorgehen
### Mittels tegrastats und TOP Profiler implementieren 
### Zeitmessung in bestehende ML Pipeline integrieren
### Typecasting auf FP32, BF16
### Messung der Ähnlichkeitsmetriken mittles LPIPS, SSIM & CLIP Score
### Berechnung der Mittelwerte und Vergleich
### Resumee
