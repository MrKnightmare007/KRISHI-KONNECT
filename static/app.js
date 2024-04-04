class Chatbox {
    constructor() {
        this.args = {
            openButton: document.querySelector('.chatbox__button'), // Adjust the selector here
            chatbox: document.querySelector('.chatbox__support'), // Adjust the selector here
            sendButton: document.querySelector('.chatbox__send--footer'), // Adjust the selector here
        };

        this.state = false;
        this.messages = [];
    }

    display() {
        const { openButton, chatbox, sendButton } = this.args;

        openButton.addEventListener('click', () => this.toggleState(chatbox));
        sendButton.addEventListener('click', () => this.onSendButton(chatbox));

        const node = chatbox.querySelector('input');
        node.addEventListener("keyup", ({ key }) => {
            if (key === "Enter") {
                this.onSendButton(chatbox);
            }
        });
    }

    toggleState(Chatbox) {
        this.state = !this.state;

        if (this.state) {
            Chatbox.classList.add('chatbox--active');
        } else {
            Chatbox.classList.remove('chatbox--active');
        }
    }

    onSendButton(Chatbox) {
        var textfield = Chatbox.querySelector('input');
        let text = textfield.value;
        if (text === "") {
            return;
        }

        let msg1 = { name: "User", message: text };
        this.messages.push(msg1);

        fetch('/chat', {
            method: 'POST',
            body: JSON.stringify({ message: text }),
            headers: {
                'Content-Type': 'application/json'
            },
        })
            .then(r => r.json())
            .then(r => {
                let msg2 = { name: "Sam", message: r.answer };
                this.messages.push(msg2);
                this.updateChatText(Chatbox);
            })
            .catch((error) => {
                console.error('Error:', error);
                this.updateChatText(Chatbox);
            });

        textfield.value = '';
    }

    updateChatText(Chatbox) {
        var html = '';
        this.messages.slice().reverse().forEach(function (item) {
            if (item.name === "Sam") {
                html += '<div class="messages__item messages__item--operator">' + item.message + '</div>';
            } else {
                html += '<div class="messages__item messages__item--visitor">' + item.message + '</div>';
            }
        });

        const chatmessage = Chatbox.querySelector('.chatbox__messages');
        chatmessage.innerHTML = html;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const chatbox = new Chatbox();
    chatbox.display();
});
