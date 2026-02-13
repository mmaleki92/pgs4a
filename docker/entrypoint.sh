#!/bin/bash
set -e

COMMAND="${1:-help}"
shift || true

case "$COMMAND" in
    installsdk)
        echo "=== Installing Android SDK (non-interactive) ==="
        # Accept terms automatically and skip interactive prompts
        export PGS4A_NO_TERMS=1

        # Run installsdk but feed 'yes' answers to all prompts.
        # We use '|| true' because 'yes' returns a non-zero exit code
        # when its output pipe is closed by the completed process.
        yes | python android.py installsdk || true

        # Verify that the SDK was actually installed
        if [ -d "android-sdk/cmdline-tools" ]; then
            echo "=== SDK installation complete ==="
        else
            echo "=== WARNING: SDK installation may have failed. Check the output above for errors. ==="
            exit 1
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

    build)
        if [ -z "$1" ] || [ -z "$2" ]; then
            echo "Usage: docker run pgs4a build <app_directory> <release|debug>"
            echo "Example: docker run -v \$(pwd)/mygame:/opt/pgs4a/mygame pgs4a build mygame release"
            exit 1
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

    test)
        python android.py test
        ;;

    shell)
        exec /bin/bash
        ;;

    help)
        echo ""
        echo "pgs4a - Pygame Subset for Android (Docker)"
        echo "==========================================="
        echo ""
        echo "Usage: docker run [options] pgs4a <command> [arguments]"
        echo ""
        echo "Commands:"
        echo "  installsdk              Install the Android SDK (non-interactive)"
        echo "  configure <app_dir>     Configure an app for building"
        echo "  build <app_dir> <mode>  Build an APK (mode: release or debug)"
        echo "  test                    Run a quick test"
        echo "  shell                   Open a bash shell in the container"
        echo "  help                    Show this help message"
        echo ""
        echo "Examples:"
        echo "  # Build the image:"
        echo "  docker build -t pgs4a ."
        echo ""
        echo "  # Install SDK (saves to a volume for reuse):"
        echo "  docker run -v pgs4a-sdk:/opt/pgs4a/android-sdk -v pgs4a-ant:/opt/pgs4a/apache-ant pgs4a installsdk"
        echo ""
        echo "  # Configure your game:"
        echo "  docker run -it -v pgs4a-sdk:/opt/pgs4a/android-sdk -v \$(pwd)/mygame:/opt/pgs4a/mygame pgs4a configure mygame"
        echo ""
        echo "  # Build your game:"
        echo "  docker run -v pgs4a-sdk:/opt/pgs4a/android-sdk -v pgs4a-ant:/opt/pgs4a/apache-ant \\"
        echo "    -v \$(pwd)/mygame:/opt/pgs4a/mygame -v \$(pwd)/output:/output pgs4a build mygame release"
        echo ""
        echo "  # Or use docker-compose (recommended):"
        echo "  docker compose run pgs4a installsdk"
        echo "  docker compose run pgs4a configure examples/example_app"
        echo "  docker compose run pgs4a build examples/example_app release"
        echo ""
        ;;

    *)
        # Pass through to android.py for any other command
        python android.py "$COMMAND" "$@"
        ;;
esac
