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

## Deployment [Self Note]
This is a self note. You do not need this for normal indicator usage.
##### Check if key already available
`gpg --list-secret-keys`

##### Generate key if not available
```
gpg --gen-key
gpg -a --output ~/.gnupg/mihaigalos.gpg --export 'Mihai Galos'
gpg --import ~/.gnupg/mihaigalos.gpg
```

##### Debian Package Generation
`dpkg-buildpackage -b -pgpg -kmihaigalos@gmail.com`

##### Prepare for upload to Launchpad
###### Prerequisites:
* Ubuntu One account active
* gpg key used to sign the debian uploaded to Ubuntu Keyserver:
 - `gpg --list-keys`
 - `gpg  --keyserver hkp://keyserver.ubuntu.com:11371 --send-keys <KEY>`)
* OpenPGP keys displays the key

###### Upload:
`dput ppa:mihaigalos/ppa netatmo-indicator_0.1-1_amd64.changes`
