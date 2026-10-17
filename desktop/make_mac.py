# Builds the macOS apps from Windows. @electron/packager needs symlinks for macOS
# (admin-only on Windows), so this copies Electron's official macOS zip entry by entry,
# keeping its symlinks, renames it to SHADE.app and adds the game inside.
#   usage: python make_mac.py   (after `node build.js copy`, which also downloads Electron)
import os, plistlib, zipfile, glob

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.environ['LOCALAPPDATA'], 'electron', 'Cache')
OUT = os.path.join(HERE, '..', 'dist')
os.makedirs(OUT, exist_ok=True)

app_files = ['package.json', 'main.js'] + [
    os.path.relpath(p, HERE).replace(os.sep, '/')
    for p in glob.glob(os.path.join(HERE, 'game', '**', '*'), recursive=True) if os.path.isfile(p)]

for arch in ('arm64', 'x64'):
    src = glob.glob(os.path.join(CACHE, '*', f'electron-v33.2.1-darwin-{arch}.zip'))[0]
    dst = os.path.join(OUT, f'SHADE-mac-{arch}.zip')
    with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zo:
        for info in zi.infolist():
            name = info.filename
            if not name.startswith('Electron.app/') or name.endswith('Resources/default_app.asar'):
                continue  # skip Electron's licence files at the zip root and its demo app
            data = zi.read(info)
            info.filename = name.replace('Electron.app/', 'SHADE.app/', 1)
            if name == 'Electron.app/Contents/Info.plist':
                pl = plistlib.loads(data)
                pl.update(CFBundleName='SHADE', CFBundleDisplayName='SHADE', CFBundleIdentifier='com.teamshade.shade')
                data = plistlib.dumps(pl)
            zo.writestr(info, data)
        for f in app_files:
            zf = zipfile.ZipInfo('SHADE.app/Contents/Resources/app/' + f, date_time=(2026, 10, 18, 0, 0, 0))
            zf.create_system = 3; zf.external_attr = 0o100644 << 16; zf.compress_type = zipfile.ZIP_DEFLATED
            with open(os.path.join(HERE, f), 'rb') as fh:
                zo.writestr(zf, fh.read())
    print('built', dst, os.path.getsize(dst) // (1 << 20), 'MB')
