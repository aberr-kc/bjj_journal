// BJJTestApp.mc - Simple Connect IQ app to test real data
using Toybox.Application;
using Toybox.WatchUi;
using Toybox.Communications;
using Toybox.Activity;
using Toybox.Time;

class BJJTestApp extends Application.AppBase {
    function initialize() {
        AppBase.initialize();
    }

    function getInitialView() {
        return [new BJJTestView(), new BJJTestDelegate()];
    }
}

class BJJTestView extends WatchUi.View {
    function initialize() {
        View.initialize();
    }

    function onUpdate(dc) {
        dc.setColor(Graphics.COLOR_WHITE, Graphics.COLOR_BLACK);
        dc.clear();
        dc.drawText(
            dc.getWidth() / 2,
            dc.getHeight() / 2 - 30,
            Graphics.FONT_MEDIUM,
            "BJJ Journal Test",
            Graphics.TEXT_JUSTIFY_CENTER
        );
        
        dc.drawText(
            dc.getWidth() / 2,
            dc.getHeight() / 2,
            Graphics.FONT_SMALL,
            "Press START to send",
            Graphics.TEXT_JUSTIFY_CENTER
        );
        
        dc.drawText(
            dc.getWidth() / 2,
            dc.getHeight() / 2 + 30,
            Graphics.FONT_SMALL,
            "activity data",
            Graphics.TEXT_JUSTIFY_CENTER
        );
    }
}

class BJJTestDelegate extends WatchUi.BehaviorDelegate {
    function initialize() {
        BehaviorDelegate.initialize();
    }

    function onSelect() {
        sendTestActivity();
        return true;
    }
    
    function sendTestActivity() {
        var activityInfo = Activity.getActivityInfo();
        var currentTime = Time.now();
        
        // Create test data with real activity info if available
        var testData = {
            "activity_name" => "BJJ Training - Connect IQ",
            "duration_minutes" => 75,
            "calories" => 650,
            "avg_heart_rate" => 145,
            "max_heart_rate" => 178,
            "timestamp" => Time.Gregorian.info(currentTime, Time.FORMAT_SHORT).year + "-" +
                          Time.Gregorian.info(currentTime, Time.FORMAT_SHORT).month.format("%02d") + "-" +
                          Time.Gregorian.info(currentTime, Time.FORMAT_SHORT).day.format("%02d") + "T" +
                          Time.Gregorian.info(currentTime, Time.FORMAT_SHORT).hour.format("%02d") + ":" +
                          Time.Gregorian.info(currentTime, Time.FORMAT_SHORT).min.format("%02d") + ":00Z",
            "activity_id" => "connectiq_" + currentTime.value()
        };
        
        // Use real data if available
        if (activityInfo != null) {
            if (activityInfo.elapsedTime != null) {
                testData["duration_minutes"] = activityInfo.elapsedTime / 60000;
            }
            if (activityInfo.calories != null) {
                testData["calories"] = activityInfo.calories;
            }
            if (activityInfo.averageHeartRate != null) {
                testData["avg_heart_rate"] = activityInfo.averageHeartRate;
            }
            if (activityInfo.maxHeartRate != null) {
                testData["max_heart_rate"] = activityInfo.maxHeartRate;
            }
        }
        
        // Update this IP to your computer's IP
        var url = "http://192.168.1.100:8000/garmin/activity";
        
        Communications.makeWebRequest(
            url,
            testData,
            {
                :method => Communications.HTTP_REQUEST_METHOD_POST,
                :headers => {"Content-Type" => Communications.REQUEST_CONTENT_TYPE_JSON}
            },
            method(:onActivitySent)
        );
    }
    
    function onActivitySent(responseCode, data) {
        if (responseCode == 200) {
            System.println("Activity sent successfully!");
        } else {
            System.println("Failed to send activity: " + responseCode);
        }
    }
}