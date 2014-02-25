var url_api = "http://192.168.0.14:8000/";

var lastCommand;
var lastObject;
function sendCommand(command, object) {
    var api = url_api + command;
    lastCommand = command;

    $.ajax({
        statusCode: { 200: function() {
                setMetadata();
                if (lastCommand == "pause") {
                    $("#ctrl_pause").prop("disabled", true);
                } else if (lastCommand == "resume") {
                    $("#ctrl_pause").prop("disabled", false);
                }
            }
        },
        dataType: "json",
        url: api,
    });
}