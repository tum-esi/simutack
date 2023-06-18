import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";

Vue.use(Vuex);


const store = new Vuex.Store({
    state: {
        simutackAddress: "http://"+ location.hostname + ":3000",
        // simutackAddress: "http://10.157.150.3:3000",

        sensors:
            [
                // {
                //     name: "",
                //     type: "",
                // },
            ],
        sensorCount: 0,
        sensorData: {},
    },
    mutations: {
        // synchornous
        addSensor(state, sensor) {
            // Add sensor to list
            if (!state.sensors.some(s => s.name === sensor.name)) {
                state.sensors.push(sensor);
                state.sensorCount++;
            }
        },
        deleteSensor(state, sensor) {
            // Remove sensor from list
            const index = state.sensors.indexOf(sensor);
            if (index > -1) {
                state.sensors.splice(index, 1);
                state.sensorCount--;
            }
        },
        storeSensorData(state, payload) {
            // Only one payload argument can be passed:
            // payload {
            //     sensorName: String,
            //     sensorData: Object,
            // }

            // Store data (Use Vue.set to ensure all components will be notified)
            Vue.set(state.sensorData, payload.sensorName, payload.sensorData)
            // Vue.delete(state.sensorData, payload.sensorName)
        }
    },
    actions: {
        // asynchornous
        async addSensor(context, sensor) {
            // Check if sensor name already exits
            if (context.state.sensors.some(s => s.name === sensor.name)) {
                return;
            }

            // Add sensor to list
            context.commit('addSensor', sensor);

            // Setup the event source for regular data updates (SSE)
            // let url = context.state.hostAddress + "sensor/" + sensor.type + "/" + sensor.name + "/events";
            // let eventSource = new EventSource(url);
            // eventSource.addEventListener(
            //     "message",
            //     (event) => {
            //         // Get JSON object (for SSE MIME-type is text/event-stream)
            //         let data = JSON.parse(event.data);

            //         // Store data
            //         context.commit('storeSensorData', { sensorName: sensor.name, sensorData: data });
            //     },
            //     false
            // );

            // Setup the WebSocket connection for regular data updates
            let url = context.state.simutackAddress + "/sensor/" + sensor.type + "/" + sensor.name + "/websocket";
            url = url.replace("http", "ws"); // Change to websocket protocol
            let socket = new WebSocket(url);

            socket.onopen = function () {
                console.log("WebSocket connection established with " + url);
            };
            socket.onmessage = function (event) {
                // Get JSON object
                let data = JSON.parse(event.data);

                // Store data
                context.commit('storeSensorData', { sensorName: sensor.name, sensorData: data });
            };
        },
        async createSensor(context, sensor) {
            return new Promise((resolve, reject) => {
                // Ensure that we have an array of sensors that can be sent to server even if only one sensor is created
                let sensors = (Array.isArray(sensor) ? sensor : [sensor])

                // Add subscriber
                // sensors.forEach(s => {
                //     s['subscriber'] = context.state.hostAddress +
                //         "sensor/" +
                //         s.type +
                //         "/" +
                //         s.name +
                //         "/stream";
                // });

                // Create sensor via HTTP request
                axios({
                    method: "POST",
                    url: context.state.simutackAddress + "/config",
                    headers: { "content-type": "application/json" },
                    data: { 'newSensors': sensors },
                }).then(
                    (response) => {
                        // Add sensor to list
                        sensors.forEach(s => {
                            context.dispatch("addSensor", s);
                        });
                        resolve(response);
                    },
                    (error) => {
                        reject(error);
                    }
                );
            });
        },
        async deleteSensor(context, sensor) {
            console.log(sensor);

            return new Promise((resolve, reject) => {
                // Create sensor via HTTP request
                axios({
                    method: "DELETE",
                    url: context.state.simutackAddress + "/config",
                    headers: { "content-type": "application/json" },
                    data: sensor,
                }).then(
                    (response) => {
                        // Remove sensor from list
                        context.commit("deleteSensor", sensor);
                        resolve(response);
                    },
                    (error) => {
                        reject(error);
                    }
                );
            });
        },
        async initTrafficSignEcu(context) {
            // Setup the WebSocket connection for regular data updates
            let url = "ws://" + location.hostname + ":4000/traffic-sign/websocket";
            // let url = "ws://10.157.150.3:4000/traffic-sign/websocket";
            let socket = new WebSocket(url);

            socket.onopen = function () {
                console.log("WebSocket connection established with " + url);
            };
            socket.onmessage = function (event) {
                // Get JSON object
                let data = JSON.parse(event.data);

                // Store data
                context.commit('storeSensorData', { sensorName: "traffic-sign-ecu", sensorData: data });
            };
            socket.onerror = function (error) {
                console.log("Error occured: " + error);
            }
            
        }
    },
    getters: {
        getSensorData: (state) => (sensorName) => {
            let data = state.sensorData[sensorName];
            return data ? data : null;
        },
    },
});

export default store;