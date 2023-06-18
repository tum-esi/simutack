<template>
  <div v-if="settings" class="tachometer-settings">
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
        <div :id="sensorName + '-settings-column1'" class="col-6">
          <SettingEntry
            :id="sensorNames + '-update-interval'"
            label="Update Interval [s]:"
            type="number"
            placeholder="Enter the sensor's update interval in seconds."
            tooltip="The interval at which the sensor produces new data."
            :step="0.001"
            :min="0"
            v-model="settings.updateInterval"
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
  name: "TachometerSettings",
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
