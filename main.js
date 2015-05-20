var app = require('app');
var BrowserWindow = require('browser-window');
var os = require('os');
var exiting = false;
var log_to_file = false;
var logfile = '';

if(log_to_file){
    var fs = require('fs');
    var util = require('util');
    var log_file = fs.createWriteStream(logfile, {flags : 'w'});
    var log_stdout = process.stdout;

    console.log = function(d) { //
      log_file.write(util.format(d) + '\n');
      log_stdout.write(util.format(d) + '\n');
    };
}

// Report crashes to our server.
require('crash-reporter').start();

if(os.platform() === 'win32'){
    var serverBinary = __dirname + '\\dist\\machinery\\machinery.exe';
}else{
    var serverBinary = __dirname + '/machinery/machinery';
}

console.log("platform is " + os.platform());
console.log("spawning binary in " + serverBinary);
var spawn = require('child_process').spawn, server = spawn(serverBinary);

server.on('close', function (code) {
    console.log('server process exited with code ' + code);
    //respawn if not exiting
    if (!exiting) {
        console.log("restarting server ...");
        server = spawn(serverBinary);
    }
});

server.stdout.on('data', function (data) {
  console.log('server: ' + data);
});

server.stderr.on('data', function (data) {
  console.log('server: ' + data);
});

var mainWindow = null;

// Quit when all windows are closed.
app.on('window-all-closed', function () {
    if (process.platform != 'darwin') {
        app.quit();
    }
});

app.on('ready', function () {
    // Create the browser window.
    mainWindow = new BrowserWindow({
        width: 1100,
        height: 800,
        'min-width': 995,
        'min-height': 600,
        "node-integration": false
    });

    // load main.html
    mainWindow.loadUrl('file://' + __dirname + '/main.html');

    // Emitted when the window is closed.
    mainWindow.on('closed', function () {
        exiting = true;
        mainWindow = null;
        server.kill();
    });
});