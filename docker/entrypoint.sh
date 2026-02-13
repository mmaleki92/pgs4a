#!/bin/bash
set -e

# Check if the Android SDK and Ant are installed
check_sdk() {
    if [ ! -d "android-sdk/tools" ] || [ ! -d "apache-ant" ]; then
        echo ""
        echo "=== ERROR: Android SDK is not installed. ==="
        echo ""
        echo "The SDK was not downloaded during the Docker image build."
        echo "This usually happens when the image is built without internet access."
        echo ""
        echo "To fix this, run:"
        echo "  docker run -it pgs4a installsdk"
        echo ""
        echo "Then rebuild the image with:"
        echo "  docker build -t pgs4a ."
        echo ""
        exit 1
    fi
}

COMMAND="${1:-help}"
shift || true

case "$COMMAND" in
    installsdk)
        if [ -d "android-sdk/cmdline-tools" ] && [ -d "apache-ant" ]; then
            echo "=== Android SDK and Ant are already installed (built into the image) ==="
        else
            echo "=== Installing Android SDK (non-interactive) ==="
            export PGS4A_NO_TERMS=1
            yes | python android.py installsdk || true

            if [ -d "android-sdk/cmdline-tools" ]; then
                echo "=== SDK installation complete ==="
            else
                echo "=== WARNING: SDK installation may have failed. Check the output above for errors. ==="
                exit 1
            fi
        fi
        ;;

    configure)
        if [ -z "$1" ]; then
            echo "Usage: docker run pgs4a configure <app_directory>"
            echo "Example: docker run -v \$(pwd)/mygame:/opt/pgs4a/mygame pgs4a configure mygame"
            exit 1
        fi
        python android.py configure "$@"
        ;;

    setconfig)
        python android.py setconfig "$@"
        ;;

    build)
        if [ -z "$1" ] || [ -z "$2" ]; then
            echo "Usage: docker run pgs4a build <app_directory> <release|debug>"
            echo "Example: docker run -v \$(pwd)/mygame:/opt/pgs4a/mygame pgs4a build mygame release"
            exit 1
        fi

        check_sdk

        APP_DIR="$1"

        # Auto-configure if .android.json is missing
        if [ ! -f "$APP_DIR/.android.json" ]; then
            echo "=== No .android.json found in $APP_DIR. Auto-configuring with defaults... ==="
            APP_DIR="${APP_DIR%/}"
            APP_NAME="${APP_DIR##*/}"
            PACKAGE_NAME=$(echo "$APP_NAME" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]_')
            python android.py setconfig "$APP_DIR" name "$APP_NAME"
            python android.py setconfig "$APP_DIR" icon_name "$APP_NAME"
            python android.py setconfig "$APP_DIR" package "org.pgs4a.$PACKAGE_NAME"
            python android.py setconfig "$APP_DIR" version "1.0"
            python android.py setconfig "$APP_DIR" numeric_version "100"
            python android.py setconfig "$APP_DIR" orientation "sensorLandscape"
            echo "=== Auto-configuration complete. Run 'configure' for custom settings. ==="
        fi

        python android.py build "$@"

        # Copy APK to output directory if it exists
        if ls bin/*.apk 1>/dev/null 2>&1; then
            if cp bin/*.apk /output/ 2>/dev/null; then
                echo "=== APK(s) copied to /output ==="
                ls -la /output/*.apk 2>/dev/null || true
            else
                echo "=== WARNING: Could not copy APK to /output. Check directory permissions. ==="
            fi
        fi
        ;;

    buildapk)
        # Full pipeline: configure + build a game directory into an APK
        APP_DIR="${1:-examples/example_app}"
        shift || true

        check_sdk

        echo "=== Building APK for: $APP_DIR ==="

        # Check if already configured
        if [ ! -f "$APP_DIR/.android.json" ]; then
            echo "=== Configuring $APP_DIR with defaults ==="
            APP_DIR="${APP_DIR%/}"
            APP_NAME="${APP_DIR##*/}"
            PACKAGE_NAME=$(echo "$APP_NAME" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]_')
            python android.py setconfig "$APP_DIR" name "$APP_NAME"
            python android.py setconfig "$APP_DIR" icon_name "$APP_NAME"
            python android.py setconfig "$APP_DIR" package "org.pgs4a.$PACKAGE_NAME"
            python android.py setconfig "$APP_DIR" version "1.0"
            python android.py setconfig "$APP_DIR" numeric_version "100"
            python android.py setconfig "$APP_DIR" orientation "sensorLandscape"
        fi

        echo "=== Building release APK ==="
        python android.py build "$APP_DIR" release || true

        # Copy APK to output
        if ls bin/*.apk 1>/dev/null 2>&1; then
            if cp bin/*.apk /output/ 2>/dev/null; then
                echo "=== SUCCESS: APK(s) copied to /output ==="
                ls -la /output/*.apk 2>/dev/null || true
            else
                echo "=== APK built but could not copy to /output ==="
                ls -la bin/*.apk 2>/dev/null || true
            fi
        else
            echo "=== WARNING: No APK found. Build may have failed. ==="
            exit 1
        fi
        ;;

    test)
        python android.py test
        ;;

    pytest)
        pip3 install pytest 2>/dev/null || true
        python -m pytest tests/ -v
        ;;

    shell)
        exec /bin/bash
        ;;

    help)
        echo ""
        echo "pgs4a - Pygame Subset for Android (Docker)"
        echo "==========================================="
        echo ""
        echo "The SDK, cmdline-tools, Ant, Python 3, and pygame are pre-installed in this image."
        echo ""
        echo "Usage: docker run [options] pgs4a <command> [arguments]"
        echo ""
        echo "Commands:"
        echo "  buildapk [app_dir]       Full pipeline: configure + build APK (default: examples/example_app)"
        echo "  build <app_dir> <mode>   Build an APK (mode: release or debug)"
        echo "  configure <app_dir>      Configure an app interactively"
        echo "  setconfig <dir> <k> <v>  Set a config value non-interactively"
        echo "  installsdk               Re-install the Android SDK"
        echo "  test                     Run a quick self-test"
        echo "  pytest                   Run the test suite"
        echo "  shell                    Open a bash shell in the container"
        echo "  help                     Show this help message"
        echo ""
        echo "Examples:"
        echo "  # Build the example app APK:"
        echo "  docker run -v \$(pwd)/output:/output pgs4a buildapk"
        echo ""
        echo "  # Build your own game:"
        echo "  docker run -v \$(pwd)/mygame:/opt/pgs4a/mygame -v \$(pwd)/output:/output pgs4a buildapk mygame"
        echo ""
        echo "  # Interactive configure + build:"
        echo "  docker run -it -v \$(pwd)/mygame:/opt/pgs4a/mygame pgs4a configure mygame"
        echo "  docker run -v \$(pwd)/mygame:/opt/pgs4a/mygame -v \$(pwd)/output:/output pgs4a build mygame release"
        echo ""
        echo "  # Open a shell:"
        echo "  docker run -it pgs4a shell"
        echo ""
        ;;

    *)
        # Pass through to android.py for any other command
        python android.py "$COMMAND" "$@"
        ;;
esac
