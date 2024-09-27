const data = new Array(0);
const charts_url = "/getcharts"
const channels_url = "/getchannels"

let lastUpdate = Date.now();

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

function fillChart() {
    const now = Date.now();
    let xData = [];
    let yData = [];
    axios.get(channels_url).then((response) => {
        console.log(response.data)
        let channels = response.data
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
                let chart = document.createElement("div")
                chart.setAttribute("class", "chart")
                chart.setAttribute("id", channel_name + "-chart")
                channel_div.appendChild(chart)
                let chart_name = document.createElement("h1")
                chart_name.setAttribute("class", "chart-name")
                chart_name.innerText = channel_name
                chart.appendChild(chart_name)
                let canvas = document.createElement("canvas")
                canvas.setAttribute("id", channel_name + "-canvas")
                canvas.setAttribute("class", "chart-canvas")
                chart.appendChild(canvas)
                let ctx = document.getElementById(channel_name + "-canvas").getContext("2d");
                console.log('Response: ' + JSON.stringify(response));
                const data = response.data
                console.log('Data: ' + JSON.stringify(data));
                Object.keys(data).forEach(function(key) {
                    let name = key
                    console.log('Key: ' + key + ' Value: ' + data[key]);
                    console.log(data[key]);
                    for (let i = 0; i < data[key].length; i++) {
                        xData.push(data[key][i][0]);
                        yData.push(data[key][i][1]);
                    }
                    console.log(xData)
                    console.log(yData)
                    createLineChart(xData, yData, name, ctx);
                })
            });
        })
    });
}

fillChart();