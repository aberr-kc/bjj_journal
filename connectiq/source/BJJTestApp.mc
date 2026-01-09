using Toybox.Application;
using Toybox.WatchUi;
using Toybox.Communications;
using Toybox.Activity;
using Toybox.Time;
using Toybox.System;

class BJJTestApp extends Application.AppBase {
    function initialize() {
        AppBase.initialize();
    }

    function onStart(state as Dictionary?) as Void {
    }

    function onStop(state as Dictionary?) as Void {
    }

    function getInitialView() as Array<Views or InputDelegates>? {
        return [new BJJTestView(), new BJJTestDelegate()];
    }
}

class BJJTestView extends WatchUi.View {
    function initialize() {
        View.initialize();
    }

    function onLayout(dc as Dc) as Void {
        // Simple layout without resource files for now
    }

    function onUpdate(dc as Dc) as Void {
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_BLACK);
        dc.clear();
        
        var width = dc.getWidth();
        var height = dc.getHeight();
        
        dc.drawText(
            width / 2,
            height / 2 - 40,
            Graphics.FONT_MEDIUM,
            "BJJ Journal",
            Graphics.TEXT_JUSTIFY_CENTER
        );
        
        dc.drawText(
            width / 2,
            height / 2 - 10,
            Graphics.FONT_SMALL,
            "Test App",
            Graphics.TEXT_JUSTIFY_CENTER
        );
        
        dc.drawText(
            width / 2,
            height / 2 + 20,
            Graphics.FONT_TINY,
            "START = Send Data",
            Graphics.TEXT_JUSTIFY_CENTER
        );
        
        dc.drawText(
            width / 2,
            height / 2 + 40,
            Graphics.FONT_TINY,
            "BACK = Exit",
            Graphics.TEXT_JUSTIFY_CENTER
        );
    }
}

class BJJTestDelegate extends WatchUi.BehaviorDelegate {
    function initialize() {
        BehaviorDelegate.initialize();
    }

    function onSelect() as Boolean {
        sendTestActivity();
        return true;
    }
    
    function onBack() as Boolean {
        System.exit();
        return true;
    }
    
    function sendTestActivity() as Void {
        var activityInfo = Activity.getActivityInfo();
        var currentTime = Time.now();
        var timeInfo = Time.Gregorian.info(currentTime, Time.FORMAT_SHORT);
        
        // Format timestamp as ISO string
        var timestamp = timeInfo.year + "-" + 
                       timeInfo.month.format("%02d") + "-" + 
                       timeInfo.day.format("%02d") + "T" + 
                       timeInfo.hour.format("%02d") + ":" + 
                       timeInfo.min.format("%02d") + ":" + 
                       timeInfo.sec.format("%02d") + "Z";
        
        // Create test data - update with real values if activity is running
        var testData = {
            "activity_name" => "BJJ Training - Connect IQ Test",
            "duration_minutes" => 75,
            "calories" => 650,
            "avg_heart_rate" => 145,
            "max_heart_rate" => 178,
            "timestamp" => timestamp,
            "activity_id" => "connectiq_" + currentTime.value()
        };
        
        // Use real activity data if available
        if (activityInfo != null) {
            if (activityInfo.elapsedTime != null && activityInfo.elapsedTime > 0) {
                testData["duration_minutes"] = (activityInfo.elapsedTime / 60000).toNumber();
            }
            if (activityInfo.calories != null && activityInfo.calories > 0) {
                testData["calories"] = activityInfo.calories.toNumber();
            }
            if (activityInfo.averageHeartRate != null && activityInfo.averageHeartRate > 0) {
                testData["avg_heart_rate"] = activityInfo.averageHeartRate.toNumber();
            }
            if (activityInfo.maxHeartRate != null && activityInfo.maxHeartRate > 0) {
                testData["max_heart_rate"] = activityInfo.maxHeartRate.toNumber();
            }
        }
        
        // Update this to your computer's IP address
        var url = "http://192.168.68.61:8000/garmin/activity";
        
        System.println("Sending activity data to: " + url);
        
        Communications.makeWebRequest(
            url,
            testData,
            {
                :method => Communications.HTTP_REQUEST_METHOD_POST,
                :headers => {
                    "Content-Type" => Communications.REQUEST_CONTENT_TYPE_JSON
                }
            },
            method(:onActivitySent)
        );
        
        // Show sending status
        WatchUi.pushView(
            new WatchUi.Confirmation("Sending to Journal..."),
            new WatchUi.ConfirmationDelegate(),
            WatchUi.SLIDE_IMMEDIATE
        );
    }
    
    function onActivitySent(responseCode as Number, data as Dictionary?) as Void {
        System.println("Response code: " + responseCode);
        
        if (responseCode == 200) {
            System.println("Activity sent successfully!");
            WatchUi.pushView(
                new WatchUi.Confirmation("Sent Successfully!"),
                new WatchUi.ConfirmationDelegate(),
                WatchUi.SLIDE_IMMEDIATE
            );
        } else {
            System.println("Failed to send activity. Code: " + responseCode);
            WatchUi.pushView(
                new WatchUi.Confirmation("Send Failed: " + responseCode),
                new WatchUi.ConfirmationDelegate(),
                WatchUi.SLIDE_IMMEDIATE
            );
        }
    }
}

function getApp() as BJJTestApp {
    return Application.getApp() as BJJTestApp;
}