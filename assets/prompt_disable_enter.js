// const messageBuffer = [];
// const ws = new WebSocket("ws://127.0.0.1:5000/ws");

// ws.onmessage = function(event) {
//     const message = event.data;
//     messageBuffer.push(message);  // Buffer incoming messages
// };

// // Function to retrieve buffered messages for Dash
// window.dash_clientside = Object.assign({}, window.dash_clientside, {
//     clientside: {
//         getBufferedMessages: function() {
//             console.log("Fetching buffered messages...");
//             const bufferedMessages = messageBuffer.splice(0);  // Retrieve and clear buffer
//             console.log(bufferedMessages)
//             return bufferedMessages.join(" ");  // Combine into a single string
//         }
//     }
// });
// const ws = new WebSocket("ws://localhost:5000/ws");

// ws.onmessage = function(event) {
//     const message = event.data;
//     console.log("Message received from WebSocket:", message);  // Log received message
//     // You can also display this message directly in the UI here if necessary.
// };

// $("textarea").keydown(function(e){
//     console.log("key pressed");
//     // Enter was pressed without shift key
//     if (e.keyCode == 13 && !e.shiftKey)
//     {
//         // prevent default behavior
//         e.preventDefault();
//     }
//     });

var textarea = document.getElementById('prompt-text');
document.addEventListener('keypress', function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        return false;
    }

})