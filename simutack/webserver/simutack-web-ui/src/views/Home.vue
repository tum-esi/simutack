<template>
  <div class="home">
    <b-jumbotron>
      <h1 class="display-2">Welcome to Simutack</h1>
      <h1>A data generation framework for automotive sensors</h1>
    </b-jumbotron>
    <b-container class="text-left">
      <h3>Usage</h3>
      <p>
        Create and manage all sensors in the <strong>Sensors</strong> section.
        You can also change some sensor settings, as well as configure and apply
        individual attacks. Currently, the following sensor types are supported:
      </p>
      <ul>
        <li>Camera</li>
        <li>GNSS</li>
        <li>IMU</li>
        <li>Tachometer</li>
      </ul>
      <p>
        The effect of certain attacks can be directly evaluated with the
        built-in autopilot. Check out the <strong>Autopilot</strong> section to
        play around with the predefined sensors and attacks and see how the
        autopilot is affected.
      </p>
      <p>
        In case you would like to change some basic settings of the application,
        e.g. the frameworks IP address or some simulation parameters, you can do
        so in the <strong>Settings</strong> section.
      </p>
    </b-container>
  </div>
</template>

<script>
// @ is an alias to /src

export default {
  name: "Home",
  components: {},
};
</script>

<style scoped>
p {
  text-align: justify;
}
</style>
