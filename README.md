# ESP GUI Loader

Manual for building a PyInstaller application.
## Build

Run `docker buildx build --platform linux/amd64 -t mwojcik/pyinstaller-win:latest .` in root repo directory.
To build the app, run `docker run --platform linux/amd64 -v $(pwd):/src/ mwojcik/pyinstaller-win` in `src/`.