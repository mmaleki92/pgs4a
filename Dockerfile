FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${PATH}:/opt/pgs4a/android-sdk/cmdline-tools/latest/bin:/opt/pgs4a/android-sdk/platform-tools"
ENV PGS4A_NO_TERMS=1

# Install system dependencies: Python 3, JDK 17, build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    openjdk-17-jdk \
    wget \
    unzip \
    git \
    sed \
    && rm -rf /var/lib/apt/lists/*

# Set python3 as default
RUN ln -sf /usr/bin/python3 /usr/bin/python

# Install pygame and jinja2 (needed by the build system)
RUN pip3 install --no-cache-dir pygame jinja2

WORKDIR /opt/pgs4a

# Copy the project files
COPY . .

# Make scripts executable
RUN chmod +x docker/entrypoint.sh

# Install the Android SDK, Ant, and build tools (non-interactive)
# '|| true' is needed because 'yes' exits with non-zero when its pipe closes.
# If the download fails (e.g., no internet during build), the SDK can be
# installed later at runtime via: docker run pgs4a installsdk
RUN yes | python android.py installsdk || true

# Verify SDK installation
RUN test -d android-sdk/cmdline-tools && echo "cmdline-tools: OK" || echo "cmdline-tools: MISSING"
RUN test -d android-sdk/tools && echo "android tools: OK" || echo "android tools: MISSING"
RUN test -d apache-ant && echo "ant: OK" || echo "ant: MISSING"
RUN test -d android-sdk/platforms/android-33 && echo "platform android-33: OK" || echo "platform: MISSING"
RUN test -d android-sdk/build-tools && echo "build-tools: OK" || echo "build-tools: MISSING"
RUN python -c "import pygame; print('pygame ' + pygame.version.ver + ': OK')"

# Pre-configure the example app (non-interactive with defaults)
RUN python android.py setconfig examples/example_app name "ExampleApp" && \
    python android.py setconfig examples/example_app icon_name "ExampleApp" && \
    python android.py setconfig examples/example_app package "org.pgs4a.example" && \
    python android.py setconfig examples/example_app version "1.0" && \
    python android.py setconfig examples/example_app numeric_version "100" && \
    python android.py setconfig examples/example_app orientation "sensorLandscape"

# Build the example app APK (may fail if SDK download was blocked; users can rebuild at runtime)
RUN python android.py build examples/example_app release || true

# Verify the APK was built
RUN ls -la bin/*.apk 2>/dev/null && echo "=== APK BUILD SUCCESS ===" || echo "=== APK not found in bin/ ==="

# Create output directory and copy APK
RUN mkdir -p /output && cp bin/*.apk /output/ 2>/dev/null || true

ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["help"]
