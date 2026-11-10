# Prompt Saver

A lightweight prompt library manager built for the Invoke community.

Library size & stress testing

Prompt Saver has been stress-tested using large libraries to understand real-world limits when images are embedded.

In testing, a library containing 1,250 prompts with images, a 138MB library file size loaded in around 5 seconds on the test machine A M1 Macbook Air. Load time will vary depending on user hardware, available memory, and disk speed.

* FOR MAC USERS ONLY ONCE MOVED TO THE APPLICATIONS FOLDER BUT BEFORE FIRST USE, RUN THIS COMMAND IN TERMINAL xattr -dr com.apple.quarantine "/Applications/Prompt Saver.app"
  THIS IS A ONE TIME OPERATION

## Windows SmartScreen Warning (First Launch)

When you first run **Prompt Saver** on Windows, you may see a message saying **“Windows protected your PC”**.

This is **normal behavior** for unsigned or newly built desktop applications and does **not** mean the app is unsafe.

### Why this happens

Microsoft Defender SmartScreen may block apps that:

* Are not code-signed yet
* Are newly built or not widely downloaded
* Are distributed outside the Microsoft Store

### How to run the app anyway

1. On the **Windows protected your PC** screen, click **More info**
2. Click **Run anyway**
3. The app will start normally

Windows usually remembers this choice, so you should not see the warning again for the same build.

### Is it safe?

* Prompt Saver runs entirely locally
* It does not install system services
* It does not require administrator access
* It only accesses files and dialogs you explicitly allow

If you built the app yourself or downloaded it from the official project source, this warning is expected and safe to bypass.

### For developers

To permanently remove this warning for end users, the application must be code-signed with a trusted Windows certificate or distributed via the Microsoft Store.

## Why the interface is a web view

Prompt Saver is built with Tauri, so the interface is drawn by the system web view rather than by native macOS or Windows widgets.

That was deliberate. Native builds for two platforms drift apart fast — different spacing, different control sizes, different idioms — and you end up with an app that feels like two different apps. A web view keeps the layout identical on both, so the buttons are where you left them whichever machine you are on.

The trade-off is that it does not inherit native look and feel. That is a conscious choice, not an oversight.
