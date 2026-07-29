const WebSocket = require('ws');
const fs = require('fs');

// ---------------- UNITY SERVER ----------------
const unityServer = new WebSocket.Server({ port: 8080 });
console.log("Unity WebSocket server running on ws://localhost:8080");

let unitySocket = null;

unityServer.on('connection', ws => {
    console.log("Unity connected");
    unitySocket = ws;

    // Acknowledge Unity connection
    ws.send(JSON.stringify({ status: "connected_to_js_server" }));

    // Read JSON file and send to Unity
    const filePath = String.raw`jsons\First_Test_json.json`;

    fs.readFile(filePath, 'utf8', (err, jsonString) => {
        if (err) {
            console.error("Error reading JSON file:", err);
            ws.send(JSON.stringify({ error: "json_read_failed" }));
            return;
        }

        try {
            const data = JSON.parse(jsonString);
            ws.send(JSON.stringify({
                status: "json_sent",
                payload: data
            }));
            console.log("JSON data sent to Unity.");
        } catch (parseError) {
            console.error("Invalid JSON format:", parseError);
            ws.send(JSON.stringify({ error: "invalid_json_format" }));
        }
    });

    ws.on('close', () => {
        console.log("Unity disconnected");
        unitySocket = null;
    });
});

// ---------------- PYTHON SERVER ----------------
const pythonServer = new WebSocket.Server({ port: 8765 });
console.log("Python WebSocket server running on ws://localhost:8765");

pythonServer.on('connection', ws => {
    console.log("Python connected");

    // Acknowledge Python connection
    ws.send(JSON.stringify({ status: "connected_to_js_server" }));

    ws.on('message', (msg) => {
        console.log("Received from Python:", msg);

        // Forward Python JSON to Unity
        if (unitySocket && unitySocket.readyState === WebSocket.OPEN) {
            unitySocket.send(JSON.stringify({
                status: "forwarded_from_python",
                payload: JSON.parse(msg)
            }));
        } else {
            console.log("Unity not connected, cannot forward message.");
        }
    });

    ws.on('close', () => {
        console.log("Python disconnected");
    });
});
