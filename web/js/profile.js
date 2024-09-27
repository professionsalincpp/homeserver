console.log(document.cookie);

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

let auth = JSON.parse(getCookie("auth"))

const username = document.getElementById("username")
const password = document.getElementById("password")
const admin = document.getElementById("admin")

username.innerHTML = "Username: " + auth.username
password.innerHTML = "Password: " + auth.password
admin.innerHTML = "Admin: " + (auth.admin == "1" ? "Yes" : "No")

const users = document.getElementById("users")
const userChannels = document.getElementById("user-channels")

const dbUrl = 'http://192.168.1.13:8080/getusers'
const channelsUrl = 'http://192.168.1.13:8080/getchannels'
const getUserUrl = `http://192.168.1.13:8080/getuser?name=${auth.username}`

function loadChannels() {
    fetch(getUserUrl)
        .then(response => response.json()) // eslint-disable-line
        .then(data => {
            console.log(data)
            user_id = data['id']
            console.log(`User ID: ${user_id}`)
            createElements(user_id)
        })
        .catch(error => {
            console.log(error)
        })
}

function createElements(user_id) {
    fetch(channelsUrl + `?owner_id=${user_id}`)
        .then(response => response.json()) // eslint-disable-line
        .then(data => {
            Object.keys(data).forEach(function(key) {
                const channel = data[key]
                const element = document.createElement("li")
                element.setAttribute("data-channel", channel['name'])
                element.innerHTML = `<a href="/channels?name=${channel['name']}">${channel['name']}</a>`
                userChannels.appendChild(element)
            })
        })
    if (auth['admin'] == "1") { 
        fetch(dbUrl)
            .then(response => response.json()) // eslint-disable-line
            .then(data => {
                console.log(data)
                users.innerHTML = "<tr><th>Username</th><th>Password</th><th>Admin</th></tr>" // Clear table before adding new data
                for (let i = 0; i < data.length; i++) {
                    const user = data[i]
                    const row = document.createElement("tr")
                    const nameCell = document.createElement("td")
                    const passwordCell = document.createElement("td")
                    const adminCell = document.createElement("td");
                    const adminSwitch = document.createElement("label");
                    // adminSwitch.setAttribute("for", "adminSwitch");
                    adminSwitch.setAttribute("class", "switch");
                    // adminSwitch.setAttribute("data-toggle", "toggle");
                    // adminSwitch.setAttribute("data-on", "Yes");
                    // adminSwitch.setAttribute("data-off", "No");
                    adminSwitch.setAttribute("data-size", "small");
                    adminSwitch.setAttribute("data-off-text", "No");
                    adminSwitch.setAttribute("data-on-text", "Yes");

                    const switchInput = document.createElement("input");
                    switchInput.setAttribute("type", "checkbox");
                    switchInput.setAttribute("id", "adminSwitch");
                    if (user['is_admin']) {
                        switchInput.setAttribute("checked", true);
                    }
                    if (user['username'] == auth.username) {
                        switchInput.disabled = true;
                    }

                    const switchLabel = document.createElement("span");
                    switchLabel.setAttribute("class", "slider round");
                    switchInput.addEventListener("change", function() {
                        let usr = {
                            username: user['username'],
                            password: user['password'],
                            admin: switchInput.checked
                        }
                        setAdmin(usr)
                    });

                    adminSwitch.appendChild(switchInput);
                    adminCell.appendChild(adminSwitch);
                    adminSwitch.appendChild(switchLabel)
                    adminCell.appendChild(adminSwitch)
                    nameCell.innerText = user['username']
                    passwordCell.innerText = user['password']
                    row.appendChild(nameCell)
                    row.appendChild(passwordCell)
                    row.appendChild(adminCell)
                    users.appendChild(row)
                }
            })
    } else {
        users.innerHTML = `Access denied. You are not an admin. auth['admin'] = ${auth['admin']}`
    }
}

function setAdmin(user) {
    let url = `/setadmin?username=${user.username}&admin=${user.admin}`
    console.log(url)
    fetch(url)
    .then(response => response.json()) // eslint-disable-line
    .then(data => {
        console.log(data)
    })
    // location.reload() // Refresh page to reflect changes
}


loadChannels()