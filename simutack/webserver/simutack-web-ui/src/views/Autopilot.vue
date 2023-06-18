<template>
  <div class="autopilot">
    <b-container fluid class="text-left px-5">
      <b-row>
        <div class="col-xl-6">
          <h4>Manual Control</h4>
          <b-form-group
            class="align-items-center"
            id="manual-control-group"
            label="Manual Control:"
            label-for="manual-control"
            label-cols="2"
          >
            <b-form-checkbox
              switch
              id="manual-control"
              size="lg"
              v-model="manualControl"
              @change="manualControlChanged()"
            ></b-form-checkbox>
          </b-form-group>
          <h4>Vehicle Inputs</h4>
          <b-row>
            <b-col cols="2" class="align-self-center">
              <label for="range-throttle">Throttle: </label>
            </b-col>
            <b-col cols="8" class="align-self-center">
              <b-form-input
                id="range-throttle"
                v-model="control.throttle"
                type="range"
                min="0"
                max="1"
                step="0.01"
                number
              ></b-form-input>
            </b-col>
            <b-col cols="2" class="align-self-center">
              <div class="mt-2">{{ control.throttle.toFixed(3) }}</div>
            </b-col>
          </b-row>
          <b-row>
            <b-col cols="2" class="align-self-center">
              <label for="range-brake">Brake: </label>
            </b-col>
            <b-col cols="8" class="align-self-center">
              <b-form-input
                id="range-brake"
                v-model="control.brake"
                type="range"
                min="0"
                max="1"
                step="0.01"
                number
              ></b-form-input>
            </b-col>
            <b-col cols="2" class="align-self-center">
              <div class="mt-2">{{ control.brake.toFixed(3) }}</div>
            </b-col>
          </b-row>
          <b-row>
            <b-col cols="2" class="align-self-center">
              <label for="range-throttle">Steer: </label>
            </b-col>
            <b-col cols="8" class="align-self-center">
              <b-form-input
                id="range-steer"
                v-model="control.steer"
                type="range"
                min="-1"
                max="1"
                step="0.01"
                number
              ></b-form-input>
            </b-col>
            <b-col cols="2" class="align-self-center">
              <div class="mt-2">{{ control.steer.toFixed(3) }}</div>
            </b-col>
          </b-row>

          <!-- PID params -->
          <b-row>
            <b-col cols="2" class="align-self-center">
              <label for="range-p">P: </label>
            </b-col>
            <b-col cols="8" class="align-self-center">
              <b-form-input
                id="range-p"
                v-model="steerControl.Kp"
                type="range"
                step="0.001"
                min="0"
                max="2"
                number
              ></b-form-input>
            </b-col>
            <b-col cols="2" class="align-self-center">
              <div class="mt-2">{{ steerControl.Kp }}</div>
            </b-col>
          </b-row>
          <b-row>
            <b-col cols="2" class="align-self-center">
              <label for="range-i">I: </label>
            </b-col>
            <b-col cols="8" class="align-self-center">
              <b-form-input
                id="range-i"
                v-model="steerControl.Ki"
                type="range"
                step="0.0001"
                min="0"
                max="2"
                number
              ></b-form-input>
            </b-col>
            <b-col cols="2" class="align-self-center">
              <div class="mt-2">{{ steerControl.Ki }}</div>
            </b-col>
          </b-row>
          <b-row>
            <b-col cols="2" class="align-self-center">
              <label for="range-d">D: </label>
            </b-col>
            <b-col cols="8" class="align-self-center">
              <b-form-input
                id="range-d"
                v-model="steerControl.Kd"
                type="range"
                step="0.001"
                min="0"
                max="2"
                number
              ></b-form-input>
            </b-col>
            <b-col cols="2" class="align-self-center">
              <div class="mt-2">{{ steerControl.Kd }}</div>
            </b-col>
          </b-row>

          <!-- Vehicle Dashboard -->
          <b-row class="mt-3">
            <b-col>
              <h4>Position</h4>
              <p>{{ this.position }}</p>
            </b-col>
            <b-col>
              <h4>Orientation</h4>
              <p>{{ this.orientation }}</p>
            </b-col>
            <b-col>
              <h4>Speed</h4>
              <p>{{ this.speed }}</p>
            </b-col>
            <b-col>
              <h4>Speed Limit</h4>
              <b-img height="100" left :src="this.speedLimitImage" />
              <p>{{ this.speedLimit }}</p>
            </b-col>
          </b-row>

          <div class="text-center">
            <b-button @click="resetVehicle()" class="my-1 align-self-center"
              >Reset Vehicle</b-button
            >
          </div>
        </div>
        <div class="col-xl-6">
          <h4>Dash Cam</h4>
          <b-row>
            <b-col>
              <ImageDisplay sensorName="traffic-sign-ecu" :showStats="false" />
              <!-- <ImageDisplay sensorName="autopilot-camera1" :showStats="false" /> -->
            </b-col>
            <b-col>
              <ImageDisplay sensorName="autopilot-camera2" :showStats="false" />
            </b-col>
          </b-row>
        </div>
      </b-row>
      <h4>Sensors</h4>
      <b-row class="px-3 mw-100">
        <b-tabs class="mt-1 w-100" content-class="mt-3">
          <b-tab v-for="s in requiredSensors" :key="s.name" :title="s.name">
            <Sensor
              v-if="$store.state.sensors.includes(s)"
              :name="s.name"
              :type="s.type"
              :autopilotView="true"
            />
          </b-tab>
        </b-tabs>
      </b-row>
    </b-container>
  </div>
</template>

<script>
// @ is an alias to /src
import axios from "axios";
import ImageDisplay from "@/components/ImageDisplay.vue";
import Sensor from "@/components/Sensor.vue";

// Import test track as waypoint list
import vehicleTrackFile from "@/tracks/speed_limit2.json";
// import vehicleTrackFile from "@/tracks/track1.json";
// import vehicleTrackFile from "@/tracks/zickzack.json";

export default {
  name: "Autopilot",
  components: { ImageDisplay, Sensor },
  data() {
    return {
      // Required sensors that will be created automatically if not already existing
      requiredSensors: [
        {
          name: "autopilot-gnss",
          type: "gnss",
        },
        {
          name: "autopilot-imu",
          type: "imu",
        },
        {
          name: "autopilot-tachometer",
          type: "tachometer",
        },
        {
          name: "autopilot-camera1",
          type: "camera",
        },
        {
          name: "autopilot-camera2",
          type: "camera",
        },
      ],
      // Auxilliary variables
      down: false,
      lastChar: null,
      lastSpeedLimit: -1,
      // Configure vehicle control
      manualControl: true,
      autopilotInterval: 20, // 100ms
      autopilotIntervalId: 0,
      // targetSpeed: 15.0, // m/s = 54 km/h
      vehicleTrack: vehicleTrackFile,
      targetWaypointIndex: 0, // Waypoint index in vehicle track
      northVector: [0.0, -1.0, 0.0], // Carla magnetic north vector (reference for IMU); in docs
      maxThrottle: 0.75,
      maxBrake: 1.0,
      maxSteer: 1.0,
      dt: 0.1,
      // Actual vehicle control params
      control: {
        throttle: 0.0,
        brake: 0.0,
        steer: 0.0,
      },
      // PID controller settings
      accelControl: {
        Kp: 0.5, // Proportional gain
        Ki: 0.001, // Integral gain
        Kd: 0.02, // Differential gain
        tau: 1.0, // Derivative low-pass filter time constant
        integrator: 0.0,
        differentiator: 0.0,
        lastError: 0.0,
        lastMeasurement: 0.0,
      },
      steerControl: {
        Kp: 0.012, // Proportional gain
        Ki: 0.0001, // Integral gain
        Kd: 0.001, // Differential gain
        tau: 1.0, // Derivative low-pass filter time constant
        integrator: 0.0,
        differentiator: 0.0,
        lastError: 0.0,
        lastMeasurement: 0.0,
      },
    };
  },
  mounted() {
    // Create required sensors if not already available
    this.$store.dispatch("createSensor", this.requiredSensors).then(
      () => {
        // Apply custom sensor settings when all sensors were successfully created
        // Dash camera
        let settings_cam = {
          enabled: true,
          updateInterval: 0.1,
          imageWidth: 700, //800,
          imageHeight: 300, //600,
          fov: 20.0, //90.0,
          position: {
            x: 1.5,
            y: 0.0,
            z: 1.5,
          },
          rotation: {
            pitch: 0.0,
            yaw: 5.0,
            roll: 0.0,
          }
        };
        let url =
          this.$store.state.simutackAddress + "/sensor/camera/autopilot-camera1";

        axios({
          method: "POST",
          url: url,
          data: {
            settings: settings_cam,
          },
          headers: { "content-type": "application/json" },
        }).then(() => {});

        // Third person camera
        settings_cam = {
          enabled: true,
          updateInterval: 0.1,
          imageWidth: 800,
          imageHeight: 600,
          fov: 90.0,
          position: {
            x: -6.0,
            y: 0.0,
            z: 5.0,
          }
        };
        settings_cam.rotation = {
          roll: 0.0,
          pitch: -35.0,
          yaw: 0.0,
        };
        url =
          this.$store.state.simutackAddress + "/sensor/camera/autopilot-camera2";

        axios({
          method: "POST",
          url: url,
          data: {
            settings: settings_cam,
          },
          headers: { "content-type": "application/json" },
        }).then(() => {});

        // IMU
        let settings_imu = {
          enabled: true,
          updateInterval: 0.1,
        };
        url = this.$store.state.simutackAddress + "/sensor/imu/autopilot-imu";

        axios({
          method: "POST",
          url: url,
          data: {
            settings: settings_imu,
          },
          headers: { "content-type": "application/json" },
        }).then(() => {});

        // GNSS
        let settings_gnss = {
          enabled: true,
          updateInterval: 0.1,
        };
        url = this.$store.state.simutackAddress + "/sensor/gnss/autopilot-gnss";

        axios({
          method: "POST",
          url: url,
          data: {
            settings: settings_gnss,
          },
          headers: { "content-type": "application/json" },
        }).then(() => {});

        // Tachometer
        let settings_tacho = {
          enabled: true,
          updateInterval: 0.1,
        };
        url =
          this.$store.state.simutackAddress +
          "/sensor/tachometer/autopilot-tachometer";

        axios({
          method: "POST",
          url: url,
          data: {
            settings: settings_tacho,
          },
          headers: { "content-type": "application/json" },
        }).then(() => {
          // Enable autopilot
          //   this.manualControl = false;
          this.manualControlChanged();
        });

        // Notify user
        this.$bvToast.toast(
          "The required sensors for the autopilot have been successfully created.",
          {
            title: "Info",
            toaster: "b-toaster-bottom-right",
            variant: "success",
            autoHideDelay: 5000,
          }
        );
      },
      (error) => {
        console.error(error);

        // Notify user about failure
        let message;
        if (error.response == undefined)
          message =
            "The server is not responding. Is the Simutack framework running?";
        else message = "HTTP Error " + error.response.status;
        this.$bvToast.toast(message, {
          title: "Error",
          toaster: "b-toaster-bottom-right",
          variant: "danger",
          autoHideDelay: 5000,
        });
      }
    );

    // Init Traffic Sign ECU
    this.initEcu();
  },
  computed: {
    speed() {
      let tachometerData = this.$store.getters.getSensorData(
        "autopilot-tachometer"
      );
      let speedString = "-";
      if (tachometerData)
        speedString = (tachometerData.data.speed * 3.6).toFixed(1) + " km/h";
        // speedString = tachometerData.data.speed.toFixed(3) + " m/s";
      return speedString;
    },
    targetSpeed() {
      if (this.speedLimit > 0)
        return (this.speedLimit / 3.6); // convert to m/s
      else
        return 12.5; // m/s = 45 km/h
    },
    speedLimit() {
      let speedLimit = "";
      let speedLimitData = this.$store.getters.getSensorData(
        "traffic-sign-ecu"
      );
      if (speedLimitData) {
        speedLimit = speedLimitData.data.sign;
      }
      if (speedLimit != "" && speedLimit != "None") {
        // eslint-disable-next-line vue/no-side-effects-in-computed-properties
        this.lastSpeedLimit = parseInt(speedLimit);
      }
      return this.lastSpeedLimit;
    },
    speedLimitImage() {
      if (this.speedLimit == 30) return require("@/assets/speed_limit_30.svg");
      else if (this.speedLimit == 50)
        return require("@/assets/speed_limit_50.svg");
      else if (this.speedLimit == 60)
        return require("@/assets/speed_limit_60.svg");
      else if (this.speedLimit == 70)
        return require("@/assets/speed_limit_70.svg");
      else if (this.speedLimit == 80)
        return require("@/assets/speed_limit_80.svg");
      else if (this.speedLimit == 90)
        return require("@/assets/speed_limit_90.svg");
      else return null;
    },
    position() {
      let gnssData = this.$store.getters.getSensorData("autopilot-gnss");
      let positionString = "Lat: -, Lon: -, Alt: -";
      if (gnssData) {
        positionString =
          "Lat: " +
          gnssData.data.latitude.toFixed(6) +
          " °\nLon: " +
          gnssData.data.longitude.toFixed(6) +
          " °\nAlt: " +
          gnssData.data.altitude.toFixed(2) +
          " m";
      }
      return positionString;
    },
    orientation() {
      let imuData = this.$store.getters.getSensorData("autopilot-imu");
      let orientationString = "-";
      if (imuData)
        orientationString = imuData.data.orientation.toFixed(3) + " °";
      return orientationString;
    },
  },
  methods: {
    initEcu() {
      console.log("Init ECU...");

      this.$store.dispatch("initTrafficSignEcu").then(
        () => {
          // Notify user
          this.$bvToast.toast(
            "The Traffic Sign ECU was successfully connected.",
            {
              title: "Info",
              toaster: "b-toaster-bottom-right",
              variant: "success",
              autoHideDelay: 5000,
            }
          );
        },
        (error) => {
          console.error(error);

          // Notify user about failure
          let message;
          if (error.response == undefined)
            message =
              "The server is not responding. Is the Traffic Sign ECU running?";
          else message = "HTTP Error " + error.response.status;
          this.$bvToast.toast(message, {
            title: "Error",
            toaster: "b-toaster-bottom-right",
            variant: "danger",
            autoHideDelay: 5000,
          });
        }
      );
    },

    manualControlChanged() {
      console.log(
        "Manual Control switched " + (this.manualControl ? "on" : "off")
      );
      if (this.manualControl) {
        window.addEventListener("keydown", this.keyDown);
        window.addEventListener("keyup", this.keyUp);
        if (this.autopilotIntervalId) clearInterval(this.autopilotIntervalId);
        this.control.throttle = 0.0;
        this.control.brake = 1.0;
        this.control.steer = 0.0;
      } else {
        window.removeEventListener("keydown", this.keyDown);
        window.removeEventListener("keyup", this.keyUp);
        this.autopilotIntervalId = setInterval(
          this.autopilotControl,
          this.autopilotInterval
        );
      }
    },

    keyDown(e) {
      // Get input char
      let cmd = String.fromCharCode(e.keyCode).toLowerCase();

      // (Prevent multiple sending from repeated keydown event)
      if (this.down && this.lastChar === cmd) return;
      this.down = true;
      this.lastChar = cmd;

      // Compute control based on input
      if (cmd === "w") this.control.throttle = 1.0;
      else if (cmd === "a") this.control.steer = -1.0;
      else if (cmd === "s") this.control.brake = 1.0;
      else if (cmd === "d") this.control.steer = 1.0;

      // Send to car
      this.applyControl();
    },
    keyUp(e) {
      // Prevent repeated keydown event
      this.down = false;

      // Get input char
      let cmd = String.fromCharCode(e.keyCode).toLowerCase();

      // Compute control based on input
      if (cmd === "w") this.control.throttle = 0.0;
      else if (cmd === "a") this.control.steer = 0.0;
      else if (cmd === "s") this.control.brake = 0.0;
      else if (cmd === "d") this.control.steer = 0.0;

      // Send to car
      this.applyControl();
    },
    applyControl() {
      axios({
        method: "POST",
        url: this.$store.state.simutackAddress + "/control",
        data: this.control,
        headers: { "content-type": "application/json" },
      }).then(
        (/*result*/) => {
          //   this.response = result.data;
          //   console.log(this.response);
        },
        (error) => {
          console.error(error);
        }
      );
    },
    autopilotControl() {
      // based on Carla local_planner.py example
      // Get sensor input
      let currentSpeed = this.$store.state.sensorData["autopilot-tachometer"]
        .data.speed; // m/s
      let currentLocation = this.$store.state.sensorData["autopilot-gnss"].data; // geo location (lat/lon/alt)
      let currentHeading = this.$store.state.sensorData["autopilot-imu"].data
        .orientation; // degree [0, 360]

      // Get next targets
      let targetSpeed = this.targetSpeed;
      let targetWaypoint = this.vehicleTrack[this.targetWaypointIndex];
      // let targetWaypoint = { altitude: 0.0, longitude: 0.0013470978970933827, latitude: 0.0009193043707966808 };
      // let targetWaypoint = { altitude: 0.0, longitude: 0.0013650978970933827, latitude: -0.1009193043707966808 };

      // console.log(
      //   "Current: " +
      //     currentSpeed +
      //     " m/s, Target: " +
      //     this.targetSpeed +
      //     " m/s"
      // );
      // console.log(
      //   "Current: " + currentLocation + ", Target: " + this.targetLocation
      // );
      let locationVector = [
        /*x*/ currentLocation.longitude *
          60 *
          1852, // convert geo position (degree) to m; 60 angular minutes, 1852m <-> 1 nautic mile
        /*y*/ -currentLocation.latitude * 60 * 1852, // convert geo position (degree) to m; 60 angular minutes, 1852m <-> 1 nautic mile, *-1 because north directs towards -y
        /*z*/ 0.0,
      ];

      // console.log(
      //   "" + locationVector[0] + ", " + locationVector[1] + ", " + locationVector[2] + ", " + currentSpeed + ", " + this.targetSpeed
      // );
      console.log(
        "" + locationVector[0] + ", " + locationVector[1] + ", " + locationVector[2] + ", " + currentHeading);
      

      // Compute new system input
      let acceleration = this.computeAcceleration(currentSpeed, targetSpeed);
      let steering = this.computeSteering(
        currentLocation,
        currentHeading,
        targetWaypoint
      );

      //   console.log(
      //     "Computed Acceleration: " + acceleration + ", Steering: " + steering
      //   );

      // Steering regulation: changes cannot happen abruptly, can't steer too much.
      if (steering > this.control.steer + 0.15)
        steering = this.control.steer + 0.15;
      else if (steering < this.control.steer - 0.15)
        steering = this.control.steer - 0.15;

      // Apply steering
      if (steering >= 0) this.control.steer = Math.min(this.maxSteer, steering);
      else this.control.steer = Math.max(-this.maxSteer, steering);

      // Apply throttle and brake
      if (acceleration >= 0.0) {
        this.control.throttle = Math.min(acceleration, this.maxThrottle);
        this.control.brake = 0.0;

        // Slow down when steering
        if (Math.abs(steering) > 0.05) {
          this.control.throttle = 0.2 * this.control.throttle;
        }
      } else {
        this.control.throttle = 0.0;
        this.control.brake = Math.min(Math.abs(acceleration), this.maxBrake);
      }

      //   console.log(
      //     "Throttle: " +
      //       this.control.throttle +
      //       ", Brake: " +
      //       this.control.brake +
      //       ", Steer: " +
      //       this.control.steer
      //   );

      // Apply control
      this.applyControl();
    },
    computeAcceleration(currentSpeed, targetSpeed) {
      // PID controller to estimate throttle/brake input
      let error = targetSpeed - currentSpeed;
      let measurement = currentSpeed;

      // Proportional term
      let p = this.accelControl.Kp * error;

      // Integral term
      let i =
        this.accelControl.integrator +
        0.5 *
          this.accelControl.Ki *
          this.dt *
          (this.accelControl.lastError + error);

      // Derivative term
      let d =
        (2.0 *
          this.accelControl.Kd *
          (measurement - this.accelControl.lastMeasurement) +
          (2.0 * this.accelControl.tau - this.dt) *
            this.accelControl.differentiator) /
        (2.0 * this.accelControl.tau + this.dt);

      //   console.log("P: " + p + ", I: " + i + ", D: " + d);

      // Compute actual PID controller output (clamp value to limits)
      let pid = Math.min(Math.max(p + i + d, -1.0), 1.0);

      // Update state variables
      this.accelControl.integrator = i;
      this.accelControl.differentiator = d;
      this.accelControl.lastError = error;
      this.accelControl.lastMeasurement = measurement;

      return pid;
    },
    dotProduct(v1, v2) {
      let result = 0;
      for (let i = 0; i < 3; i++) {
        result += v1[i] * v2[i];
      }
      return result;
    },
    vectorNorm(v) {
      return Math.sqrt(this.dotProduct(v, v));
    },
    crossProduct(v1, v2) {
      return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
      ];
    },
    computeSteering(currentLocation, currentHeading, targetLocation) {
      // PID controller to estimate steering input

      //   console.log(
      //     "Current Location: lat = " +
      //       currentLocation.latitude +
      //       ", lon = " +
      //       currentLocation.longitude +
      //       ", alt = " +
      //       currentLocation.altitude +
      //       ", Current Heading: " +
      //       currentHeading +
      //       ", Target Location: lat = " +
      //       targetLocation.latitude +
      //       ", lon = " +
      //       targetLocation.longitude +
      //       ", alt = " +
      //       targetLocation.altitude
      //   );

      // Get vehicle-target vector
      let targetVector = [
        /*x*/ (targetLocation.longitude - currentLocation.longitude) *
          60 *
          1852, // convert geo position (degree) to m; 60 angular minutes, 1852m <-> 1 nautic mile
        /*y*/ -(targetLocation.latitude - currentLocation.latitude) * 60 * 1852, // convert geo position (degree) to m; 60 angular minutes, 1852m <-> 1 nautic mile, *-1 because north directs towards -y
        /*z*/ 0.0,
      ];

      //   console.log(
      //     "Target Vector: x = " +
      //       targetVector[0] +
      //       ", y = " +
      //       targetVector[1] +
      //       ", z = " +
      //       targetVector[2]
      //   );

      // Get angle between target vector and magnetic north (magnetic direction towards target waypoint)
      let targetHeading = Math.acos(
        Math.min(
          Math.max(
            this.dotProduct(targetVector, this.northVector) /
              (this.vectorNorm(targetVector) *
                this.vectorNorm(this.northVector)),
            -1.0
          ),
          1.0
        )
      );
      targetHeading = (targetHeading / Math.PI) * 180.0; // Convert rad to deg

      // console.log("Target Heading: " + targetHeading);

      // Check for turning direction (error will be always positive between 0 .. 180 degree from upper formula)
      if (this.crossProduct(this.northVector, targetVector)[2] < 0.0) {
        targetHeading = 360.0 - targetHeading;
      }

      //   console.log("Target Heading: " + targetHeading);

      // Get difference in magnetic orientations (error)
      let error = targetHeading - currentHeading;
      if (error > 180.0) {
        error = error - 360;
      } else if (error < -180.0) {
        error = error + 360;
      }
      let measurement = currentHeading;

      //   console.log("Error: " + error);

      // Proportional term
      let p = this.steerControl.Kp * error;

      // Integral term
      let i =
        this.steerControl.integrator +
        0.5 *
          this.steerControl.Ki *
          this.dt *
          (this.steerControl.lastError + error);

      // Derivative term
      let d =
        (2.0 *
          this.steerControl.Kd *
          (measurement - this.steerControl.lastMeasurement) +
          (2.0 * this.steerControl.tau - this.dt) *
            this.steerControl.differentiator) /
        (2.0 * this.steerControl.tau + this.dt);

      //   console.log("P: " + p + ", I: " + i + ", D: " + d);

      // Compute actual PID controller output (clamp value to limits)
      let pid = Math.min(Math.max(p + i + d, -1.0), 1.0);

      // Update state variables
      this.steerControl.integrator = i;
      this.steerControl.differentiator = d;
      this.steerControl.lastError = error;
      this.steerControl.lastMeasurement = measurement;

      // Update waypoints
      if (this.vectorNorm(targetVector) < 4.0) this.targetWaypointIndex++;
      //   if (this.vectorNorm(targetVector) < 0.5) this.targetWaypointIndex++;
      if (this.targetWaypointIndex >= this.vehicleTrack.length)
        this.targetWaypointIndex = 0;

      return pid;
    },
    resetVehicle() {
      // Reset control input
      this.targetWaypointIndex = 0;
      this.control.throttle = 0.0;
      this.control.brake = 1.0;
      this.control.steer = 0.0;

      // Reset saved speed limit
      this.lastSpeedLimit = -1;

      // Reset PID variables
      this.accelControl.integrator = 0.0;
      this.accelControl.differentiator = 0.0;
      this.accelControl.lastError = 0.0;
      this.accelControl.lastMeasurement = 0.0;

      this.steerControl.integrator = 0.0;
      this.steerControl.differentiator = 0.0;
      this.steerControl.lastError = 0.0;
      this.steerControl.lastMeasurement = 0.0;

      // Reset vehicle at server
      let vehicleLocation = {
        // m
        x: this.vehicleTrack[0].longitude * 60 * 1852,
        y: this.vehicleTrack[0].latitude * -1 * 60 * 1852 + 0.5,
        z: this.vehicleTrack[0].altitude,
      };
      let vehicleRotation = {
        // degree
        pitch: 0,
        yaw: 0,
        roll: 0,
      };

      axios({
        method: "POST",
        url: this.$store.state.simutackAddress + "/config",
        headers: { "content-type": "application/json" },
        data: {
          simulation: {
            reset: true,
            vehicleLocation: vehicleLocation,
            vehicleRotation: vehicleRotation,
          },
        },
      }).then(
        () => {
          console.log("Simulation was reset!");
        },
        (error) => {
          console.log(error);
        }
      );
    },

    // debugOutput() {
    //   // Get sensor input
    //   let currentLocation = this.$store.state.sensorData["autopilot-gnss"]; // geo location (lat/lon/alt)
    //   let currentHeading = this.$store.state.sensorData["autopilot-imu"]
    //     .orientation; // degree [0, 360]
    //   let targetLocation = this.vehicleTrack[this.targetWaypointIndex];

    //   console.log(
    //     "Current Location: lat = " +
    //       currentLocation.latitude +
    //       ", lon = " +
    //       currentLocation.longitude +
    //       ", alt = " +
    //       currentLocation.altitude +
    //       ", Target Location: lat = " +
    //       targetLocation.latitude +
    //       ", lon = " +
    //       targetLocation.longitude +
    //       ", alt = " +
    //       targetLocation.altitude
    //   );

    //   // Get vehicle-target vector
    //   let targetVector = [
    //     /*x*/ (targetLocation.longitude - currentLocation.longitude) *
    //       60 *
    //       1852, // convert geo position (degree) to m; 60 angular minutes, 1852m <-> 1 nautic mile
    //     /*y*/ -(targetLocation.latitude - currentLocation.latitude) * 60 * 1852, // convert geo position (degree) to m; 60 angular minutes, 1852m <-> 1 nautic mile
    //     /*z*/ 0.0,
    //   ];

    //   let currentVector = [
    //     /*x*/ currentLocation.longitude * 60 * 1852, // convert geo position (degree) to m; 60 angular minutes, 1852m <-> 1 nautic mile
    //     /*y*/ -currentLocation.latitude * 60 * 1852, // convert geo position (degree) to m; 60 angular minutes, 1852m <-> 1 nautic mile
    //     /*z*/ 0.0,
    //   ];
    //   console.log(
    //     "Current Vector: x = " +
    //       currentVector[0] +
    //       ", y = " +
    //       currentVector[1] +
    //       ", z = " +
    //       currentVector[2]
    //   );

    //   console.log(
    //     "Target Vector: x = " +
    //       targetVector[0] +
    //       ", y = " +
    //       targetVector[1] +
    //       ", z = " +
    //       targetVector[2]
    //   );

    //   // Get angle between target vector and magnetic north (magnetic direction towards target waypoint)
    //   let targetHeading = Math.acos(
    //     Math.min(
    //       Math.max(
    //         this.dotProduct(targetVector, this.northVector) /
    //           (this.vectorNorm(targetVector) *
    //             this.vectorNorm(this.northVector)),
    //         -1.0
    //       ),
    //       1.0
    //     )
    //   );
    //   targetHeading = (targetHeading / Math.PI) * 180.0; // Convert rad to deg

    //   //   console.log("Target Heading: " + targetHeading);

    //   // Check for turning direction (error will be always positive between 0 .. 180 degree from upper formula)
    //   if (this.crossProduct(this.northVector, targetVector)[2] < 0.0) {
    //     targetHeading = 360.0 - targetHeading;
    //   }

    //   console.log(
    //     "Current Heading: " +
    //       currentHeading +
    //       ", Target Heading: " +
    //       targetHeading
    //   );

    //   // Get difference in magnetic orientations (error)
    //   let error = targetHeading - currentHeading;
    //   if (error > 180.0) {
    //     error = error - 360;
    //   } else if (error < -180.0) {
    //     error = error + 360;
    //   }

    //   console.log("Error: " + error);

    //   // Update waypoints
    //   //   if (this.vectorNorm(targetVector) < 5.0) this.targetWaypointIndex++;
    //   if (this.vectorNorm(targetVector) < 0.5) this.targetWaypointIndex++;
    //   if (this.targetWaypointIndex >= this.vehicleTrack.length)
    //     this.targetWaypointIndex = 0;

    //   console.log("Index: " + this.targetWaypointIndex);
    // },
  },
};
</script>

<style scoped>
p {
  white-space: pre-line;
}
</style>
