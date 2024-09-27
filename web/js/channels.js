const data = new Array(0);
const charts_url = "/getcharts"
const channels_url = "/getchannels"
const get_user_url = "/getuser"

const tabButtons = Array.from(document.getElementsByClassName("tab-button"))
const tabContents = Array.from(document.getElementsByClassName("tab-content"))

tabButtons.forEach((tabButton, index) => {
    tabButton.addEventListener("click", () => {
        selectTab(index)
    })
})

function getUserId(username) {
    return fetch(get_user_url + `?name=${username}`)
    .then(response => response.json())
    .then(data => {
        return data['id'];
    });
}

function checkChannelOwner(channel_name, user_id) {
    console.log(`Final URL ${channels_url + `?name=${channel_name}`}`)
    return fetch(channels_url + `?name=${channel_name}`)
        .then(response => response.json())
        .then(data => {
            console.log(data)
            console.log(`Owner ID: ${data['owner_id']} User ID: ${user_id}`)
            return data['owner_id'] == user_id;
        })
        .catch(error => {
            console.log(error);
        })
}

const selectTab = (index) => {
    if (index < 0 || index >= tabButtons.length) {
        return
    }
    tabContents.forEach((tabContent) => {
        tabContent.style.display = "none"
    });
    tabButtons.forEach((tabButton) => {
        tabButton.classList.remove("active")
    });
    tabContents[index].style.display = "flex"
    tabButtons[index].classList.add("active")
}

selectTab(0)

const getURI = () => {
    let args = decodeURIComponent(window.location.search)
    args = args.replace("?", "")
    args = args.split("&")
    let args_dict = {}
    for (let i = 0; i < args.length; i++) {
        let arg = args[i]
        let arg_parts = arg.split("=")
        args_dict[arg_parts[0]] = arg_parts[1]
    }
    return args_dict
}

const args = getURI()
console.log(args)

function createLineChart(xData, yData, name, context) {
    let data = {
        labels: xData,
        datasets: [{
            label: name,
            data: yData,
            pointStyle: false,
            fill: true,
            borderWidth: 1,
            borderColor: '#234',
            backgroundColor: '#89a',
        }]
    };

    let config = {
        type: 'line',    
        data: data,
        options: {
            elements: {
                point:{
                    radius: 1
                }
            }
        }
    }
    let chart = new Chart(context, config);
}


function fillChart(channels) {
    Object.keys(channels).forEach(function(key) {
        let channel = channels[key]
        let channel_name = channel['name']
        let channel_owner = channel['owner_id']
        console.log(channel)
        let channel_div = document.createElement("div")
        channel_div.setAttribute("class", "channel")
        channel_div.setAttribute("id", channel)
        let channel_h1 = document.createElement("h1")
        channel_h1.setAttribute("class", "channel-name")
        channel_h1.innerText = channel_name + " (" + channel_owner + ")"
        channel_div.appendChild(channel_h1)
        document.getElementById("channels-list").appendChild(channel_div)
        axios.get(charts_url + "?channel_name=" + channel_name).then((response) => {
            console.log('Response: ');
            console.log(response)
            console.log('Response: ' + JSON.stringify(response));
            const data = response.data
            console.log('Data: ' + JSON.stringify(data));
            Object.keys(data).forEach(function(key) {
                let xData = [];
                let yData = [];
                let name = key
                console.log('Key: ' + key + ' Value: ' + data[key]);
                console.log(data[key]);
                for (let i = 0; i < data[key].length; i++) {
                    xData.push(data[key][i][0]);
                    yData.push(data[key][i][1]);
                }
                let chart = document.createElement("div")
                chart.setAttribute("class", "chart")
                chart.setAttribute("id", name + "-chart")
                channel_div.appendChild(chart)
                let chart_name = document.createElement("h1")
                chart_name.setAttribute("class", "chart-name")
                chart_name.innerText = key
                chart.appendChild(chart_name)
                let canvas = document.createElement("canvas")
                canvas.setAttribute("id", name + "-canvas")
                canvas.setAttribute("class", "chart-canvas")
                chart.appendChild(canvas)
                let ctx = document.getElementById(name + "-canvas").getContext("2d");
                console.log(xData)
                console.log(yData)
                createLineChart(xData, yData, name, ctx);
            })
        });
    });
}

function fillChannels() {
    const uri = decodeURIComponent(window.location.search);
    const params = new URLSearchParams(uri);
    let channels = {}
    console.log(`Url: ${channels_url + uri}`);
    console.log(`Params: ${params}`);
    if (params.has("name")) {
        axios.get(channels_url + uri).then((response) => {
            channels[1] = {
                name: response.data.name,
                owner_id: response.data.owner_id
            }
            fillChart(channels);
        });
    } else {
        axios.get(channels_url + uri).then((response) => {
            console.log(response.data)
            channels = response.data
            fillChart(channels);
        });
    }
}

checkChannelOwner('test_channel', 1).then((result) => {
    if (!result) {
        getElementById("api-content").style.display = "none"
    }
})

fillChannels()