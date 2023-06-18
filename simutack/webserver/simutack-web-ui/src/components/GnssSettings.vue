<template>
  <div v-if="settings" class="gnss-settings">
    <b-form @submit="onSubmit">
      <b-form-group
        class="align-items-center"
        :id="sensorName + '-enable-sensor-group'"
        label="Sensor Updates:"
        :label-for="sensorName + '-enable-sensor'"
        label-cols="3"
        label-size="sm"
      >
        <b-form-checkbox
          switch
          :id="sensorName + '-enable-sensor'"
          size="lg"
          v-model="settings.enabled"
        ></b-form-checkbox>
      </b-form-group>

      <b-form-row>
        <div :id="sensorName + '-settings-column1'" class="col">
          <SettingEntry
            :id="sensorName + '-update-interval'"
            label="Update Interval [s]:"
            type="number"
            placeholder="Enter the sensor's update interval in seconds."
            tooltip="The interval at which the sensor produces new data."
            :step="0.001"
            :min="0"
            v-model="settings.updateInterval"
          />

          <SettingEntry
            :id="sensorName + '-alt-bias'"
            label="Altitude Noise Bias:"
            type="number"
            placeholder="Enter the bias."
            tooltip="The bias for the altitude parameter in the internal noise model."
            :step="0.001"
            v-model="settings.noiseAltBias"
          />

          <SettingEntry
            :id="sensorName + '-alt-stddev'"
            label="Altitude Noise Std Dev:"
            type="number"
            placeholder="Enter the standard deviation."
            tooltip="The standard deviation for the altitude parameter in the internal noise model."
            :step="0.001"
            v-model="settings.noiseAltStdDev"
          />

          <SettingEntry
            :id="sensorName + '-lat-bias'"
            label="Latitude Noise Bias:"
            type="number"
            placeholder="Enter the bias."
            tooltip="The bias for the latitude parameter in the internal noise model."
            :step="0.001"
            v-model="settings.noiseLatBias"
          />
        </div>
        <div :id="sensorName + '-settings-column2'" class="col">
          <SettingEntry
            :id="sensorName + '-lat-stddev'"
            label="Latitude Noise Std Dev:"
            type="number"
            placeholder="Enter the standard deviation."
            tooltip="The standard deviation for the latitude parameter in the internal noise model."
            :step="0.001"
            v-model="settings.noiseLatStdDev"
          />

          <SettingEntry
            :id="sensorName + '-lon-bias'"
            label="Longitude Noise Bias:"
            type="number"
            placeholder="Enter the bias."
            tooltip="The bias for the longitude parameter in the internal noise model."
            :step="0.001"
            v-model="settings.noiseLonBias"
          />

          <SettingEntry
            :id="sensorName + '-lon-stddev'"
            label="Longitude Noise Std Dev:"
            type="number"
            placeholder="Enter the standard deviation."
            tooltip="The standard deviation for the longitude parameter in the internal noise model."
            :step="0.001"
            v-model="settings.noiseLonStdDev"
          />
        </div>
      </b-form-row>

      <div class="text-center p-4">
        <b-button type="submit" variant="primary" size="sm" class="m-2">Apply</b-button>
      </div>
    </b-form>
  </div>
</template>

<script>
// @ is an alias to /src
import axios from "axios";
import SettingEntry from "@/components/SettingEntry.vue";

export default {
  name: "GnssSettings",
  components: { SettingEntry },
  props: {
    sensorName: String,
    settings: Object,
    url: String,
  },
  data() {
    return {
      // settings: {
      //   enabled: true,
      //   updateInterval: 1.0,
      //   noiseAltBias: 0.0,
      //   noiseAltStdDev: 0.0,
      //   noiseLatBias: 0.0,
      //   noiseLatStdDev: 0.0,
      //   noiseLonBias: 0.0,
      //   noiseLonStdDev: 0.0,
      // },
    };
  },
  methods: {
    onSubmit(event) {
      event.preventDefault();

      axios({
        method: "POST",
        url: this.url,
        data: {
          settings: this.settings,
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

<style scoped>
</style>
