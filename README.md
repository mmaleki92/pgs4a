# pgs4a
A slightly modified version of the deprecated Pygame Subset for Android. It was easy way to port your Pygame (v1.9.1 on Python 2.7) to your android devices. It builds an APK using the android SDK and installs it on your device.
Pgs4a was made by Tom Rothamel, Patrick Dawson and others, using Kivy's *python-for-android* packager to make Pygame games run on android.
He developed pgs4a until 2013 until he moved on with his other projects.
Meanwhile, I made a couple of edits to pgs4a to keep it working nicely in the constantly evolving android environment. Note that this repo depends on outdated versions of libraries, like Python 2.7. Python 3 is not supported; app bundles for google play are also not supported. For up-to-date libraries you may want to look into different projects like [python-for-android](https://github.com/kivy/python-for-android) instead.

# Changelog

### 0.9.6 (last release by Tom)
* This release patches Python to work with .apk files distributed through the Amazon App Store, which are subtly different from standard apk files.
* This release fixes support for pre-2.3 Android devices

### 0.9.7 (my changes)
* immersive full screen mode (api 19+)
* removed all permissions (storage, wakelock)
* two-finger multitouch implementation
* target SDK of project can be configured by user
* added full keyboard and mouse (api 21+) support
* autobackup via google, for specified files (api 23+, see */res/xml*)
* resizeable activity (api 24+)
* adaptive icon (api 26+)
* additional 64-bit libraries, with 16kB page size memory support
* can build APKs that run on devices up to API 35 (android 12), although no app bundles are created (so no uploading to google play)

The shared libraries in the *libs* folder are built by the [rapt](https://github.com/startgridsrc/rapt) toolchain. This toolchain actually builds an entire pgs4a distribution, like this repository, but it's not as up to date as this repository. The shared libraries (.so files) of the other rapt repository are simply copied into this (newer) repository. 

# Instructions

You can set up pgs4a either using **Docker** (recommended — no manual dependency installation needed) or **manually** on your host system.

---

## Option A: Docker (Recommended)

Docker handles all dependencies (JDK, Android SDK, Ant) automatically. You don't need to install anything except Docker itself.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running
- [Docker Compose](https://docs.docker.com/compose/install/) (included with Docker Desktop)

### Quick Start

**1. Build the Docker image:**

```bash
docker build -t pgs4a .
```

**2. Install the Android SDK (one-time setup):**

This downloads and installs the Android SDK, Ant, and build tools. They are stored in Docker volumes so you only need to do this once.

```bash
docker compose run pgs4a installsdk
```

**3. Configure your app:**

Using the included example app:
```bash
docker compose run pgs4a configure examples/example_app
```

Or mount your own game directory:
```bash
docker run -it \
  -v pgs4a-sdk:/opt/pgs4a/android-sdk \
  -v pgs4a-ant:/opt/pgs4a/apache-ant \
  -v $(pwd)/mygame:/opt/pgs4a/mygame \
  pgs4a configure mygame
```

You will be asked several questions about your app (name, package, version, etc.).

**4. Build the APK:**

```bash
docker compose run pgs4a build examples/example_app release
```

The built APK will be copied to the `./output` directory.

For your own game:
```bash
docker run \
  -v pgs4a-sdk:/opt/pgs4a/android-sdk \
  -v pgs4a-ant:/opt/pgs4a/apache-ant \
  -v $(pwd)/mygame:/opt/pgs4a/mygame \
  -v $(pwd)/output:/output \
  pgs4a build mygame release
```

**5. Install the APK on your device:**

Connect your phone via USB (with USB debugging enabled), then:
```bash
adb install output/YourApp-release.apk
```

### Docker Commands Reference

| Command | Description |
|---------|-------------|
| `docker compose run pgs4a installsdk` | Install Android SDK and tools |
| `docker compose run pgs4a configure <dir>` | Configure an app for building |
| `docker compose run pgs4a build <dir> release` | Build a release APK |
| `docker compose run pgs4a build <dir> debug` | Build a debug APK |
| `docker compose run pgs4a test` | Run a quick self-test |
| `docker compose run pgs4a shell` | Open a bash shell in the container |
| `docker compose run pgs4a help` | Show available commands |

### Docker Tips

- The SDK is stored in Docker volumes (`pgs4a-sdk` and `pgs4a-ant`), so it persists across container runs.
- To reset the SDK, remove the volumes: `docker volume rm pgs4a-sdk pgs4a-ant`
- To mount a custom game, add `-v $(pwd)/mygame:/opt/pgs4a/mygame` to your `docker run` command or edit `docker-compose.yml`.
- The `configure` command requires interactive input, so use `docker compose run` (not `docker compose up`).
- Built APKs are saved to the `./output` directory when using docker-compose.

---

## Option B: Manual Setup

1. Make sure a recent Java JDK and JRE are installed. This project is tested with OpenJDK 23.0.1, both on Windows and Linux platforms. MacOS may work but is not tested.
1. Clone this repository, open a terminal and run:
   
   ```
   python ./android.py installsdk
   ```
   This automatically downloads and extracts:
   - Ant
   - Android commandline-tools (which downloads 'platforms;android-33')
   - Android tools (older version which downloads 'build-tools-29.0.3', 'platform-tools' and 'extra-android-m2repository')
    - You will be prompted to agree with the terms and conditions of the SDK packages, requiring you to press *yes* or *y* many times. Then it copies 'support-v4-19.1.0.jar' from extra-android-m2repository into the `libs` folder. And to make that Ant build without errors with newer Java versions, two files are edited automatically: 'build.xml' and 'dx.bat'. And finally, the script will help you create a random key to sign APKs (you need to create a key in case you haven't a key already). A key is required to install an APK on a device.
If any of this fails, look into `buildlib/install_sdk.py`.
1. In this readme, the folder *examples/example_app* is used to create a minimal app to demonstrate that the build process is working. To build your own game, just add a new folder with your game files, and use the path of your folder instead.
1. Run
   ```
   python ./android.py configure examples/example_app
   ```
   It asks several questions and creates a Json file which is added to the game folder, containing several properties of your app, like the name and version. You can run this command again any time you changed something about your game.
1. Connect your phone to your PC via USB. Make sure USB debugging is enabled (see developer options on your phone) as well as USB file transfer.
1. Run
   ```
   python ./android.py build examples/example_app release
   ```
   An APK should be created and installed on your phone. The app will start immediately, in theory!
1. If the app installs, but crashes immediately, run
   ```
   python ./android.py logcat
   ```
    to find out why. This command shows Python errors only. To see other possible errors, navigate to *android-sdk/platform-tools* and run `./adb logcat`. Open your app, and when it crashes, press *Ctrl + C* to stop logging, and look for errors. For example, your project folder has to contain a file called *main.py*, so you may have to rename one of your files to that, and try again. Or you may need to manually change *java.target* to 1.8 in the file *\android-sdk\tools\ant\build.xml* to avoid javac warnings/errors.

The original instructions can be found [here](https://github.com/startgridsrc/rapt/blob/master/doc/android-packaging.rst).
These are the original instructions which are old but detailed, and most of it is probably still fine. You'll find handy info on using the android module in Python, for example to make your game handle the back button, and detect app switching (so you know when to call your savegame function).

# License
The Pygame Subset for Android is licensed under the GNU Lesser General Public License. To the best of our knowledge, Pygame, SDL, and all other dependences are licensed under compatible licenses.

The Pygame Subset for Android is by:

Tom Rothamel

Patrick Dawson

It integrates code from an number of projects, including:

* [Python-for-android](https://github.com/kivy/python-for-android)
* [Pygame](https://www.pygame.org/news)
* [SDL (including Pelya's Android port)](https://github.com/pelya/commandergenius)
* [Python](https://www.python.org/)
* [Jtar](https://github.com/kamranzafar/jtar)
* Jinja2
* Colorama
