<template>
  <div ref="display" class="image-display py-2">
    <h6 v-if="showStats">
      {{
        "Frame: " + this.frame + ",\t t = " + this.timestamp.toFixed(3) + "s"
      }}
    </h6>
    <b-img v-bind:src="image" blank-src="null" center fluid-grow />
  </div>
</template>

<script>
export default {
  name: "ImageDisplay",
  props: {
    sensorName: String,
    showStats: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    sensorData() {
      return this.$store.getters.getSensorData(this.sensorName);
    },
    frame() {
      // Check that sensorData actually contains the frame property
      if (
        this.sensorData &&
        Object.prototype.hasOwnProperty.call(this.sensorData.info, "frame")
      )
        return this.sensorData.info.frame;
      else return 0;
    },
    timestamp() {
      // Check that sensorData actually contains the timestamp property
      if (
        this.sensorData &&
        Object.prototype.hasOwnProperty.call(this.sensorData.info, "timestamp")
      )
        return this.sensorData.info.timestamp;
      else return 0.0;
    },
    // Check that sensorData actually contains the image property
    image() {
      if (
        this.sensorData &&
        Object.prototype.hasOwnProperty.call(this.sensorData.data, "image")
      ) {
        return "data:image/jpeg;base64," + this.sensorData.data.image;
      } else return null;
    },
  },
  methods: {
    click() {
      console.log(this.frame);
    },
  },
};
</script>
