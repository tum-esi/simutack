<template>
  <div v-if="settings" class="imu-settings">
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
            :id="sensorName + '-accel-stddev-x'"
            label="Acceleration (X-Axis) Noise Std Dev:"
            type="number"
            placeholder="Enter the stdandard deviation."
            tooltip="The standard deviation for the acceleration (x-axis) in the internal noise model."
            :step="0.001"
            v-model="settings.noiseAccelStdDevX"
          />

          <SettingEntry
            :id="sensorName + '-accel-stddev-y'"
            label="Acceleration (Y-Axis) Noise Std Dev:"
            type="number"
            placeholder="Enter the stdandard deviation."
            tooltip="The standard deviation for the acceleration (y-axis) in the internal noise model."
            :step="0.001"
            v-model="settings.noiseAccelStdDevY"
          />

          <SettingEntry
            :id="sensorName + '-accel-stddev-z'"
            label="Acceleration (Z-Axis) Noise Std Dev:"
            type="number"
            placeholder="Enter the stdandard deviation."
            tooltip="The standard deviation for the acceleration (z-axis) in the internal noise model."
            :step="0.001"
            v-model="settings.noiseAccelStdDevZ"
          />

          <SettingEntry
            :id="sensorName + '-gyro-stddev-x'"
            label="Gyroscope (X-Axis) Noise Std Dev:"
            type="number"
            placeholder="Enter the stdandard deviation."
            tooltip="The standard deviation for the gyroscope (x-axis) in the internal noise model."
            :step="0.001"
            v-model="settings.noiseGyroStdDevX"
          />
        </div>
        <div :id="sensorName + '-settings-column2'" class="col">
          <SettingEntry
            :id="sensorName + '-gyro-stddev-y'"
            label="Gyroscope (Y-Axis) Noise Std Dev:"
            type="number"
            placeholder="Enter the stdandard deviation."
            tooltip="The standard deviation for the gyroscope (y-axis) in the internal noise model."
            :step="0.001"
            v-model="settings.noiseGyroStdDevY"
          />

          <SettingEntry
            :id="sensorName + '-gyro-stddev-z'"
            label="Gyroscope (Z-Axis) Noise Std Dev:"
            type="number"
            placeholder="Enter the stdandard deviation."
            tooltip="The standard deviation for the gyroscope (z-axis) in the internal noise model."
            :step="0.001"
            v-model="settings.noiseGyroStdDevZ"
          />

          <SettingEntry
            :id="sensorName + '-gyro-bias-x'"
            label="Gyroscope (X-Axis) Bias:"
            type="number"
            placeholder="Enter the bias."
            tooltip="The bias for the gyroscope (x-axis) in the internal noise model."
            :step="0.001"
            v-model="settings.noiseGyroBiasX"
          />

          <SettingEntry
            :id="sensorName + '-gyro-bias-y'"
            label="Gyroscope (Y-Axis) Bias:"
            type="number"
            placeholder="Enter the bias."
            tooltip="The bias for the gyroscope (y-axis) in the internal noise model."
            :step="0.001"
            v-model="settings.noiseGyroBiasY"
          />

          <SettingEntry
            :id="sensorName + '-gyro-bias-z'"
            label="Gyroscope (Z-Axis) Bias:"
            type="number"
            placeholder="Enter the bias."
            tooltip="The bias for the gyroscope (z-axis) in the internal noise model."
            :step="0.001"
            v-model="settings.noiseGyroBiasZ"
          />
        </div>
      </b-form-row>

      <div class="text-center p-4">
        <b-button type="submit" variant="primary" size="sm" class="m-2"
          >Apply</b-button
        >
      </div>
    </b-form>
  </div>
</template>

<script>
// @ is an alias to /src
import axios from "axios";
import SettingEntry from "@/components/SettingEntry.vue";

export default {
  name: "ImuSettings",
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
      //   noiseAccelStdDevX: 0.0,
      //   noiseAccelStdDevY: 0.0,
      //   noiseAccelStdDevZ: 0.0,
      //   noiseGyroStdDevX: 0.0,
      //   noiseGyroStdDevY: 0.0,
      //   noiseGyroStdDevZ: 0.0,
      //   noiseGyroBiasX: 0.0,
      //   noiseGyroBiasY: 0.0,
      //   noiseGyroBiasZ: 0.0,
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
