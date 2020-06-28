$(function() {
    // variables
    const socket = create_socket('ws/chat/')

    const messages = $('#all_messages')
    const form = $("#chatform")
    const lastMessageId = $("#last_message_id")
    const loadOldMessages = $("#load_old_messages")

    let username = ""

    // functions

    // update logged in users list
    function init () {
        socket.send(JSON.stringify({command: 'init_chat'}))
    }

    function update_presence(data) {
        add_message(data)
        presence(data.message)
    }

    function presence(data) {
        const user_list = data.members

        document.getElementById("loggedin-users-count").innerText = user_list.length
        let user_list_obj = document.getElementById("user-list")
        user_list_obj.innerText = ""

        for(let i = 0; i < user_list.length; i++ ){
            let user_el = document.createElement('li')
            user_el.setAttribute('class', 'list-group-item')
            user_el.innerText = user_list[i]
            user_list_obj.append(user_el)
        }
    }

    // add_message
    function add_message(data){
        const m = data.message
        let chat = $("#chat")
        let el = $('<li class="list-group-item"></li>')

        el.append('<strong>'+m.message.author+'</strong> : ')

        el.append(m.message.content)

        chat.append(el)
        messages.scrollTop(messages[0].scrollHeight)

        if (m.mention_user === username){
            toastr.info(m.mention_message)
        }
    }

    // load history
    function fetch_messages(data) {
        const new_messages = data.messages
        const last_id = data.previous_id

        if(last_id === -1){
            loadOldMessages.remove()
            lastMessageId.text(last_id)
            if(new_messages.length === 0)
                return
        }
        else
            lastMessageId.text(last_id)

        let chat = $("#chat")

        for(let i=new_messages.length - 1; i>=0; i--){
            let el = $('<li class="list-group-item"></li>')

            el.append('<strong>'+new_messages[i]['user']+'</strong> : ')
            el.append(new_messages[i]['message'])
            chat.prepend(el)
        }
    }


    messages.scrollTop(messages[0].scrollHeight)

    // socket control

    socket.onopen = function connection(ws) {
        init()
    }

    socket.onmessage = function(message) {

        const no_messages = $("#no_messages")

        if(no_messages.length)
            no_messages.remove()


        const data = JSON.parse(message.data)
        // console.log(data)

        if(data.type === "presence"){
            presence(data)
            return
        }

        if(data.message?.type === "add_message"){
            add_message(data)
            return
        }

        if(data.message?.type === "update_presence"){
            update_presence(data)
            return
        }
        if(data.type === "init_chat"){
            console.log(data)
            if (!username)
                username = data.username
        }


        if(data.type === "fetch_messages"){
            fetch_messages(data)
        }
    }


    // button control

    form.on("submit", function(event) {
        const elMessage = $('#message')
        const message = elMessage.val()
        socket.send(JSON.stringify({command: 'add_message', data: message}))
        elMessage.val('').focus()
        return false
    })

    loadOldMessages.on("click", function() {
        let message = {
            last_message_id: lastMessageId.text()
        }

        socket.send(JSON.stringify({command: 'fetch_messages', data: message}))
        return false
    })
})