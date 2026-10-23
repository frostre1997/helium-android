<div align="center">
    <img src="resources/branding/app_icon/raw.png"
        title="Helium" alt="Helium logo" width="120" />
    <h1>Helium for Android</h1>
    <p>
        The browser built around privacy, consent, and comfort — now on Android.
    </p>
    <a href="https://helium.computer/">
        helium.computer
    </a>
</div>

> [!WARNING]
> **This is an unofficial, experimental community port.**
> It is not affiliated with or endorsed by the upstream Helium project.
> Builds are unstable and not ready for daily use. See [Known issues](#known-issues).

## About this repository

This repo is the **Android platform layer** for Helium. It does **not** contain
a browser engine or a vendored copy of Chromium.

Like every serious Chromium-based browser, Helium is built as a **patch stack
applied to a vanilla Chromium source tree**. This repository supplies only the
Android-specific pieces:

- `patches/` — Android-specific Quilt patches
- `flags.gn` — GN build flags for the Android target
- `pruning.list` — files removed from the final build
- build orchestration scripts that fetch Chromium and apply the layers

The source of truth for the build is [`patches/series`](patches/series).
If a patch isn't listed there, it isn't applied.

## How it's built

The build is a sequential pipeline. Each layer is applied on top of the last:

```
Chromium source
└─> upstream Helium patches   (imputnet/helium)
└─> Android patches     (this repo)
└─> GN + Ninja  ──> APK
```

1. **Fetch Chromium** via `depot_tools`:
```sh
fetch --nohooks android
```

2. Apply upstream Helium patches from imputnet/helium, in the order
   defined by its patches/series:
```
upstream-fixes → ungoogled-chromium → helium/core → helium/ui
```
3. Apply this repo's Android patches on top.
4. Configure GN with flags.gn plus Android args:
```gn
target_os  = "android"
target_cpu = "arm64"
is_debug   = false
   ```
5. Build with Ninja and sign the resulting APK.

We deliberately do not vendor Chromium or submodule the source tree.
Chromium's gclient owns its dependency graph via DEPS files, and any
foreign Git structure breaks that. This is the same reason Helium, Titanium,
Bromite, and ungoogled-chromium all ship patches instead of forks.

## Downloads

There are no official releases yet. To get an APK you must build it yourself
(see Development) or use a community build at your own risk.

> [!NOTE]
Extension support exists but is fragile on Android. You must enable
"Desktop site" before visiting the Chrome Web Store, and the OS may
kill extension background pages at any time.

Related repos

Upstream Helium

- Helium core — patch stack, tooling, services
- Helium for macOS
- Helium for Linux
- Helium for Windows

Android community

- Titanium Browser — the
  original community Android port, formerly android-helium-browser
- This repo — Android platform
  layer used by this port

Build dependencies

- depot_tools
- Chromium Android build instructions

Development

macOS and Linux are the upstream development platforms. Android builds are
tested on Ubuntu (latest LTS) with a standard Chromium Android toolchain
(depot_tools, Android SDK, NDK, JDK).

Requirements

- ~500 GB free disk space (source + build artifacts)
- 16 GB RAM minimum, 32 GB recommended
- Python 3, quilt, and the Chromium Android system dependencies

Quick start

```sh
# 1. Toolchain
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH="$PWD/depot_tools:$PATH"

# 2. Chromium
mkdir helium-android && cd helium-android
fetch --nohooks android
gclient runhooks

# 3. Patches
#    Apply upstream Helium patches, then this repo's Android patches,
#    using the series files as the source of truth.

# 4. Build
gn gen out/arm64 --args="$(cat flags.gn) target_os=\"android\" target_cpu=\"arm64\""
ninja -C out/arm64 chrome_public_apk
```

Exact patch application order and signing steps live in the build scripts in
this repo. Do not edit files in patches/ directly — make changes in the
Chromium tree, then refresh the patches with quilt refresh.

Known issues

- White-screen crash after several days of use; may require clearing app
  data to recover.
- No DRM support — streaming services such as Netflix will not work.
- WebRTC leaks are prevented by default, which can break apps like Discord
  Voice. Adjust the policy in settings if needed.
- Extension background pages are frequently killed by the OS, breaking
  ad-blockers such as uBlock Origin.
- Not a security substitute for running GrapheneOS with Vanadium. App-level
  hardening cannot replace kernel- and memory-level protections.

Contributing

Before contributing, please read upstream's
CONTRIBUTING.md.
For this port, please open issues with:

- the Chromium version you built against
- the exact patch that failed (if the build broke)
- device model and Android version

Credits

The Chromium project

The Chromium Project is at the core of Helium,
making it possible in the first place.

Helium

Helium by
imput provides the patch stack, tooling, and
services this port builds on.

ungoogled-chromium

Helium originally branched off
ungoogled-chromium.
Special thanks to everyone behind that project.

Other Chromium projects

Helium includes patches from other open source Chromium projects:

- Inox patchset
- Debian
- Bromite
- Iridium Browser
- Brave

All patches are sorted by vendor in the patches/ directory.

Android port

- Titanium Browser by
  jqssun — the reference community Android port
- Vanadium by GrapheneOS — hardened
  Chromium patches (note: GPLv2, see licensing caveat below)

License

All code, patches, modified portions of imported code or patches, and any other
content unique to this port is licensed under GPL-3.0. See
LICENSE.

Any content imported from other projects retains its original license. For
example, unmodified code imported from ungoogled-chromium remains under its
BSD 3-Clause license.

> [!IMPORTANT]
Upstream Helium is GPL-3.0 and the Chromium base is BSD-3-Clause, but
Vanadium is GPLv2, which is not compatible with GPLv3. If you combine
Vanadium patches with Helium patches in a single distribution, review the
licensing implications first. Pure Helium patches (without Vanadium) avoid
this conflict.