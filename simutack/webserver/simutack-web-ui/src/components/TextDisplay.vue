<template>
  <div ref="display" class="text-display p-2">
    <b-form-checkbox v-model="autoscroll" class="my-1">
      Autoscroll
    </b-form-checkbox>
    <b-form-textarea plaintext :value="this.text" max-rows="20" />
  </div>
</template>

<script>
export default {
  name: "TextDisplay",
  props: {
    sensorName: String,
    dataType: String,
  },
  data() {
    return {
      textBuffer: [],
      nextLine: 0,
      maxLines: 1000,
      autoscroll: true,
    };
  },
  computed: {
    text: {
      get: function () {
        return this.textBuffer.join("");
      },
    },
    sensorData() {
      return this.$store.getters.getSensorData(this.sensorName);
    },
  },
  watch: {
    sensorData(data) {
      // Format output message
      let msg = "";
      if (this.dataType === "gnss") {
        msg = this.parseGnss(data);
      } else if (this.dataType === "imu") {
        msg = this.parseImu(data);
      } else if (this.dataType === "tachometer") {
        msg = this.parseTachometer(data);
      }

      // Append message to output buffer
      if (this.nextLine < this.maxLines) {
        // Insert new message at the end
        this.textBuffer.push(msg);
        this.nextLine++;
      } else {
        // Remove first (oldest) message and insert new message at the end
        this.textBuffer.shift();
        this.textBuffer.push(msg);
      }

      // Auto scroll bottom
      if (this.autoscroll) {
        let display = this.$refs.display.getElementsByTagName("textarea")[0];
        display.scrollTop = display.scrollHeight + 500;
      }
    },
  },
  methods: {
    parseGnss(data) {
      let msg = "";
      if (data) {
        msg =
          "Frame " +
          data.info.frame +
          ", t = " +
          data.info.timestamp.toFixed(3) +
          "\tLat: " +
          data.data.latitude.toFixed(3) +
          ", Lon: " +
          data.data.longitude.toFixed(3) +
          ", Alt: " +
          data.data.altitude.toFixed(3) +
          "\n";
      }
      return msg;
    },
    parseTachometer(data) {
      let msg = "";
      if (data) {
        msg =
          "Frame " +
          data.info.frame +
          ", t = " +
          data.info.timestamp.toFixed(3) +
          ":\tSpeed: " +
          data.data.speed.toFixed(1) +
          " m/s\n";
      }
      return msg;
    },
    parseImu(data) {
      let msg = "";
      if (data) {
        msg =
          "Frame " +
          data.info.frame +
          ", t = " +
          data.info.timestamp.toFixed(3) +
          // ":\tLat: " +
          // data.altitude.toFixed(3) +
          "\n";
      }
      return msg;
    },
  },
};
</script>
