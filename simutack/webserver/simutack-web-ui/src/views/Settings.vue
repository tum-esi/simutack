<template>
  <div class="settings">
    <b-container fluid class="text-left">
      <b-form @submit="onSubmit" class="mx-3 col-6">
        <h4>General Settings</h4>
        <SettingEntry
          id="simutack-address"
          label="simutack Address:"
          type="string"
          placeholder="Enter the IP address + port of the simutack framework, e.g. 'http://localhost:8300'."
          tooltip="The IP address + port at which the simutack framework can be reached."
          v-model="simutackAddress"
        />

        <h4>Simulation Settings</h4>
        <SettingEntry
          id="world-step"
          label="World Step [s]:"
          type="number"
          min="0"
          step="0.001"
          placeholder="Enter the world step in s."
          tooltip="The simulated world step in seconds, i.e. the elapsed time between two computed frames."
          v-model="worldStep"
        />

        <div class="text-center p-4">
          <b-button type="submit" variant="primary" class="m-2">Apply</b-button>
        </div>
      </b-form>
    </b-container>
  </div>
</template>

<script>
// @ is an alias to /src
import axios from "axios";
import SettingEntry from "@/components/SettingEntry.vue";

export default {
  name: "Settings",
  components: {
    SettingEntry,
  },
  data() {
    return {
      worldStep: 0.1,
    };
  },
  computed: {
    simutackAddress: {
      get: function () {
        return this.$store.state.simutackAddress;
      },
      set: function (address) {
        this.$store.state.simutackAddress = address;
      },
    },
  },
  mounted() {
    axios({
      method: "GET",
      url: this.simutackAddress + "/config",
      headers: { "content-type": "application/json" },
    }).then(
      (result) => {
        this.worldStep = result.data.simulation.worldStep;
      },
      (error) => {
        console.error(error);
      }
    );
  },
  methods: {
    onSubmit(event) {
      event.preventDefault();

      axios({
        method: "POST",
        url: this.simutackAddress + "/config",
        data: {
          simulation: {
            worldStep: this.worldStep,
          },
        },
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
  },
};
</script>
