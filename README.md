# netatmo-indicator
Ubuntu debian deployment of a Menubar indicator for the Netatmo Weather Station

## Settings
The indicator stores its settings in .netatmo-indicator-preferences.yaml, with an additional credentials file
for netatmo. The credentials' file is reference with the <credentials_file> tag in .netatmo-indicator-preferences.yaml

One may edit the credentials directly in the Menu.

If desired, one may edit the .netatmo-indicator-preferences.yaml and add a dictionary of aliases to substitute the
names displayed, i.e.:

```
aliases:
  Living: In
  Outdoor: Out
  Bedroom: Bed
```

## Screenshots
![alt text](screenshots/netatmo-indicator-screenshot.png)
