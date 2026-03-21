using Toybox.WatchUi as Ui;
using Toybox.System as Sys;

class bjj_garminApp extends Ui.Widget {

    var counter = 0;

    function initialize() {
        Ui.Widget.initialize();
        Sys.println("BJJ Widget initialized");
    }

    // Define layout size (needed for simulator)
    function onLayout(dc) {
        // Fill the widget with white background
        dc.clear();
        // Draw static text
        dc.drawText(10, 20, Ui.FONT_LARGE, "BJJ Rolls");
        dc.drawText(10, 50, Ui.FONT_MEDIUM, "Count: " + counter);
    }

    // Called when the widget updates (dynamic changes)
    function onUpdate(dc) {
        dc.clear();
        dc.drawText(10, 20, Ui.FONT_LARGE, "BJJ Rolls");
        dc.drawText(10, 50, Ui.FONT_MEDIUM, "Count: " + counter);
    }

    // Increment counter when user presses main button
    function onButton(event) {
        if (event == Ui.BUTTON_DOWN) {
            counter += 1;
            Sys.println("Counter: " + counter);
            Ui.req
