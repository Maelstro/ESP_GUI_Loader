FROM debian:bullseye-slim
ENV DEBIAN_FRONTEND noninteractive

# Set up architecture & install required software
RUN dpkg --add-architecture i386
RUN apt-get update && apt-get install --no-install-recommends -y wine \
      wine32 \
      wine64 \
      libwine \
      libwine:i386 \
      fonts-wine \
      wget \
      python3-tk

RUN wget https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks /usr/local/bin/winetricks
RUN chmod +x /usr/local/bin/winetricks

# Wine settings
ENV WINEARCH wine64
ENV WINDEBUG fixme-all
ENV WINEPREFIX /wine

# PYPI repository location
ENV PYPI_URL=https://pypi.python.org/
# PYPI index location
ENV PYPI_INDEX_URL=https://pypi.python.org/simple

# Set up Python in Wine
RUN set -xe \
    && winetricks win10 \
    && for msi_file in echo core dev exe lib path pip tcltk tools; do \
        wget -nv "https://www.python.org/ftp/python/3.9.13/amd64/${msi_file}.msi"; \
        wine msiexec /i "${msi_file}.msi" /qb TARGETDIR=C:/Python39; \
        rm ${msi_file}.msi; \
    done \
    && cd /wine/drive_c/Python39 \
    && echo 'wine '\''C:\Python39\python.exe'\'' "$@"' > /usr/bin/python \
    && echo 'wine '\''C:\Python39\Scripts\easy_install.exe'\'' "$@"' > /usr/bin/easy_install \
    && echo 'wine '\''C:\Python39\Scripts\pip.exe'\'' "$@"' > /usr/bin/pip \
    && echo 'wine '\''C:\Python39\Scripts\pyinstaller.exe'\'' "$@"' > /usr/bin/pyinstaller \
    && echo 'wine '\''C:\Python39\Scripts\pyupdater.exe'\'' "$@"' > /usr/bin/pyupdater \
    && echo 'assoc .py=PythonScript' | wine cmd \
    && echo 'ftype PythonScript=c:\Python39\python.exe "%1" %*' | wine cmd \
    && while pgrep wineserver >/dev/null; do echo "Waiting for wineserver"; sleep 1; done \
    && chmod +x /usr/bin/python /usr/bin/easy_install /usr/bin/pip /usr/bin/pyinstaller /usr/bin/pyupdater \
    && (pip install -U pip || true) \
    && rm -rf /tmp/.wine-*

ENV W_DRIVE_C=/wine/drive_c
ENV W_WINDIR_UNIX="$W_DRIVE_C/windows"
ENV W_SYSTEM64_DLLS="$W_WINDIR_UNIX/system32"
ENV W_TMP="$W_DRIVE_C/windows/temp/_$0"

# install Microsoft Visual C++ Redistributable for Visual Studio 2017 dll files
RUN set -x \
    && rm -f "$W_TMP"/* \
    && wget -P "$W_TMP" https://download.visualstudio.microsoft.com/download/pr/11100230/15ccb3f02745c7b206ad10373cbca89b/VC_redist.x64.exe \
    && cabextract -q --directory="$W_TMP" "$W_TMP"/VC_redist.x64.exe \
    && cabextract -q --directory="$W_TMP" "$W_TMP/a10" \
    && cabextract -q --directory="$W_TMP" "$W_TMP/a11" \
    && cd "$W_TMP" \
    && rename 's/_/\-/g' *.dll \
    && cp "$W_TMP"/*.dll "$W_SYSTEM64_DLLS"/

RUN /usr/bin/pip install pyinstaller

# put the src folder inside wine
RUN mkdir /src/ && ln -s /src /wine/drive_c/src

WORKDIR /wine/drive_c/src/
RUN mkdir -p /wine/drive_c/tmp

COPY entrypoint-windows.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]