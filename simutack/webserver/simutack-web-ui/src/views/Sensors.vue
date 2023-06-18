<template>
  <div class="sensors">
    <!-- Sensor Tab View -->
    <b-card no-body class="mb-4">
      <b-tabs pills vertical card v-model="tabIndex">
        <!-- Render Tabs, supply a unique `key` to each tab -->
        <b-tab v-for="s in sensors" :key="s.name" :title="s.name">
          <Sensor :name="s.name" :type="s.type" @delete="deleteSensor"></Sensor>
        </b-tab>

        <!-- New Sensor Button (Using tabs-end slot) -->
        <template #tabs-end>
          <b-nav-item
            role="presentation"
            @click.prevent="showNewSensorDialog"
            href="#"
            ><b>New Sensor</b></b-nav-item
          >
        </template>

        <!-- Render this if no tabs -->
        <template #empty>
          <div class="text-center text-muted">
            There are no sensors available.<br />
            Create a new sensor using the <b>New Sensor</b> button.
          </div>
        </template>
      </b-tabs>
    </b-card>

    <!-- New Sensor Dialog -->
    <b-modal
      title="New Sensor"
      v-model="showDialog"
      centered
      @show="resetDialog"
      @hidden="resetDialog"
      @ok="createSensor"
    >
      <form ref="form" @submit.stop.prevent="handleSubmit">
        <b-form-group
          label="Name"
          label-for="name-input"
          invalid-feedback="Unique name is required"
          :state="validName"
        >
          <b-form-input
            id="name-input"
            type="text"
            v-model="sensorName"
            v-on:keypress="validateChar($event)"
            :state="validName"
            required
          ></b-form-input>
        </b-form-group>
        <b-form-group label="Type" label-for="type-input">
          <b-form-select
            id="type-input"
            v-model="sensorType"
            :options="sensorTypes"
          ></b-form-select>
        </b-form-group>
      </form>
    </b-modal>

    <!-- Utility components -->
    <b-overlay :show="showLoading" rounded="sm" no-wrap fixed z-index="2000" />
  </div>
</template>

<script>
// @ is an alias to /src
import axios from "axios";
import Sensor from "@/components/Sensor.vue";

export default {
  name: "Sensors",
  components: {
    Sensor,
  },
  data() {
    return {
      showDialog: false,
      showLoading: false,
      tabIndex: 0,
      validName: null,
      sensorName: "",
      sensorType: null,
      sensorTypes: ["camera", "gnss", "imu", "tachometer"],
    };
  },
  computed: {
    sensors() {
      return this.$store.state.sensors;
    },
    sensorCount() {
      return this.$store.state.sensorCount;
    },
    simutackAddress() {
      return this.$store.state.simutackAddress;
    },
  },
  mounted() {
    // Show loading animation while waiting for server response
    this.showLoading = true;

    // Load list of available sensors
    axios({
      method: "GET",
      url: this.simutackAddress + "/config",
      headers: { "content-type": "application/json" },
    }).then(
      (result) => {
        result.data.sensors.forEach((s) => {
          // Add sensor to list
          let sensor = {
            name: s.name,
            type: s.type,
          };
          this.$store.dispatch("addSensor", sensor);
        });

        // Hide loading animation
        this.showLoading = false;

        // Notify user
        let msg = "";
        if (result.data.sensors.length == 0)
          msg = "There are currently no sensors available.";
        else if (result.data.sensors.length == 1)
          msg = "1 Sensor has been successfully loaded.";
        else
          msg = result.data.sensors.length + " sensors have been successfully loaded.";

        this.$bvToast.toast(msg, {
          title: "Done",
          toaster: "b-toaster-bottom-right",
          variant: "success",
          autoHideDelay: 5000,
        });
      },
      (error) => {
        console.error(error);

        // Hide loading animation
        this.showLoading = false;

        // Notify user about failure
        this.$bvToast.toast(
          "Couldn't load any sensor! The server is not responding",
          {
            title: "Error",
            toaster: "b-toaster-bottom-right",
            variant: "danger",
            autoHideDelay: 5000,
          }
        );
      }
    );
  },
  methods: {
    // closeTab(x) {
    //   for (let i = 0; i < this.tabs.length; i++) {
    //     if (this.tabs[i] === x) {
    //       this.tabs.splice(i, 1);
    //     }
    //   }
    // },
    resetDialog() {
      this.sensorName = "";
      this.sensorType = this.sensorTypes[0];
      this.validName = null;
    },
    validateChar(e) {
      let char = String.fromCharCode(e.keyCode); // Get the character
      // Validate with regex (Allow only alphanumeric characters)
      if (/^[A-Za-z0-9-_]+$/.test(char)) return true;
      else e.preventDefault(); // If not match, don't add to input text
    },
    createSensor(modalEvent) {
      // Prevent modal from closing
      modalEvent.preventDefault();

      // Check for validity
      const valid = this.$refs.form.checkValidity();
      this.validName = valid;
      if (!valid) return;

      // Show loading animation while waiting for server response
      this.showLoading = true;

      // Create sensor
      let sensor = {
        name: this.sensorName,
        type: this.sensorType,
      };

      this.$store.dispatch("createSensor", sensor).then(
        () => {
          // Hide loading animation
          this.showLoading = false;

          // Close the dialog manually
          this.$nextTick(() => {
            this.showDialog = false;
          });

          // Change to new sensor tab
          this.tabIndex = this.$store.state.sensorCount - 1;

          // Notify user
          this.$bvToast.toast("The sensor has been successfully created.", {
            title: "Info",
            toaster: "b-toaster-bottom-right",
            variant: "success",
            autoHideDelay: 5000,
          });
        },
        (error) => {
          console.error(error);

          // Hide loading animation
          this.showLoading = false;

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
    },
    deleteSensor() {
      // Show loading animation
      this.showLoading = true;

      // Get selected sensor
      let sensor = this.$store.state.sensors[this.tabIndex];

      // Invoke deletion process
      this.$store.dispatch("deleteSensor", sensor).then(
        () => {
          // Hide loading animation
          this.showLoading = false;

          // Notify user
          this.$bvToast.toast("The sensor has been successfully deleted.", {
            title: "Info",
            toaster: "b-toaster-bottom-right",
            variant: "success",
            autoHideDelay: 5000,
          });
        },
        (error) => {
          console.error(error);

          // Hide loading animation
          this.showLoading = false;

          // Notify user about failure
          let message;
          if (error.response == undefined)
            message =
              "Could not delete the sensor due to an error, please try again!";
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
    showNewSensorDialog() {
      this.resetDialog();
      this.showDialog = true;
    },
  },
};
</script>

<style scoped>
.sensors {
  margin: 0rem 2rem;
}
</style>
