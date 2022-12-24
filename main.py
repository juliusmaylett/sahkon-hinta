from nordpool import getCurrentSpotPrice

hinta = getCurrentSpotPrice()
print(f"Sähkön hinta Suomessa nyt {hinta} €/MWh")