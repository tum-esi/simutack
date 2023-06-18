<template>
  <div class="navbar">
    <b-navbar toggleable="sm" type="dark" variant="dark" class="w-100">
      <b-navbar-brand href="#">Simutack</b-navbar-brand>

      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

      <b-collapse id="nav-collapse" is-nav>
        <b-navbar-nav>
          <b-nav-item to="/">Home</b-nav-item>
          <b-nav-item to="/sensors">Sensors</b-nav-item>
          <b-nav-item to="/autopilot">Autopilot</b-nav-item>
          <b-nav-item to="/settings">Settings</b-nav-item>
          <b-nav-item to="/about">About</b-nav-item>
        </b-navbar-nav>
      </b-collapse>
    </b-navbar>
  </div>
</template>

<script>
// @ is an alias to /src

export default {
  name: "NavBar",
  components: {},
};
</script>

<style scoped>
</style>
