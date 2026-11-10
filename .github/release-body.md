## Prompt Saver v1.5.0

Changes since v1.4.4:

- libraries now live in the app's own data folder, with a dropdown to switch between them
- the last library reopens automatically on launch
- New Library button
- Import Library button for libraries saved outside the app; the original file stays where it is
- automatic .bak snapshot beside the library on every save
- warning prompt when closing with unsaved changes
- copy button confirms inline with a green "Copied"
- more space around the delete button
- cards now record seed, scheduler and size alongside steps, CFG and shift

### Upgrading

If you are coming from 1.4.4, use **Import Library** to bring your existing library into the app. Your old file is left untouched where it is.

### About the interface

This is not a native Mac or Windows app. It is built with Tauri, so the interface is rendered by the system web view. That is deliberate: native builds for two platforms drift apart quickly and you end up with an app that looks like two different apps. A web view keeps it identical on both. The trade-off is that it does not look or feel native, which is a conscious choice rather than an oversight.
