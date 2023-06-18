<template>
  <div v-if="settings" class="camera-settings">
    <b-form @submit="onSubmit">
      <b-form-group
        class="align-items-center"
        :id="sensorName + '-enable-sensor-group'"
        label="Sensor Updates:"
        :label-for="sensorName + '-enable-sensor'"
        label-size="sm"
        label-cols="3"
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
            :id="sensorName + '-width'"
            label="Image Width:"
            type="number"
            placeholder="Enter the image width."
            tooltip="The camera image's width."
            :step="1"
            v-model="settings.imageWidth"
          />

          <SettingEntry
            :id="sensorName + '-height'"
            label="Image Height:"
            type="number"
            placeholder="Enter the image height."
            tooltip="The camera image's height."
            :step="1"
            v-model="settings.imageHeight"
          />

          <SettingEntry
            :id="sensorName + '-fov'"
            label="Image FoV (horizontal):"
            type="number"
            placeholder="Enter the image FoV."
            tooltip="The camera image's horizontal field of view."
            :step="1"
            v-model="settings.fov"
          />

          <SettingEntry
            :id="sensorName + '-position-x'"
            label="Camera Position X:"
            type="number"
            placeholder="Enter the camera's position (x-axis)."
            tooltip="The camera's position (x-axis)."
            :step="0.1"
            v-model="settings.position.x"
          />
        </div>
        <div :id="sensorName + '-settings-column2'" class="col">
          <SettingEntry
            :id="sensorName + '-position-y'"
            label="Camera Position Y:"
            type="number"
            placeholder="Enter the camera's position (y-axis)."
            tooltip="The camera's position (y-axis)."
            :step="0.1"
            v-model="settings.position.y"
          />

          <SettingEntry
            :id="sensorName + '-position-z'"
            label="Camera Position Z:"
            type="number"
            placeholder="Enter the camera's position (z-axis)."
            tooltip="The camera's position (z-axis)."
            :step="0.1"
            v-model="settings.position.z"
          />

          <SettingEntry
            :id="sensorName + '-rotation-roll'"
            label="Camera Rotation Roll:"
            type="number"
            placeholder="Enter the camera's rotation (roll-axis)."
            tooltip="The camera's position (roll-axis)."
            :step="0.1"
            v-model="settings.rotation.roll"
          />

          <SettingEntry
            :id="sensorName + '-rotation-pitch'"
            label="Camera Rotation Pitch:"
            type="number"
            placeholder="Enter the camera's rotation (pitch-axis)."
            tooltip="The camera's position (pitch-axis)."
            :step="0.1"
            v-model="settings.rotation.pitch"
          />

          <SettingEntry
            :id="sensorName + '-rotation-yaw'"
            label="Camera Rotation Yaw:"
            type="number"
            placeholder="Enter the camera's rotation (yaw-axis)."
            tooltip="The camera's position (yaw-axis)."
            :step="0.1"
            v-model="settings.rotation.yaw"
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
  name: "CameraSettings",
  components: { SettingEntry },
  props: {
    sensorName: String,
    settings: {
      type: Object,
      default() {
        return {
          enabled: false,
          updateInterval: 1.0,
          imageWidth: 0,
          imageHeight: 0,
          fov: 0.0,
          position: {
            x: 0.0,
            y: 0.0,
            z: 0.0,
          },
          rotation: {
            roll: 0.0,
            pitch: 0.0,
            yaw: 0.0,
          },
        };
      },
    },
    url: String,
  },
  data() {
    return {};
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
